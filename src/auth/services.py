from passlib.context import CryptContext
from .models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select
from sqlalchemy import delete as sql_del
from .schemas import UserSchemaCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(raw_password, hashed_password)


def get_password_hash(raw_password: str) -> str:
    return pwd_context.hash(raw_password)


async def create(db: AsyncSession, user: UserSchemaCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_with_paswd(db: AsyncSession, user: UserSchemaCreate) -> User | None:
    try:
        db_user = (
            await db.execute(select(User).where((User.username == user.username)))
        ).scalar()
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            raise NoResultFound
        return db_user
    except NoResultFound:
        return None


async def get(db: AsyncSession, username: str) -> User | None:
    return (
        await db.execute(select(User).where(User.username == username))
    ).scalar_one_or_none()


async def get_all(db: AsyncSession, bound: int | None = None):
    return (await db.execute(select(User).limit(bound))).scalars().all()


async def delete(db: AsyncSession, username: str) -> None:
    query = sql_del(User).where(User.username == username)
    await db.execute(query)
    await db.commit()
