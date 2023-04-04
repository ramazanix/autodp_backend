from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config import settings
from src.db import session_manager


def init_app(init_db=True):
    lifespan = None

    if init_db:
        session_manager.init(settings.DB_URL)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if session_manager._engine is not None:
                await session_manager.close()

    server = FastAPI(title="My FastAPI Server", lifespan=lifespan)

    from .main import main_router, auth_jwt_exception_handler
    from .auth.router import auth_router, users_router
    from fastapi_jwt_auth.exceptions import AuthJWTException

    server.include_router(main_router)
    server.include_router(auth_router)
    server.include_router(users_router)
    server.add_exception_handler(AuthJWTException, auth_jwt_exception_handler)

    return server


server = init_app()
