from pydantic import BaseModel, UUID4, Field
from uuid import uuid4


class RoleSchemaBase(BaseModel):
    id: UUID4
    name: str
    description: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {"id": uuid4(), "name": "base", "description": "base user"}
        }


class RoleSchemaCreate(BaseModel):
    name: str = Field(min_length=2, max_length=20)
    description: str = Field(min_length=2, max_length=100)

    class Config:
        schema_extra = {"example": {"name": "base", "description": "base user"}}


class RoleSchemaUpdate(BaseModel):
    name: str | None = Field(min_length=2, max_length=20)
    description: str | None = Field(min_length=2, max_length=100)

    class Config:
        schema_extra = {"example": {"name": "base", "description": "base user"}}


class RoleSchema(RoleSchemaBase):
    users: list["UserSchemaBase"]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": uuid4(),
                "name": "base",
                "description": "base user",
                "users": [{"username": "John"}],
            }
        }


from .user import UserSchemaBase

RoleSchema.update_forward_refs()
