from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.schemas import UserSchema
from src.auth.services import get
from src.config import settings
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from src.db import get_db

main_router = APIRouter(prefix="")


@AuthJWT.load_config
def get_config():
    return settings


def auth_jwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@main_router.get("/user/", response_model=UserSchema, tags=["Current_User"])
async def get_current_user(
    db: AsyncSession = Depends(get_db), authorize: AuthJWT = Depends()
):
    authorize.jwt_required()
    current_user = authorize.get_jwt_subject()
    db_user = await get(db, current_user)
    return db_user
