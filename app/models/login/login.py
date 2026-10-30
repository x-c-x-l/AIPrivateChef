from pydantic import BaseModel, Field


class LoginRequset(BaseModel):
    username: str
    password: str
    # code: str
    # codeid: str


class RegisterRequset(BaseModel):
    username: str
    password: str
    name: str
    email: str = Field(default="")
    phone: str = Field(default="")
    # code: str
    # codeid: str
