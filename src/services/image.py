from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select as sa_select
from ..models import Image


async def create(db: AsyncSession, image: dict[str, str | int]) -> Image | None:
    db_image = Image(**image)
    db.add(db_image)
    await db.commit()
    await db.refresh(db_image)
    return db_image


async def get_by_name(db: AsyncSession, name: str) -> Image | None:
    return (
        await db.execute(sa_select(Image).where(Image.name == name))
    ).scalar_one_or_none()


async def delete(db: AsyncSession, image: dict[str, str | int]) -> None:
    db_image = Image(**image)
    await db.delete(db_image)
    await db.commit()
