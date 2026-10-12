"""Database engine/session management and ORM base classes.

One driver (psycopg 3) serves both the async API path and the sync paths
(Alembic migrations, Dramatiq workers, CLI), using the same `postgresql+psycopg://` URL.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Engine, MetaData, create_engine, func, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

# Deterministic constraint names keep Alembic migrations stable and reviewable.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Database:
    """Owns the engines. Engines connect lazily, so constructing this is cheap."""

    def __init__(self, url: str, *, echo: bool = False) -> None:
        self.url = url
        self.engine: AsyncEngine = create_async_engine(url, echo=echo, pool_pre_ping=True)
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self.engine, expire_on_commit=False
        )
        self._sync_engine: Engine | None = None
        self._sync_session_factory: sessionmaker[Session] | None = None

    @property
    def sync_session_factory(self) -> sessionmaker[Session]:
        """Sync sessions for Dramatiq workers and CLI commands."""
        if self._sync_session_factory is None:
            self._sync_engine = create_engine(self.url, pool_pre_ping=True)
            self._sync_session_factory = sessionmaker(self._sync_engine, expire_on_commit=False)
        return self._sync_session_factory

    async def ping(self) -> None:
        async with self.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

    async def dispose(self) -> None:
        await self.engine.dispose()
        if self._sync_engine is not None:
            self._sync_engine.dispose()
