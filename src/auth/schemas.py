from pydantic import BaseModel, UUID4
from datetime import datetime


class UserSchemaBase(BaseModel):
    username: str


class UserSchemaCreate(UserSchemaBase):
    password: str


class UserSchema(BaseModel):
    id: UUID4
    username: str
    join_date: datetime

    class Config:
        orm_mode = True
