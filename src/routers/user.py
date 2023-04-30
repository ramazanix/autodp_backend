from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.user import UserSchemaCreate, UserSchema, UserSchemaUpdate
from ..services.user import create, update, delete, get_all, get_by_username
from fastapi_jwt_auth import AuthJWT
from ..db import get_db
from .auth import redis_conn
from ..config import settings


users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/me", response_model=UserSchema)
async def get_current_user(
    db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    db_user = await get_by_username(db, current_user)
    return db_user


@users_router.post("", response_model=UserSchema, status_code=201)
async def create_user(user: UserSchemaCreate, db: AsyncSession = Depends(get_db)):
    new_user = await create(db, user)
    if not new_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return new_user


@users_router.get("", response_model=list[UserSchema])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    limit: int | None = None,
):
    return await get_all(db, limit)


@users_router.get("/{username}", response_model=UserSchema)
async def get_user(
    username: str, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user = await get_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user


@users_router.patch("/{username}", response_model=UserSchema)
async def update_user(
    username: str,
    payload: UserSchemaUpdate,
    db: AsyncSession = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    if not authorize.get_jwt_subject() == username:
        raise HTTPException(status_code=405)

    new_user_data: dict = payload.dict()
    if not any(new_user_data.values()):
        raise HTTPException(status_code=400)

    existed_user = await get_by_username(db, username=username)

    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")

    if new_username := new_user_data.get("username"):
        new_access_token = authorize.create_access_token(subject=new_username)
        authorize.set_access_cookies(new_access_token)

    return await update(db, payload, existed_user)


@users_router.delete("/{username}", status_code=204)
async def delete_user(
    username: str,
    db: AsyncSession = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    if not authorize.get_jwt_subject() == username:
        raise HTTPException(status_code=405)

    existed_user = await get_by_username(db, username=username)
    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")
    jti = authorize.get_raw_jwt()["jti"]
    redis_conn.setex(jti, settings.AUTHJWT_COOKIE_MAX_AGE, "true")
    authorize.unset_jwt_cookies()
    return await delete(db, existed_user)
