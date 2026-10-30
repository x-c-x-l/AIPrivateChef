import alibabacloud_oss_v2 as oss
from fastapi import APIRouter, Query, Response, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import timedelta
import os
import httpx
import uuid
import io
# 加载环境变量
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# 从环境变量中加载凭证信息，用于身份验证
credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()

# 加载SDK的默认配置，并设置凭证提供者
cfg = oss.config.load_default()
cfg.credentials_provider = credentials_provider

# 方式一：只填写Region（推荐）
# 必须指定Region ID，SDK会根据Region自动构造HTTPS访问域名
cfg.region = 'cn-beijing'

# 使用配置好的信息创建OSS客户端
client = oss.Client(cfg)

# OSS 域名配置
OSS_ENDPOINT = os.getenv("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")
OSS_BUCKET = os.getenv("OSS_BUCKET")


@router.get("/oss/presign")
def chat_endpoint(filename: str):
    # 根据文件扩展名判断 Content-Type
    content_type_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    ext = filename.split(".")[-1].lower() if "." in filename else "jpg"
    content_type = content_type_map.get(ext, "application/octet-stream")

    pre_result = client.presign(oss.PutObjectRequest(
        bucket=OSS_BUCKET,
        key=filename,
        content_type=content_type,
    ), expires=timedelta(seconds=3600))

    # 返回上传 URL 和可访问的图片路径
    return {
        "uploadUrl": pre_result.url.strip('"'),
        "contentType": content_type,
        "accessUrl": f"https://{OSS_BUCKET}.{OSS_ENDPOINT}/{filename}"
    }


@router.get("/oss/proxy")
async def proxy_oss_image(url: str = Query(...)):
    """
    代理 OSS 图片，绕过浏览器 CORS 限制。
    前端将图片 URL 通过此接口获取，后端转发 OSS 响应并添加 CORS 头。
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as http_client:
            resp = await http_client.get(url)
            return Response(
                content=resp.content,
                media_type=resp.headers.get("Content-Type", "image/jpeg"),
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Cache-Control": "public, max-age=3600",
                },
            )
    except httpx.ConnectTimeout:
        return Response(status_code=504, content=b"Image fetch timeout")
    except httpx.HTTPStatusError as e:
        return Response(status_code=e.response.status_code, content=b"Image fetch failed")
    except Exception:
        return Response(status_code=502, content=b"Image fetch error")


@router.post("/oss/upload")
async def upload_image(file: UploadFile = File(...), filename: str = Form(None)):
    """
    接收前端上传的图片，转发到 OSS。
    用于 UniApp 等无法直接上传到 OSS 的场景。
    """
    # 生成文件名
    if not filename:
        ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
        filename = f"{uuid.uuid4().hex[:12]}.{ext}"

    # 读取文件内容
    content = await file.read()

    # 判断 Content-Type
    content_type_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
    }
    ext = filename.split(".")[-1].lower() if "." in filename else "jpg"
    content_type = content_type_map.get(ext, "application/octet-stream")

    # 上传到 OSS
    client.put_object(oss.PutObjectRequest(
        bucket=OSS_BUCKET,
        key=filename,
        content_type=content_type,
    ), io.BytesIO(content))

    access_url = f"https://{OSS_BUCKET}.{OSS_ENDPOINT}/{filename}"
    return JSONResponse({"accessUrl": access_url})
