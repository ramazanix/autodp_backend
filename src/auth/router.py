from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import UserSchemaCreate, UserSchema, UserSchemaUpdate
from .services import create, get_all, get_with_paswd, delete, update
from .services import get as get_one
from fastapi_jwt_auth import AuthJWT
from ..db import get_db

users_router = APIRouter(prefix="/users", tags=["Users"])
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
    new_user = await create(db, user)
    if not new_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return new_user


@users_router.get("/", response_model=list[UserSchema])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    limit: int | None = None,
):
    return await get_all(db, limit)


@users_router.get("/{username}/", response_model=UserSchema)
async def get_user(
    username: str, db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    user = await get_one(db, username=username)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user


@users_router.patch("/{username}/", response_model=UserSchema)
async def update_user(
    username: str,
    payload: UserSchemaUpdate,
    db: AsyncSession = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    existed_user = await get_one(db, username=username)
    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")
    return await update(db, payload, existed_user)


@users_router.delete("/{username}", status_code=204)
async def delete_user(
    username: str,
    db: AsyncSession = Depends(get_db),
    authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    existed_user = await get_one(db, username=username)
    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")
    return await delete(db, existed_user)
