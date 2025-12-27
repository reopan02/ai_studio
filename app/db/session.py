from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from starlette.exceptions import HTTPException

from app.config import get_settings

_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def _normalize_async_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    if database_url.startswith("postgresql+psycopg2://"):
        return database_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    if database_url.startswith("postgresql+psycopg://"):
        return database_url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
    if database_url.startswith("sqlite:///") and "+aiosqlite" not in database_url:
        return database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    if database_url.startswith("sqlite://") and "+aiosqlite" not in database_url:
        return database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return database_url


def init_engine() -> AsyncEngine | None:
    global _engine, _async_session_factory

    if _engine is not None:
        return _engine

    settings = get_settings()
    if not settings.DATABASE_URL:
        return None

    database_url = _normalize_async_database_url(settings.DATABASE_URL)
    _engine = create_async_engine(
        database_url,
        echo=settings.DB_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_pre_ping=True,
    )
    _async_session_factory = async_sessionmaker(
        bind=_engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _async_session_factory is None:
        raise RuntimeError("Database is not configured (DATABASE_URL missing)")
    return _async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        session_factory = get_session_factory()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    async with session_factory() as session:
        yield session


async def dispose_engine() -> None:
    global _engine, _async_session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _async_session_factory = None
