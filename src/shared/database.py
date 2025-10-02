"""
Database connection and session management
"""

from collections.abc import AsyncGenerator

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings

logger = structlog.get_logger()


# Async engine (for Cloud Functions)
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Base class for all models
class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    Use in Cloud Functions like:
        async with get_db() as db:
            result = await db.execute(...)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def execute_raw_sql(query: str, params: dict | None = None):
    """
    Execute raw SQL query

    Example:
        result = await execute_raw_sql(
            "SELECT * FROM users WHERE id = :id",
            {"id": 123}
        )
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(text(query), params or {})
        await session.commit()
        return result


async def health_check() -> bool:
    """Check database connection"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return False
