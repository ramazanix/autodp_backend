from pydantic import BaseModel, Field, UUID4, validator
from datetime import datetime


class PostSchemaBase(BaseModel):
    id: UUID4
    title: str

    class Config:
        orm_mode = True


class PostSchemaCreate(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    text: str = Field(min_length=15, max_length=1000)


class PostSchemaUpdate(BaseModel):
    title: str | None = Field(min_length=3, max_length=50)
    text: str | None = Field(min_length=15, max_length=1000)


class PostSchema(BaseModel):
    id: UUID4
    title: str
    text: str
    owner: "UserSchema" = Field(exclude={"role", "created_at", "updated_at"})
    created_at: str
    updated_at: str

    @validator("created_at", "updated_at", pre=True)
    def parse_dates(cls, value):
        return datetime.strftime(value, "%X %d.%m.%Y %Z")

    class Config:
        orm_mode = True


from .user import UserSchema

PostSchema.update_forward_refs()
