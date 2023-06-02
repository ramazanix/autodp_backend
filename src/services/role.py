from src.models import Role
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence
from sqlalchemy import select as sa_select


async def get_all(db: AsyncSession, bound: int | None = None) -> Sequence[Role]:
    return (await db.execute(sa_select(Role).limit(bound))).scalars().all()


async def get_by_name(db: AsyncSession, name: str | None) -> Role:
    return (
        await db.execute(sa_select(Role).where(Role.name == name))
    ).scalar_one_or_none()
