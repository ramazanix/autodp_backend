from passlib.context import CryptContext
from redis import Redis
from .config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
redis_conn = Redis(
    host=settings.REDIS_HOST, password=settings.REDIS_PASSWORD, decode_responses=True
)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(raw_password, hashed_password)


def get_password_hash(raw_password: str) -> str:
    return pwd_context.hash(raw_password)
