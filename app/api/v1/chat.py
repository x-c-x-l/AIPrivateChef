from fastapi import APIRouter, Depends
from app.models.schemas import ChatRequest
from fastapi.responses import StreamingResponse
from app.agents.personal_chief import get_messages, search_recipes, clear_messages
from app.utils.JWTUtil import JWTUtil
from app.utils.ResponseData import ResponseData
from app.utils.Utils import Utils
from app.utils.MysqlConnect import MysqlConnect
from datetime import datetime

router = APIRouter(dependencies=[Depends(JWTUtil.verify_access_token)])


@router.post("/chat/create")
def chat_create(current_user: dict = Depends(JWTUtil.verify_access_token)):
    try:
        user_id = int(current_user.get("sub"))
        uuid = Utils.getUUId()
        db = MysqlConnect()
        user = db.query_one("SELECT * FROM users WHERE id = %s", (user_id,))
        sql = "insert into agent_record(id,user_id,name,content,created_at) values (%s,%s,%s,%s,%s)"
        db.execute(sql, (uuid, user_id, user["name"], "问答", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        db.close()
        return ResponseData(data=uuid)
    except Exception as e:
        print(f"chat_create error: {e}")
        return ResponseData(message="创建失败！", code="500")


@router.get("/chat/list")
def chat_list(page=1, pageSize=10, current_user: dict = Depends(JWTUtil.verify_access_token)):
    try:
        user_id = int(current_user.get("sub"))
        db = MysqlConnect()
        # 查询总数
        count_sql = "select count(*) as total from agent_record where user_id = %s"
        count_result = db.query_one(count_sql, (user_id,))
        total = count_result["total"] if count_result else 0
        # 分页查询
        sql = "select * from agent_record where user_id = %s order by created_at desc LIMIT %s OFFSET %s"
        offset = (int(page) - 1) * int(pageSize)
        data = db.query_all(sql, (user_id, int(pageSize), offset))
        db.close()
        return ResponseData(data={"list": data, "total": total, "page": page, "pageSize": pageSize})
    except Exception as e:
        print(f"chat_list error: {e}")
        return ResponseData(message="查询失败！", code="500")


@router.post("/chat/stream")
async def chat_endpoint(request: ChatRequest, current_user: dict = Depends(JWTUtil.verify_access_token)):
    try:
        print("request::", request)
        user_id = int(current_user.get("sub"))
        db = MysqlConnect()
        sql = "select * from agent_record where user_id = %s and id = %s"
        data = db.query_one(sql, (user_id, request.thread_id))
        print("data::::", data)
        if data and data.get("content") == "问答":
            user = db.query_one("SELECT * FROM users WHERE id = %s", (user_id,))
            sql = "update agent_record set content = %s , name = %s where user_id = %s and id = %s"
            db.execute(sql, (request.message, user["name"], user_id, request.thread_id))

        # 先保存用户消息
        sql = "insert into agent_message(thread_id,user_id,role,content,image_url,message_type,status,created_at) values (%s,%s,%s,%s,%s,%s,%s,%s)"
        message_type = "image" if request.image_url else "text"
        db.execute(
            sql,
            (
                request.thread_id,
                user_id,
                "user",
                request.message,
                request.image_url,
                message_type,
                "1",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )
        sql = "select * from user_preferences where user_id = %s"
        preferences = db.query_one(sql, (user_id,))
        db.close()

        async def stream_and_save():
            full_answer = ""
            try:
                async for chunk in search_recipes(preferences, request.message, request.image_url, request.thread_id):
                    if chunk:
                        full_answer += chunk
                        yield chunk
            finally:
                if full_answer.strip():
                    db = MysqlConnect()
                    try:
                        sql = "insert into agent_message(thread_id,user_id,role,content,image_url,message_type,status,created_at) values (%s,%s,%s,%s,%s,%s,%s,%s)"
                        db.execute(
                            sql,
                            (
                                request.thread_id,
                                user_id,
                                "assistant",
                                full_answer,
                                None,
                                "text",
                                "1",
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            )
                        )
                    finally:
                        db.close()

        return StreamingResponse(
            stream_and_save(),
            media_type="text/event-stream",
        )
    except Exception as e:
        print(f"chat_list error: {e}")
        return ResponseData(message="查询失败！", code="500")


@router.get("/chat/messages")
async def get_chat_messages(thread_id: str, page: str = '1', pageSize: str = '10',
                            current_user: dict = Depends(JWTUtil.verify_access_token)):
    try:
        """"获取历史消息"""
        user_id = int(current_user.get("sub"))
        db = MysqlConnect()
        # 查询总数
        count_sql = "select count(*) as total from agent_message where thread_id = %s and user_id = %s"
        count_result = db.query_one(count_sql, (thread_id, user_id))
        total = count_result["total"] if count_result else 0
        # 分页查询
        offset = (int(page) - 1) * int(pageSize)
        sql = "select * from agent_message where thread_id = %s and user_id = %s order by created_at LIMIT %s OFFSET %s"
        data = db.query_all(sql, (thread_id, user_id, int(pageSize), offset))

        # 查询收藏状态
        if data and len(data) > 0:
            message_ids = [str(item['id']) for item in data]
            placeholders = ','.join(['%s'] * len(message_ids))
            favorite_sql = f"SELECT message_id FROM recipe_favorites WHERE user_id = %s AND thread_id = %s AND message_id IN ({placeholders})"
            favorite_params = [user_id, thread_id] + message_ids
            favorites = db.query_all(favorite_sql, tuple(favorite_params))
            favorite_set = set(str(f['message_id']) for f in (favorites or []))

            # 给每条消息添加收藏状态
            for item in data:
                item['is_favorite'] = str(item['id']) in favorite_set
        else:
            data = []

        db.close()
        return ResponseData(data={"list": data, "total": total, "page": page, "pageSize": pageSize})
    except Exception as e:
        print(f"get_chat_messages error: {e}")
        return ResponseData(message="查询失败！", code="500")


@router.delete("/chat/messages")
async def clear_chat_messages(thread_id: str, current_user: dict = Depends(JWTUtil.verify_access_token)):
    try:
        """清空历史消息"""
        user_id = int(current_user.get("sub"))
        clear_messages(thread_id)
        db = MysqlConnect()
        db.execute("DELETE FROM agent_record WHERE id = %s AND user_id = %s", (thread_id, user_id))
        db.close()
        return ResponseData()
    except Exception as e:
        return ResponseData(message="操作失败！", code="500")
