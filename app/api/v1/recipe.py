from fastapi import APIRouter, Depends
from app.utils.JWTUtil import JWTUtil
from app.utils.ResponseData import ResponseData
from app.utils.MysqlConnect import MysqlConnect
from pydantic import BaseModel

router = APIRouter(dependencies=[Depends(JWTUtil.verify_access_token)])


class FavoriteRequest(BaseModel):
    thread_id: str
    message_id: int


# 新增收藏
@router.post("/recipe/favorite")
def favorite_create(request: FavoriteRequest, current_user: dict = Depends(JWTUtil.verify_access_token)):
    try:
        user_id = int(current_user.get("sub"))
        message_id = request.message_id
        db = MysqlConnect()
        # 检查是否已收藏
        sql = "select id from recipe_favorites where user_id=%s and thread_id=%s and message_id=%s"
        favorite = db.query_one(sql, (user_id, request.thread_id, message_id))
        if favorite:
            return ResponseData(message="该条内容已收藏!", code=500)
        sql = "select content, role from agent_message where user_id=%s and thread_id=%s and id=%s"
        message = db.query_one(sql, (user_id, request.thread_id, message_id))
        if not message:
            return ResponseData(message="没有找到该消息内容!", code=500)
        if message["role"] == "user":
            return ResponseData(message="这条消息内容不可被收藏!", code=500)

        # 插入收藏
        sql = "insert into recipe_favorites(user_id, thread_id, message_id, recipe_content) values (%s, %s, %s, %s)"
        data = db.execute(sql, (user_id, request.thread_id, message_id, message["content"]))
        db.close()
        return ResponseData(data=data)
    except Exception as e:
        print(f"favorite_create error: {e}")
        return ResponseData(message="收藏失败", code=500)


# 获取收藏列表
@router.get("/recipe/favorites")
def getList(page: str = 1, pageSize: str = 10, current_user: dict = Depends(JWTUtil.verify_access_token)):
    try:
        user_id = int(current_user.get("sub"))
        db = MysqlConnect()
        sql = "select count(*)  as total from recipe_favorites where user_id=%s"
        total_result = db.query_one(sql, (user_id,))
        total = total_result["total"] if total_result else 0
        sql = "select * from recipe_favorites where user_id=%s order by id desc limit %s offset %s"
        offset = (int(page) - 1) * int(pageSize)
        data = db.query_all(sql, (user_id, int(pageSize), offset))
        db.close()
        return ResponseData(data={
            "list": data,
            "total": total,
            "pageSize": int(pageSize),
            "page": int(page)
        })
    except Exception as e:
        print(e)
        return ResponseData(message="查询失败", code=500)


# 获取收藏详情
@router.get("/recipe/favorite/{id}")
def getInfo(id: str, current_user: dict = Depends(JWTUtil.verify_access_token)):
    try:
        user_id = int(current_user.get("sub"))
        db = MysqlConnect()
        sql = "select * from recipe_favorites where user_id = %s and id = %s"
        data = db.query_one(sql, (user_id, int(id)))
        db.close()
        return ResponseData(data=data)
    except Exception as e:
        print(e)
        return ResponseData(message="查询失败", code=500)


# 取消收藏
@router.delete("/recipe/favorite/{id}")
def delFavorite(id: str, current_user: dict = Depends(JWTUtil.verify_access_token)):
    try:
        user_id = int(current_user.get("sub"))
        db = MysqlConnect()
        sql = "delete from recipe_favorites where user_id=%s and id=%s"
        data = db.execute(sql, (user_id, int(id)))
        db.close()
        return ResponseData(data=data)
    except Exception as e:
        print(e)
        return ResponseData(message="取消收藏失败", code=500)


# 获取用户统计信息
@router.get("/recipe/stats")
def get_stats(current_user: dict = Depends(JWTUtil.verify_access_token)):
    try:
        user_id = int(current_user.get("sub"))
        db = MysqlConnect()

        # 总收藏数
        total_sql = "SELECT COUNT(*) as total FROM recipe_favorites WHERE user_id = %s"
        total_result = db.query_one(total_sql, (user_id,))
        total_favorites = total_result["total"] if total_result else 0

        # 总对话数
        chat_sql = "SELECT COUNT(*) as total FROM agent_record WHERE user_id = %s"
        chat_result = db.query_one(chat_sql, (user_id,))
        total_chats = chat_result["total"] if chat_result else 0

        db.close()

        return ResponseData(data={
            "total_favorites": total_favorites,
            "total_chats": total_chats
        })
    except Exception as e:
        print(f"get_stats error: {e}")
        return ResponseData(message="获取统计信息失败", code=500)
