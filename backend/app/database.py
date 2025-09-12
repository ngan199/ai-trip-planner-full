# Purpose: Async SQLAlchemy engine/session using typed Settings (no dict() lookups)
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from .settings import Settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


# Use typed attribute from Settings (fixes ValidationError due to dict()-based access)
_s = Settings()
engine: AsyncEngine = create_async_engine(_s.database_url)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator:
    """FastAPI dependency that yields an async DB session."""
    async with async_session() as session:
        yield session
