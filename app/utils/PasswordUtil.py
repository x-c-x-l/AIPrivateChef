import bcrypt
from typing import Optional
from app.configs.dbconfig import dbconfig  # 假设你的配置里有 BCRYPT_ROUNDS

class PasswordUtil:
    """
    bcrypt 密码加密与验证工具类
    """
    # 默认成本因子，可从配置读取，若未配置则使用 12
    DEFAULT_ROUNDS = getattr(dbconfig, 'BCRYPT_ROUNDS', 12)

    @classmethod
    def hash_password(cls, plain_password: str, rounds: Optional[int] = None) -> str:
        """
        加密明文密码，返回哈希字符串（可直接存储到数据库）
        :param plain_password: 明文密码（字符串）
        :param rounds: 成本因子，不传则使用默认值
        :return: 哈希字符串（如 "$2b$12$..."）
        """
        if not plain_password:
            raise ValueError("密码不能为空")

        # 转为 bytes
        password_bytes = plain_password.encode('utf-8')
        # 生成盐值
        salt = bcrypt.gensalt(rounds=rounds if rounds is not None else cls.DEFAULT_ROUNDS)
        # 计算哈希
        hashed_bytes = bcrypt.hashpw(password_bytes, salt)
        # 返回字符串便于存储
        return hashed_bytes.decode('utf-8')

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        验证明文密码是否与哈希匹配
        :param plain_password: 用户输入的明文密码
        :param hashed_password: 数据库中存储的哈希字符串
        :return: True 表示匹配，False 表示不匹配
        """
        if not plain_password or not hashed_password:
            return False

        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except ValueError:
            # 如果哈希格式无效，返回 False
            return False
