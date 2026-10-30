import pymysql
from dbutils.pooled_db import PooledDB
from app.configs.dbconfig import dbconfig


# 数接口连接
class MysqlConnect:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        try:
            pool = PooledDB(
                creator=pymysql,  # 使用 PyMySQL 作为数据库驱动[reference:25]
                maxconnections=20,  # 连接池允许的最大连接数[reference:26]
                mincached=2,  # 初始化时池中至少保持的空闲连接数[reference:27]
                maxcached=5,  # 池中最多允许的空闲连接数[reference:28]
                blocking=True,  # 连接数达到上限时，是否阻塞等待[reference:29]
                host=dbconfig.get("host"),
                port=dbconfig.get("port"),
                user=dbconfig.get("user"),
                password=dbconfig.get("password"),
                database=dbconfig.get("database"),
                charset=dbconfig.get("charset"),
            )
            # 每次获取一个连接
            self.conn = pool.connection()
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            # 执行查询
            self.cursor.execute("SELECT VERSION()")
            version = self.cursor.fetchone()
            print(f"MySQL版本: {version[0]}")

        except Exception as e:
            print(f"数接口连接失败：{e}")

    # ---------- 查询（Read） ----------
    def query_one(self, sql, params=None):
        """查询单条记录"""
        try:
            self.cursor.execute(sql, params)
            return self.cursor.fetchone()
        except Exception as e:
            print(f"查询失败：{e}")
            return None

    def query_all(self, sql, params=None):
        """查询多条记录"""
        try:
            self.cursor.execute(sql, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"查询失败：{e}")
            return None

    # ---------- 增删改（Create / Update / Delete） ----------
    def execute(self, sql, params=None):
        """
            执行插入、更新、删除操作
            返回：受影响的行数
        """
        try:
            affected_rows = self.cursor.execute(sql, params)
            self.conn.commit()  # 提交事务
            return affected_rows
        except Exception as e:
            self.conn.rollback()  # 出错回滚
            print(f"SQL执行失败：{e}")
            raise  # 重新抛出异常，让上层感知

    # ---------- 批量操作（常用于批量插入） ----------
    def execute_many(self, sql, params=None):
        """
       批量执行（如批量插入）
       params_list: 参数列表，如 [(1,'a'), (2,'b')]
       """
        try:
            affected_rows = self.cursor.execute(sql, params)
            self.conn.commit()
            return affected_rows
        except Exception as e:
            self.conn.rollback()  # 出错回滚
            print(f"SQL执行失败：{e}")
            raise  # 重新抛出异常，让上层感知

    def close(self):
        """手动关闭游标和连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
