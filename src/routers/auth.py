from typing import Annotated
from ..schemas.user import UserSchemaCreate
from ..schemas.auth import LoginOut, RefreshOut
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import settings
from ..db import get_db
from fastapi_jwt_auth import AuthJWT
from ..services.user import get_with_paswd
from ..dependencies import Auth, base_auth, auth_checker, auth_checker_refresh
from ..redis import RedisClient


auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
redis_conn = RedisClient().conn


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token: str) -> bool:
    jti = decrypted_token["jti"]
    entry = redis_conn.get(jti)
    return entry and entry == "true"


@auth_router.post("/login", response_model=LoginOut)
async def login(
        user: UserSchemaCreate,
        db: Annotated[AsyncSession, Depends(get_db)],
        authorize: Annotated[Auth, Depends(base_auth)],
):
    db_user = await get_with_paswd(db, user)
    if not db_user:
        raise HTTPException(status_code=401, detail="Bad username or password")

    user_claims = {"user_claims": {"id": str(db_user.id)}}
    access_token = authorize.create_access_token(
        subject=user.username, user_claims=user_claims
    )
    refresh_token = authorize.create_refresh_token(
        subject=user.username, user_claims=user_claims
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


@auth_router.post("/refresh", response_model=RefreshOut)
async def refresh_access_token(
        db: Annotated[AsyncSession, Depends(get_db)],
        authorize: Annotated[Auth, Depends(auth_checker_refresh)],
):
    current_user = await authorize.get_current_user(db)
    new_user_claims = {"user_claims": authorize.user_claims}
    new_access_token = authorize.create_access_token(
        subject=current_user.username, user_claims=new_user_claims
    )
    return {"access_token": new_access_token}


@auth_router.delete('/access_revoke', status_code=204)
async def access_revoke(authorize: Annotated[Auth, Depends(auth_checker)]):
    redis_conn.setex(authorize.jti, settings.AUTHJWT_ACCESS_TOKEN_EXPIRES, 'true')


@auth_router.delete('/refresh_revoke', status_code=204)
async def refresh_revoke(authorize: Annotated[Auth, Depends(auth_checker_refresh)]):
    redis_conn.setex(authorize.jti, settings.AUTHJWT_REFRESH_TOKEN_EXPIRES, 'true')


@auth_router.delete("/logout", status_code=204)
async def logout(authorize: Annotated[Auth, Depends(auth_checker)]):
    jti = authorize.jti
    redis_conn.setex(jti, settings.AUTHJWT_ACCESS_TOKEN_EXPIRES, "true")
