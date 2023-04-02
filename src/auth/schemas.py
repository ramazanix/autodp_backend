from pydantic import BaseModel, UUID4


class UserSchemaBase(BaseModel):
    username: str


class UserSchemaCreate(UserSchemaBase):
    password: str


class UserSchema(BaseModel):
    id: UUID4
    username: str

    class Config:
        orm_mode = True
