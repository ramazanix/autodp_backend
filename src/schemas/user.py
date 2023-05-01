from pydantic import BaseModel, UUID4, validator, Field
from datetime import datetime


class UserSchemaBase(BaseModel):
    username: str = Field(min_length=2, max_length=20)


class UserSchemaCreate(UserSchemaBase):
    password: str = Field(min_length=8, max_length=32)


class UserSchemaUpdate(BaseModel):
    username: str | None = Field(min_length=2, max_length=20)
    password: str | None = Field(min_length=8, max_length=32)


class UserSchema(BaseModel):
    id: UUID4
    username: str
    created_at: str
    updated_at: str

    @validator("created_at", "updated_at", pre=True)
    def parse_dates(cls, value):
        return datetime.strftime(value, "%X %d.%m.%Y %Z")

    class Config:
        orm_mode = True