from pydantic import BaseModel


class LoginOut(BaseModel):
    access_token: str
    refresh_token: str


class RefreshOut(BaseModel):
    access_token: str
