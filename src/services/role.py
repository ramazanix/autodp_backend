from src.models import Role
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.role import RoleSchemaCreate, RoleSchemaUpdate
from collections.abc import Sequence
from sqlalchemy import select as sa_select
from sqlalchemy import update as sa_update


async def get_all(db: AsyncSession, bound: int | None = None) -> Sequence[Role]:
    return (await db.execute(sa_select(Role).limit(bound))).scalars().all()


async def get_by_name(db: AsyncSession, name: str) -> Role:
    return (
        await db.execute(sa_select(Role).where(Role.name == name))
    ).scalar_one_or_none()


async def create(db: AsyncSession, role: RoleSchemaCreate) -> Role | None:
    if await get_by_name(db, role.name):
        return None
    db_role = Role(**role.dict())
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role


async def update(db: AsyncSession, payload: RoleSchemaUpdate, role: Role) -> Role:
    update_data = payload.dict(exclude_none=True, exclude_unset=True)
    query = sa_update(Role).where(Role.name == role.name).values(update_data)
    await db.execute(query)
    await db.commit()
    await db.refresh(role)
    return role


async def delete(db: AsyncSession, role: Role) -> None:
    await db.delete(role)
    await db.commit()
