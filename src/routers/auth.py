from ..schemas.user import UserSchemaCreate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import settings
from ..db import get_db
from fastapi_jwt_auth import AuthJWT
from ..services.user import get_with_paswd
from redis import Redis

auth_router = APIRouter(prefix="/auth", tags=["Authenticate"])
redis_conn = Redis(
    host=settings.REDIS_HOST, password=settings.REDIS_PASSWORD, decode_responses=True
)


@AuthJWT.load_config
def get_config():
    return settings


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token: str) -> bool:
    jti = decrypted_token["jti"]
    entry = redis_conn.get(jti)
    return entry and entry == "true"


@auth_router.post("/login")
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
    authorize.set_access_cookies(access_token)
    authorize.set_refresh_cookies(refresh_token)
    return {"success": "Successfully login"}


@auth_router.post("/refresh")
def refresh_access_token(authorize: AuthJWT = Depends()):
    authorize.jwt_refresh_token_required()

    current_user = authorize.get_jwt_subject()
    new_access_token = authorize.create_access_token(subject=current_user)
    authorize.set_access_cookies(new_access_token)
    return {"success": "The token has been refreshed"}


@auth_router.delete("/logout")
async def logout(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    authorize.unset_jwt_cookies()
    return {"success": "Successfully logout"}
