from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.user import UserSchemaCreate, UserSchema, UserSchemaUpdate
from ..services.user import create, update, delete, get_all, get_by_username, get_by_id
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
    user_claims = authorize.get_raw_jwt()["user_claims"]
    db_user = await get_by_id(db, user_claims)
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
    limit: int | None = Query(None, gt=0),
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
    current_user_id = authorize.get_raw_jwt()["user_claims"]["id"]
    existed_user = await get_by_username(db, username=username)

    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")

    if not str(existed_user.id) == current_user_id:
        raise HTTPException(status_code=405)

    new_user_data: dict = payload.dict()
    if not any(new_user_data.values()):
        raise HTTPException(status_code=400)

    return await update(db, payload, existed_user)


@users_router.delete("/{username}", status_code=204)
async def delete_user(
    username: str,
    db: AsyncSession = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    current_user_id = authorize.get_raw_jwt()["user_claims"]["id"]
    existed_user = await get_by_username(db, username=username)

    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")

    if not str(existed_user.id) == current_user_id:
        raise HTTPException(status_code=405)

    jti = authorize.get_raw_jwt()["jti"]
    redis_conn.setex(jti, settings.AUTHJWT_COOKIE_MAX_AGE, "true")
    authorize.unset_jwt_cookies()
    return await delete(db, existed_user)
