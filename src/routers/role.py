from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..routers import admin_router
from ..schemas.role import RoleSchemaBase
from ..services.role import get_all
from ..db import get_db
from ..dependencies import Auth, auth_checker


roles_router = APIRouter(prefix="/roles", tags=["Roles"])


@admin_router.get("/roles", response_model=list[RoleSchemaBase])
@roles_router.get("", response_model=list[RoleSchemaBase])
async def get_all_roles(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
    limit: int | None = Query(None, gt=0),
):
    current_user = await authorize.get_current_user(db)
    if not current_user.role.name == "admin":
        raise HTTPException(status_code=403)

    return await get_all(db, limit)
