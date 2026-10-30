from app.api.router import app, register_routes

# 挂载路由
register_routes()

# 启动命令：python -m app.main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=True)
