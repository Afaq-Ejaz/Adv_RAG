"""Alembic environment configuration.

Reads the database URL from the application settings (``RAG_DATABASE_URL``)
when available, falling back to ``alembic.ini`` for CI-only usage.

Uses the synchronous psycopg driver for migrations — the same URL works because
``postgresql+psycopg://`` supports both sync and async depending on the calling
context.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool

from advance_rag.core.config import get_settings
from advance_rag.core.db import Base

# Import every ORM model so Base.metadata is fully populated.
import advance_rag.db_models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Prefer the live application setting over the static alembic.ini value.
_url = get_settings().database_url
if _url:
    config.set_main_option("sqlalchemy.url", _url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — emit SQL without a live connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against the database."""
    from sqlalchemy import create_engine

    connectable = create_engine(
        config.get_main_option("sqlalchemy.url", ""),
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
