from sqlalchemy import Column, String, Uuid, DateTime
from sqlalchemy.sql import func
from uuid import uuid4
from src.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, unique=True, nullable=False, default=uuid4)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), default=func.now()
    )
