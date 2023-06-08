from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..routers import admin_router
from ..schemas.role import RoleSchemaBase, RoleSchema
from ..services.role import get_all, get_by_name
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
    await authorize.is_admin(db)
    return await get_all(db, limit)


@admin_router.get("/roles/{role_name}", response_model=RoleSchema)
@roles_router.get("/{role_name}", response_model=RoleSchema)
async def get_role(
    role_name: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    await authorize.is_admin(db)
    role = await get_by_name(db, role_name)
    if not role:
        raise HTTPException(status_code=400, detail="Role not found")
    return role
