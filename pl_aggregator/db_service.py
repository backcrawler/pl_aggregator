from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncConnection, AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession

from .configs import get_settings

settings = get_settings()


def get_db_engine() -> AsyncEngine:
    engine = create_async_engine(
        f'postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}/{settings.db_name}'
    )
    return engine


@asynccontextmanager
async def get_db_connection() -> AsyncConnection:
    engine = get_db_engine()
    async with engine.begin() as conn:
        yield conn
