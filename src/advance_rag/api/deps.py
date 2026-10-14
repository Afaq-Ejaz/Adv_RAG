"""FastAPI dependency injection helpers.

Provides request-scoped database sessions, access to infrastructure resources,
and the current request context.  All routes use these instead of constructing
their own sessions.
"""

from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from advance_rag.core.context import RequestContext, require_context
from advance_rag.core.db import Database
from advance_rag.infra.resources import Resources


def get_resources(request: Request) -> Resources:
    return request.app.state.resources


def get_db(request: Request) -> Database:
    resources: Resources = request.app.state.resources
    assert resources.db is not None, "Database not initialised"
    return resources.db


async def get_session(db: Database = Depends(get_db)) -> AsyncIterator[AsyncSession]:
    """Yields a request-scoped async session; commits on success, rolls back on error."""
    async with db.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_context() -> RequestContext:
    """Returns the RequestContext set by RequestContextMiddleware."""
    return require_context()
