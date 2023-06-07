from src.models import Post
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence
from sqlalchemy import select as sa_select
from sqlalchemy import update as sa_update
from ..schemas.post import PostSchemaCreate, PostSchemaUpdate


async def get_all(db: AsyncSession, bound: int | None = None) -> Sequence[Post]:
    return (await db.execute(sa_select(Post).limit(bound))).scalars().all()


async def get_by_id(db: AsyncSession, post_id: UUID4) -> Post | None:
    return await db.get(Post, post_id)


async def create(db: AsyncSession, post: PostSchemaCreate, owner_id: UUID4) -> Post:
    db_post = Post(title=post.title, text=post.text, owner_id=owner_id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post


async def update(db: AsyncSession, payload: PostSchemaUpdate, post: Post) -> Post:
    update_data = payload.dict(exclude_none=True, exclude_unset=True)
    query = sa_update(Post).where(Post.id == post.id).values(update_data)
    await db.execute(query)
    await db.commit()
    await db.refresh(post)
    return post
