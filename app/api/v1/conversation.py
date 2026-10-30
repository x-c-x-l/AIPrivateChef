"""
对话管理 API
包括：摘要、分支、搜索
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from app.utils.JWTUtil import JWTUtil
from app.utils.ResponseData import ResponseData
from app.utils.MysqlConnect import MysqlConnect
from app.agents.conversation_manager import conversation_manager
from datetime import datetime
from app.common.logger import logger

router = APIRouter(dependencies=[Depends(JWTUtil.verify_access_token)])


# ==================== 请求模型 ====================

class CreateBranchRequest(BaseModel):
    thread_id: str
    message_id: int
    branch_name: Optional[str] = None


class SaveSummaryRequest(BaseModel):
    thread_id: str
    summary: str
    key_points: Optional[str] = None


class SearchRequest(BaseModel):
    keyword: str
    thread_id: Optional[str] = None
    page: int = 1
    page_size: int = 20


class SavePreferences(BaseModel):
    dietary_restrictions: Optional[str] = None
    favorite_cuisines: Optional[str] = None
    cooking_skill: Optional[str] = None
    summary_enabled: Optional[bool] = None
    summary_threshold: Optional[int] = None


# ==================== 对话摘要接口 ====================

@router.get("/conversation/summary")
def get_summary(thread_id: str, current_user: dict = Depends(JWTUtil.verify_access_token)):
    """获取对话摘要"""
    try:
        user_id = int(current_user.get("sub"))
        summary = conversation_manager.get_conversation_summary(thread_id, user_id)
        return ResponseData(data=summary)
    except Exception as e:
        logger.error(f"获取摘要失败: {e}")
        return ResponseData(message="获取摘要失败", code="500")


@router.post("/conversation/summary")
def save_summary(request: SaveSummaryRequest, current_user: dict = Depends(JWTUtil.verify_access_token)):
    """保存对话摘要"""
    try:
        user_id = int(current_user.get("sub"))
        success = conversation_manager.save_conversation_summary(
            request.thread_id,
            user_id,
            request.summary,
            request.key_points
        )
        if success:
            return ResponseData(message="摘要保存成功")
        else:
            return ResponseData(message="摘要保存失败", code="500")
    except Exception as e:
        logger.error(f"保存摘要失败: {e}")
        return ResponseData(message="保存摘要失败", code="500")


@router.get("/conversation/context")
def get_context(thread_id: str, max_messages: int = Query(default=10, le=50),
                current_user: dict = Depends(JWTUtil.verify_access_token)):
    """获取上下文消息（带摘要优化）"""
    try:
        user_id = int(current_user.get("sub"))
        context = conversation_manager.get_context_messages(thread_id, user_id, max_messages)
        return ResponseData(data=context)
    except Exception as e:
        logger.error(f"获取上下文失败: {e}")
        return ResponseData(message="获取上下文失败", code="500")


# ==================== 对话分支接口 ====================

@router.post("/conversation/branch")
def create_branch(request: CreateBranchRequest, current_user: dict = Depends(JWTUtil.verify_access_token)):
    """创建对话分支"""
    try:
        user_id = int(current_user.get("sub"))
        new_thread_id = conversation_manager.create_branch(
            request.thread_id,
            user_id,
            request.message_id,
            request.branch_name
        )
        if new_thread_id:
            return ResponseData(data={"thread_id": new_thread_id})
        else:
            return ResponseData(message="创建分支失败", code="500")
    except Exception as e:
        logger.error(f"创建分支失败: {e}")
        return ResponseData(message="创建分支失败", code="500")


@router.get("/conversation/branches")
def get_branches(thread_id: str, current_user: dict = Depends(JWTUtil.verify_access_token)):
    """获取会话的所有分支"""
    try:
        user_id = int(current_user.get("sub"))
        branches = conversation_manager.get_branches(thread_id, user_id)
        return ResponseData(data=branches)
    except Exception as e:
        logger.error(f"获取分支列表失败: {e}")
        return ResponseData(message="获取分支列表失败", code="500")


# ==================== 消息搜索接口 ====================

@router.post("/conversation/search")
def search_messages(request: SearchRequest, current_user: dict = Depends(JWTUtil.verify_access_token)):
    """搜索历史消息"""
    try:
        user_id = int(current_user.get("sub"))
        results = conversation_manager.search_messages(
            user_id,
            request.keyword,
            request.thread_id,
            request.page,
            request.page_size
        )
        return ResponseData(data=results)
    except Exception as e:
        logger.error(f"搜索消息失败: {e}")
        return ResponseData(message="搜索失败", code="500")


# ==================== 用户偏好接口 ====================

@router.get("/conversation/preferences")
def get_preferences(current_user: dict = Depends(JWTUtil.verify_access_token)):
    """获取用户偏好"""
    try:
        user_id = int(current_user.get("sub"))
        db = MysqlConnect()
        sql = "SELECT * FROM user_preferences WHERE user_id = %s"
        preferences = db.query_one(sql, (user_id,))
        db.close()
        return ResponseData(data=preferences)
    except Exception as e:
        logger.error(f"获取用户偏好失败: {e}")
        return ResponseData(message="获取偏好失败", code="500")


@router.post("/conversation/preferences")
def save_preferences(request: SavePreferences, current_user: dict = Depends(JWTUtil.verify_access_token)):
    """保存用户偏好"""
    try:
        user_id = int(current_user.get("sub"))
        db = MysqlConnect()

        # 检查是否已存在
        check_sql = "SELECT id FROM user_preferences WHERE user_id = %s"
        existing = db.query_one(check_sql, (user_id,))

        if existing:
            # 更新
            updates = []
            params = []
            if request.dietary_restrictions is not None:
                updates.append("dietary_restrictions = %s")
                params.append(request.dietary_restrictions)
            if request.favorite_cuisines is not None:
                updates.append("favorite_cuisines = %s")
                params.append(request.favorite_cuisines)
            if request.cooking_skill is not None:
                updates.append("cooking_skill = %s")
                params.append(request.cooking_skill)
            if request.summary_enabled is not None:
                updates.append("summary_enabled = %s")
                params.append(1 if request.summary_enabled else 0)
            if request.summary_threshold is not None:
                updates.append("summary_threshold = %s")
                params.append(request.summary_threshold)

            if updates:
                sql = f"UPDATE user_preferences SET {', '.join(updates)} WHERE user_id = %s"
                params.append(user_id)
                db.execute(sql, tuple(params))
        else:
            # 插入
            sql = """
                INSERT INTO user_preferences (user_id, dietary_restrictions, favorite_cuisines,
                    cooking_skill, summary_enabled, summary_threshold)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            db.execute(sql, (
                user_id,
                request.dietary_restrictions,
                request.favorite_cuisines,
                request.cooking_skill or 'beginner',
                1 if request.summary_enabled is None else (1 if request.summary_enabled else 0),
                request.summary_threshold or 20
            ))

        db.close()
        return ResponseData(message="偏好保存成功")
    except Exception as e:
        logger.error(f"保存用户偏好失败: {e}")
        return ResponseData(message="保存偏好失败", code="500")
