"""
对话管理器 - 提供多轮对话优化功能
包括：上下文摘要、对话分支、消息搜索
"""

from typing import List, Dict, Optional
from datetime import datetime
from app.utils.MysqlConnect import MysqlConnect
from app.common.logger import logger


class ConversationManager:
    """对话管理器"""

    def __init__(self):
        self.db = MysqlConnect()

    def close(self):
        """关闭数据库连接"""
        if self.db:
            self.db.close()

    # ==================== 对话摘要功能 ====================

    def get_conversation_summary(self, thread_id: str, user_id: int) -> Optional[Dict]:
        """获取对话摘要"""
        try:
            sql = """
                SELECT * FROM conversation_summaries
                WHERE thread_id = %s AND user_id = %s
                ORDER BY created_at DESC LIMIT 1
            """
            return self.db.query_one(sql, (thread_id, user_id))
        except Exception as e:
            logger.error(f"获取对话摘要失败: {e}")
            return None

    def save_conversation_summary(self, thread_id: str, user_id: int, summary: str, key_points: str = None):
        """保存对话摘要"""
        try:
            sql = """
                INSERT INTO conversation_summaries (thread_id, user_id, summary, key_points, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.db.execute(sql, (
                thread_id,
                user_id,
                summary,
                key_points,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            return True
        except Exception as e:
            logger.error(f"保存对话摘要失败: {e}")
            return False

    def get_messages_for_summary(self, thread_id: str, user_id: int, limit: int = 20) -> List[Dict]:
        """获取需要摘要的消息"""
        try:
            sql = """
                SELECT role, content, created_at FROM agent_message
                WHERE thread_id = %s AND user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """
            messages = self.db.query_all(sql, (thread_id, user_id, limit))
            return list(reversed(messages)) if messages else []
        except Exception as e:
            logger.error(f"获取消息失败: {e}")
            return []

    # ==================== 对话分支功能 ====================

    def create_branch(self, thread_id: str, user_id: int, message_id: int, branch_name: str = None) -> Optional[str]:
        """从指定消息创建对话分支"""
        try:
            import uuid
            new_thread_id = str(uuid.uuid4())

            # 获取原会话信息
            original_sql = "SELECT * FROM agent_record WHERE id = %s AND user_id = %s"
            original = self.db.query_one(original_sql, (thread_id, user_id))

            if not original:
                return None

            # 创建新会话记录
            name = branch_name or f"{original['name']}_分支"
            insert_sql = """
                INSERT INTO agent_record (id, user_id, name, content, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            self.db.execute(insert_sql, (
                new_thread_id,
                user_id,
                name,
                original['content'],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            # 复制指定消息之前的所有消息
            copy_sql = """
                INSERT INTO agent_message (thread_id, user_id, role, content, image_url, message_type, status, created_at)
                SELECT %s, user_id, role, content, image_url, message_type, status, created_at
                FROM agent_message
                WHERE thread_id = %s AND user_id = %s AND id <= %s
                ORDER BY created_at
            """
            self.db.execute(copy_sql, (new_thread_id, thread_id, user_id, message_id))

            # 创建分支记录
            branch_sql = """
                INSERT INTO conversation_branches (thread_id, parent_thread_id, branch_message_id, user_id, branch_name, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.db.execute(branch_sql, (
                new_thread_id,
                thread_id,
                message_id,
                user_id,
                name,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            return new_thread_id
        except Exception as e:
            logger.error(f"创建对话分支失败: {e}")
            return None

    def get_branches(self, thread_id: str, user_id: int) -> List[Dict]:
        """获取会话的所有分支"""
        try:
            sql = """
                SELECT * FROM conversation_branches
                WHERE parent_thread_id = %s AND user_id = %s
                ORDER BY created_at DESC
            """
            return self.db.query_all(sql, (thread_id, user_id)) or []
        except Exception as e:
            logger.error(f"获取分支列表失败: {e}")
            return []

    # ==================== 消息搜索功能 ====================

    def search_messages(self, user_id: int, keyword: str, thread_id: str = None, page: int = 1, page_size: int = 20) -> Dict:
        """搜索历史消息"""
        try:
            # 构建查询条件
            conditions = ["user_id = %s", "content LIKE %s"]
            params = [user_id, f"%{keyword}%"]

            if thread_id:
                conditions.append("thread_id = %s")
                params.append(thread_id)

            where_clause = " AND ".join(conditions)

            # 查询总数
            count_sql = f"SELECT COUNT(*) as total FROM agent_message WHERE {where_clause}"
            count_result = self.db.query_one(count_sql, tuple(params))
            total = count_result["total"] if count_result else 0

            # 分页查询
            offset = (page - 1) * page_size
            query_sql = f"""
                SELECT id, thread_id, role, content, created_at
                FROM agent_message
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([page_size, offset])
            data = self.db.query_all(query_sql, tuple(params))

            return {
                "list": data or [],
                "total": total,
                "page": page,
                "pageSize": page_size
            }
        except Exception as e:
            logger.error(f"搜索消息失败: {e}")
            return {"list": [], "total": 0, "page": page, "pageSize": page_size}

    def get_context_messages(self, thread_id: str, user_id: int, max_messages: int = 10) -> List[Dict]:
        """获取上下文消息（带摘要优化）"""
        try:
            # 先检查是否有摘要
            summary = self.get_conversation_summary(thread_id, user_id)

            if summary:
                # 有摘要，只返回摘要后的消息
                sql = """
                    SELECT role, content, created_at FROM agent_message
                    WHERE thread_id = %s AND user_id = %s AND created_at > %s
                    ORDER BY created_at
                    LIMIT %s
                """
                messages = self.db.query_all(sql, (
                    thread_id,
                    user_id,
                    summary['created_at'],
                    max_messages
                ))
                return {
                    "has_summary": True,
                    "summary": summary['summary'],
                    "key_points": summary.get('key_points'),
                    "messages": messages or []
                }
            else:
                # 无摘要，返回最近的消息
                sql = """
                    SELECT role, content, created_at FROM agent_message
                    WHERE thread_id = %s AND user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """
                messages = self.db.query_all(sql, (thread_id, user_id, max_messages))
                return {
                    "has_summary": False,
                    "summary": None,
                    "key_points": None,
                    "messages": list(reversed(messages)) if messages else []
                }
        except Exception as e:
            logger.error(f"获取上下文消息失败: {e}")
            return {
                "has_summary": False,
                "summary": None,
                "key_points": None,
                "messages": []
            }


# 全局实例
conversation_manager = ConversationManager()
