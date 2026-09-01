"""
Async database engine + session management.

Everything in the RAG pipeline that talks to Postgres goes through
`get_session()` (as an async context manager) so that connections
are always properly opened/closed.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Managed Postgres hosts (Neon, Supabase, Render Postgres, etc.) require
# SSL. asyncpg does NOT understand the "?sslmode=require" query-string
# convention that psycopg/libpq use -- it needs an explicit `ssl`
# connect arg instead. settings.DATABASE_URL strips any sslmode query
# param (see app/core/config.py), and DB_SSL_REQUIRED controls whether
# we pass ssl=True here. Left off by default so local Docker Postgres
# (no SSL configured) keeps working without any extra setup.
connect_args = {"ssl": True} if settings.DB_SSL_REQUIRED else {}

engine = create_async_engine(
    settings.DATABASE_URL, echo=False, pool_pre_ping=True, connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """
    Usage:
        async with get_session() as session:
            ...
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
