from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..routers import admin_router
from ..schemas.post import PostSchema, PostSchemaCreate
from ..services.post import get_all, create
from ..services.user import get_by_id as get_user_by_id
from ..db import get_db
from ..dependencies import Auth, auth_checker


posts_router = APIRouter(prefix="/posts", tags=["Posts"])


@admin_router.get("/posts", response_model=list[PostSchema])
@posts_router.get("", response_model=list[PostSchema])
async def get_all_posts(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
    limit: int | None = Query(None, gt=0),
):
    return await get_all(db, limit)


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
