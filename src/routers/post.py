from typing import Annotated
from pydantic import UUID4
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..routers import admin_router
from ..schemas.post import PostSchema, PostSchemaCreate, PostSchemaUpdate
from ..services.post import get_all, get_by_id, create, update, delete
from ..db import get_db
from ..dependencies import Auth, auth_checker


posts_router = APIRouter(prefix="/posts", tags=["Posts"])


@admin_router.get("/posts", response_model=list[PostSchema])
@posts_router.get("", response_model=list[PostSchema])
async def get_all_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int | None = Query(None, gt=0),
):
    return await get_all(db, limit)


@admin_router.get("/posts/{post_id}", response_model=PostSchema)
@posts_router.get("/{post_id}", response_model=PostSchema)
async def get_post(post_id: UUID4, db: Annotated[AsyncSession, Depends(get_db)]):
    post = await get_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=400, detail="Post not found")
    return post


@admin_router.post("/posts", response_model=PostSchema, status_code=201)
@posts_router.post("", response_model=PostSchema, status_code=201)
async def create_post(
    post: PostSchemaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    current_user = await authorize.get_current_user(db)
    owner_id = current_user.id
    return await create(db, post, owner_id)


@admin_router.patch("/posts/{post_id}", response_model=PostSchema)
@posts_router.patch("/{post_id}", response_model=PostSchema)
async def update_post(
    post_id: UUID4,
    payload: PostSchemaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    db_post = await get_by_id(db, post_id)
    if not db_post:
        raise HTTPException(status_code=400, detail="Post not found")

    current_user = await authorize.get_current_user(db)
    if db_post.owner_id != current_user.id and current_user.role.name != "admin":
        raise HTTPException(status_code=403)

    new_post_data: dict = payload.dict()
    if not any(new_post_data.values()):
        raise HTTPException(status_code=400)

    return await update(db, payload, db_post)


@admin_router.delete("/posts/{post_id}", status_code=204)
@posts_router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: UUID4,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    db_post = await get_by_id(db, post_id)
    if not db_post:
        raise HTTPException(status_code=400, detail="Post not found")

    current_user = await authorize.get_current_user(db)
    if db_post.owner_id != current_user.id and current_user.role.name != "admin":
        raise HTTPException(status_code=403)

    return await delete(db, db_post)
