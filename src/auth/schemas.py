from pydantic import BaseModel, UUID4, validator
from datetime import datetime


class UserSchemaBase(BaseModel):
    username: str


class UserSchemaCreate(UserSchemaBase):
    password: str


class UserSchema(BaseModel):
    id: UUID4
    username: str
    created_at: str
    updated_at: str

    @validator('created_at', 'updated_at', pre=True)
    def parse_dates(cls, value):
        return datetime.strftime(value, '%X %d.%m.%Y %Z')

    class Config:
        orm_mode = True
