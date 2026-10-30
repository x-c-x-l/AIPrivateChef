from fastapi import APIRouter
from app.models.login.login import LoginRequset, RegisterRequset
from app.utils.MysqlConnect import MysqlConnect
from app.utils.JWTUtil import JWTUtil
from app.utils.PasswordUtil import PasswordUtil
from datetime import datetime
from app.utils.ResponseData import ResponseData

router = APIRouter()


@router.post("/login")
async def login(request: LoginRequset):
    print("request::::", request)
    try:
        db = MysqlConnect()
        sql = "select * from users where username = %s"
        user = db.query_one(sql, (request.username,))
        if not user:
            return {"message": "登录失败，用户名不存在"}
        print(user["password"], request.password)
        if PasswordUtil.verify_password(request.password, user["password"]):
            token = JWTUtil.create_access_token(data={"sub": str(user["id"])})
            data = {
                "token": token,
                "id": user["id"],
                "username": user["username"],
            }
            return ResponseData(data=data)
        else:
            return {"message": "登录失败，账号密码错误"}
    except Exception as e:
        print(f"错误提示：{e}")
        return ResponseData(message="登录失败！",code="500")
    finally:
        # 如果 db 是每次请求创建的，记得关闭连接（如果是全局单例则不需要）
        db.close()


@router.post("/register")
def register(requset: RegisterRequset):
    try:
        if (not requset.username or not requset.password or not requset.name):
            return {
                "message": "信息填写不完整！"
            }
        db = MysqlConnect()
        sql = "insert into users (username, password,name,email,phone,status,created_at) values (%s, %s,%s, %s,%s, %s, %s)"
        password = PasswordUtil.hash_password(requset.password)
        data = db.execute(sql, (requset.username, password, requset.name, requset.email, requset.phone, 1,
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        # 如果 db 是每次请求创建的，记得关闭连接（如果是全局单例则不需要）
        db.close()
        return ResponseData(data=data)
    except Exception as e:
        print(f"错误提示：{e}")
        return ResponseData(message="注册失败！",code="500")
