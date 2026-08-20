"""
core/database.py
================
SQLAlchemy async engine and session factory.

Usage in routes (via dependency injection):
    async def my_route(db: AsyncSession = Depends(get_db)):
        ...

The engine is created lazily on first use so test environments that do not
have asyncpg installed can still import this module without errors.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import get_settings

# ------------------------------------------------------------------ #
# Naming Convention for Alembic auto-migrations
# ------------------------------------------------------------------ #
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


# ------------------------------------------------------------------ #
# Declarative Base — all models inherit from this
# ------------------------------------------------------------------ #
class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    Provides consistent naming conventions for auto-generated
    constraint names (important for Alembic migrations).
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# ------------------------------------------------------------------ #
# Lazy engine / session factory
# ------------------------------------------------------------------ #
_engine: "AsyncEngine | None" = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> "AsyncEngine":
    """Return the async engine, creating it on first call (lazy initialization)."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the session factory, creating it on first call."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False,
        )
    return _session_factory


# ------------------------------------------------------------------ #
# FastAPI Dependency — provides a DB session per request
# ------------------------------------------------------------------ #
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session dependency.

    Yields a session that is committed on success and rolled back on error.
    Always closed after the request completes.

    Example:
        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ------------------------------------------------------------------ #
# Health check utility
# ------------------------------------------------------------------ #
async def check_database_connection() -> bool:
    """
    Test database connectivity.
    Returns True if a simple query succeeds, False otherwise.
    Used by the /health endpoint.
    """
    try:
        factory = get_session_factory()
        async with factory() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
