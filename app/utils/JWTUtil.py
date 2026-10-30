import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class JWTUtil:
    """
    JWT 生成与验证工具类
    """
    # 从配置中读取，这里硬编码仅作示例，生产环境务必使用环境变量或配置文件
    SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    ALGORITHM = "HS256"  # 加密算法
    ACCESS_TOKEN_EXPIRE_MINUTES = 180  # 访问令牌过期时间（分钟）

    @classmethod
    def create_access_token(cls, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        生成访问令牌 (Access Token)
        :param data: 要编码到令牌中的数据，例如 {"sub": "user_id"}
        :param expires_delta: 自定义过期时间，若不传则使用默认值
        :return: 生成的 JWT 字符串
        """
        to_encode = data.copy()
        # 设置过期时间

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)

        # 将过期时间作为标准声明 'exp' 加入 payload
        to_encode.update({"exp": expire})

        # 生成JWT
        encode_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encode_jwt

    @staticmethod
    async def verify_access_token(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    ) -> Dict[str, Any]:
        """
        验证并解析令牌（从 Authorization: Bearer <token> 头提取 token）
        失败时抛出 HTTPException，触发全局 http_exception_handler
        """
        token = credentials.credentials
        try:
            payload = jwt.decode(token, JWTUtil.SECRET_KEY, algorithms=[JWTUtil.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            print("Token 已过期")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError as e:
            print(f"无效的 Token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的 Token",
                headers={"WWW-Authenticate": "Bearer"},
            )
