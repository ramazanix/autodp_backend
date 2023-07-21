from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from ..routers import admin_router
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.user import (
    UserSchemaCreate,
    UserSchema,
    UserSchemaUpdate,
    UserSchemaUpdateAdmin,
)
from ..schemas.post import PostSchemaBase
from ..services.user import create, update, delete, get_all, get_by_username
from ..services.role import get_by_name
from ..config import settings
from ..db import get_db
from ..dependencies import Auth, auth_checker
from ..redis import RedisClient


users_router = APIRouter(prefix="/users", tags=["Users"])
redis_conn = RedisClient().conn


@users_router.get("/me", response_model=UserSchema)
async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    return await authorize.get_current_user(db)


@admin_router.post("/users", response_model=UserSchema, status_code=201)
@users_router.post("", response_model=UserSchema, status_code=201)
async def create_user(
    user: UserSchemaCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    if user.username in settings.RESERVED_USERNAMES:
        raise HTTPException(status_code=400, detail="Not allowed username")
    new_user = await create(db, user)

    if not new_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return new_user


@admin_router.patch("/users/{username}", response_model=UserSchema)
async def update_user(
    username: str,
    payload: UserSchemaUpdateAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    await authorize.is_admin(db)

    if payload.username in settings.RESERVED_USERNAMES:
        raise HTTPException(status_code=400, detail="Not allowed username")

    existed_user = await get_by_username(db, username=username)
    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")

    new_user_data: dict = payload.dict()
    if not any(new_user_data.values()):
        raise HTTPException(status_code=400)

    if role_name := new_user_data.get("role_name"):
        db_role = await get_by_name(db, role_name)
        if not db_role:
            raise HTTPException(status_code=400, detail="Role not found")

    if new_user_data.get("username") and username != payload.username:
        another_user = await get_by_username(db, payload.username)
        if another_user:
            raise HTTPException(status_code=400, detail="Username occupied")

    return await update(db, payload, existed_user)


@admin_router.delete("/users/{username}", status_code=204)
async def delete_user(
    username: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    await authorize.is_admin(db)

    existed_user = await get_by_username(db, username)
    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")
    return await delete(db, existed_user)


@admin_router.get("/users", response_model=list[UserSchema])
@users_router.get("", response_model=list[UserSchema])
async def get_all_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int | None = Query(None, gt=0),
):
    return await get_all(db, limit)


@admin_router.get(
    "/users/{username}", response_model=UserSchema, dependencies=[Depends(auth_checker)]
)
@users_router.get(
    "/{username}", response_model=UserSchema, dependencies=[Depends(auth_checker)]
)
async def get_user(username: str, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await get_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user


@users_router.patch("/me", response_model=UserSchema)
async def update_current_user(
    payload: UserSchemaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    current_user = await authorize.get_current_user(db)

    if payload.username in settings.RESERVED_USERNAMES:
        raise HTTPException(status_code=400, detail="Not allowed username")

    new_user_data: dict = payload.dict()
    if not any(new_user_data.values()):
        raise HTTPException(status_code=400)

    if new_user_data.get("username") and current_user.username != payload.username:
        another_user = await get_by_username(db, payload.username)
        if another_user:
            raise HTTPException(status_code=400, detail="Username occupied")

    return await update(db, payload, current_user)


@users_router.delete("/me", status_code=204)
async def delete_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    current_user = await authorize.get_current_user(db)

    redis_conn.setex(authorize.jti, settings.AUTHJWT_REFRESH_TOKEN_EXPIRES, "true")
    return await delete(db, current_user)


@users_router.get("/{username}/posts", response_model=list[PostSchemaBase])
async def get_user_posts(
    username: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    db_user = await get_by_username(db, username)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    return db_user.posts
