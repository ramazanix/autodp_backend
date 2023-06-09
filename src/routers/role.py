from typing import Annotated
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..routers import admin_router
from ..schemas.role import (
    RoleSchemaBase,
    RoleSchema,
    RoleSchemaCreate,
    RoleSchemaUpdate,
)
from ..services.role import get_all, get_by_name, create, update, delete
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


@admin_router.post("/roles", response_model=RoleSchemaBase)
@roles_router.post("", response_model=RoleSchemaBase)
async def create_role(
    role: RoleSchemaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    await authorize.is_admin(db)
    new_role = await create(db, role)

    if not new_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    return new_role


@admin_router.patch("/roles/{role_name}", response_model=RoleSchemaBase)
@roles_router.patch("/{role_name}", response_model=RoleSchemaBase)
async def update_role(
    role_name: str,
    payload: RoleSchemaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    await authorize.is_admin(db)

    existed_role = await get_by_name(db, role_name)
    if not existed_role:
        raise HTTPException(status_code=400, detail="Role not found")

    new_role_data: dict = payload.dict()
    if not any(new_role_data.values()):
        raise HTTPException(status_code=400)

    if new_role_data.get("name") and role_name != payload.name:
        another_role = await get_by_name(db, payload.name)
        if another_role:
            raise HTTPException(status_code=400, detail="Role already exists")

    return await update(db, payload, existed_role)


@admin_router.delete("/roles/{role_name}", status_code=204)
@roles_router.delete("/{role_name}", status_code=204)
async def delete_role(
    role_name: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    await authorize.is_admin(db)
    existed_role = await get_by_name(db, role_name)
    if not existed_role:
        raise HTTPException(status_code=400, detail="Role not found")
    return await delete(db, existed_role)
