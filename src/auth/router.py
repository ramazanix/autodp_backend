from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import UserSchemaCreate, UserSchema, UserSchemaBase
from .services import create, get_all, get_with_paswd, delete
from .services import get as get_one
from fastapi_jwt_auth import AuthJWT
from ..db import get_db

users_router = APIRouter(prefix="/users", tags=["User"])
auth_router = APIRouter(prefix="/auth", tags=["Authenticate"])


@auth_router.post("/login/")
async def login(
    user: UserSchemaCreate,
    db: AsyncSession = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    db_user = await get_with_paswd(db, user)
    if not db_user:
        raise HTTPException(status_code=401, detail="Bad username or password")

    access_token = authorize.create_access_token(subject=user.username)
    refresh_token = authorize.create_refresh_token(subject=user.username)
    return {"access_token": access_token, "refresh_token": refresh_token}


@auth_router.post("/refresh/")
def refresh_access_token(authorize: AuthJWT = Depends()):
    authorize.jwt_refresh_token_required()

    current_user = authorize.get_jwt_subject()
    new_access_token = authorize.create_access_token(subject=current_user)
    return {"access_token": new_access_token}


@users_router.post("/", response_model=UserSchema, status_code=201)
async def create_user(user: UserSchemaCreate, db: AsyncSession = Depends(get_db)):
    return await create(db, user)


@users_router.get("/", response_model=list[UserSchema])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    authorize: AuthJWT = Depends(),
    limit: int | None = None,
):
    authorize.jwt_required()
    return await get_all(db, limit)


@users_router.delete("/", status_code=204)
async def delete_user(
    user: UserSchemaBase,
    db: AsyncSession = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    return await delete(db, username=user.username)


@users_router.get("/{username}/", response_model=UserSchema)
async def get_user(
    username: str, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    return await get_one(db, username=username)
