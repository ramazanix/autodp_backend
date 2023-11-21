import os
import aiofiles
from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
)
from ..routers import admin_router
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.user import (
    UserSchemaCreate,
    UserSchema,
    UserSchemaUpdate,
    UserSchemaUpdateAdmin,
    UserSchemaUpdateAvatar,
)
from ..schemas.post import PostSchemaBase
from ..schemas.image import ImageSchemaBase
from ..services.user import (
    create,
    update,
    delete,
    get_all,
    get_by_username,
    update_avatar,
)
from ..services.role import get_by_name
from ..services.image import create as create_img
from ..services.image import delete as delete_img
from ..config import settings
from ..db import get_db
from ..dependencies import Auth, auth_checker
from ..redis import redis_conn
from ..utils import clear_dir, hash_file_name


users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/me", response_model=UserSchema)
async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    return await authorize.get_current_user(db)


@admin_router.post("/users", response_model=UserSchema, status_code=201)
@users_router.post("", response_model=UserSchema, status_code=201)
async def create_user(
    user: UserSchemaCreate, db: Annotated[AsyncSession, Depends(get_db)]
):
    if user.username in settings.RESERVED_USERNAMES:
        raise HTTPException(status_code=400, detail="Not allowed username")
    new_user = await create(db, user)

    if not new_user:
        raise HTTPException(status_code=400, detail="User already exists")
    return new_user


@admin_router.patch("/users/{username}", response_model=UserSchema)
async def update_user(
    username: str,
    payload: UserSchemaUpdateAdmin,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    await authorize.is_admin(db)

    if payload.username in settings.RESERVED_USERNAMES:
        raise HTTPException(status_code=400, detail="Not allowed username")

    existed_user = await get_by_username(db, username=username)
    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")

    new_user_data: dict = payload.dict()
    if not any(new_user_data.values()):
        raise HTTPException(status_code=400)

    if role_name := new_user_data.get("role_name"):
        db_role = await get_by_name(db, role_name)
        if not db_role:
            raise HTTPException(status_code=400, detail="Role not found")

    if new_user_data.get("username") and username != payload.username:
        another_user = await get_by_username(db, payload.username)
        if another_user:
            raise HTTPException(status_code=400, detail="Username occupied")

    return await update(db, payload, existed_user)


@admin_router.delete("/users/{username}", status_code=204)
async def delete_user(
    username: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    await authorize.is_admin(db)

    existed_user = await get_by_username(db, username)
    if not existed_user:
        raise HTTPException(status_code=400, detail="User not found")
    return await delete(db, existed_user)


@admin_router.get("/users", response_model=list[UserSchema])
@users_router.get("", response_model=list[UserSchema])
async def get_all_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int | None = Query(None, gt=0),
):
    return await get_all(db, limit)


@admin_router.get(
    "/users/{username}", response_model=UserSchema, dependencies=[Depends(auth_checker)]
)
@users_router.get(
    "/{username}", response_model=UserSchema, dependencies=[Depends(auth_checker)]
)
async def get_user(username: str, db: Annotated[AsyncSession, Depends(get_db)]):
    user = await get_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user


@users_router.patch("/me", response_model=UserSchema)
async def update_current_user(
    payload: UserSchemaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    current_user = await authorize.get_current_user(db)

    if payload.username in settings.RESERVED_USERNAMES:
        raise HTTPException(status_code=400, detail="Not allowed username")

    new_user_data: dict = payload.dict()
    if not any(new_user_data.values()):
        raise HTTPException(status_code=400)

    if new_user_data.get("username") and current_user.username != payload.username:
        another_user = await get_by_username(db, payload.username)
        if another_user:
            raise HTTPException(status_code=400, detail="Username occupied")

    return await update(db, payload, current_user)


@users_router.delete("/me", status_code=204)
async def delete_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    current_user = await authorize.get_current_user(db)

    redis_conn.setex(authorize.jti, settings.AUTHJWT_REFRESH_TOKEN_EXPIRES, "true")
    return await delete(db, current_user)


@users_router.get("/{username}/posts", response_model=list[PostSchemaBase])
async def get_user_posts(
    username: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    authorize: Annotated[Auth, Depends(auth_checker)],
):
    db_user = await get_by_username(db, username)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    return db_user.posts


@users_router.post("/me/upload_avatar", response_model=ImageSchemaBase)
async def create_upload_avatar(
    authorize: Annotated[Auth, Depends(auth_checker)],
    file: UploadFile,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    current_user = await authorize.get_current_user(db)
    file_dir = f"{settings.STATIC_PATH}/user_avatars/{current_user.id}"
    clear_dir(file_dir)

    try:
        filename = hash_file_name(file.filename)
        file_ext = file.filename.split(".")[-1]
        file_content = await file.read()
        file_url = f"{settings.STATIC_PATH}/user_avatars/{current_user.id}/{filename}.{file_ext}"
        file_location = os.path.join(file_dir, f"{filename}.{file_ext}")

        os.makedirs(file_dir, exist_ok=True)

        async with aiofiles.open(file_location, "wb+") as image_file:
            file_data = {
                "name": file.filename,
                "size": file.size,
                "location": file_url,
            }
            await image_file.write(file_content)
            image_id = (await create_img(db, file_data)).id
            update_user_schema = UserSchemaUpdateAvatar(avatar_id=image_id)
            await update_avatar(db, update_user_schema, current_user)

    except Exception:
        await delete_img(db, file_data)
        return {"detail": "Something went wrong"}

    finally:
        await file.close()

    return file_data
