from typing import Optional, Any
from pydantic import BaseModel, Field


class ResponseData(BaseModel):
    message: str = Field(default="操作成功")
    data: Optional[Any] = Field(default="")
    code: str = Field(default="200")
