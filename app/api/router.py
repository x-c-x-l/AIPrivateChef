from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from app.api.v1 import chat,oss,recipe,conversation
from app.api.public import login
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Personal Chief API",
    description="私厨",
    version="0.1.0"
)

# 1. 配置跨域资源共享 (CORS)
# 插件开发中，由于请求来自浏览器扩展环境，必须正确配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议指定插件的 ID 或具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")

def register_routes():
    """挂载所有路由"""
    app.include_router(chat.router, prefix="/api/v1", tags=["对话"])
    app.include_router(oss.router, prefix="/api/v1", tags=["申请上传签名url"])
    app.include_router(login.router, prefix="/api/public", tags=["登录相关"])
    app.include_router(recipe.router, prefix="/api/v1", tags=["收藏"])
    app.include_router(conversation.router, prefix="/api/v1", tags=["对话管理"])

    # 前端静态资源 + SPA fallback
    @app.get("/{path:path}", include_in_schema=False)
    async def serve_frontend(path: str):
        if path.startswith("api/"):
            return JSONResponse({"error": "Not Found"}, status_code=404)
        # 返回静态文件
        file_path = os.path.join(static_dir, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # SPA fallback → index.html
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "你的独家私厨上线了~", "status": "ok"}


# ---------- 全局异常处理器 ----------
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    print("request::::",request)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )