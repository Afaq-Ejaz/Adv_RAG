"""FastAPI application factory.

``create_app()`` is the ASGI entry-point referenced by the CLI (``uvicorn
advance_rag.api.app:create_app --factory``).

Lifecycle:
    startup  → build infrastructure clients (DB, Redis, Qdrant)
    shutdown → close all connections gracefully

The app stores shared resources on ``app.state.resources`` so any route can
reach them via ``request.app.state.resources``.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from advance_rag.api.middleware import RequestContextMiddleware
from advance_rag.api.routes import health, documents
from advance_rag.core.config import get_settings
from advance_rag.core.errors import register_exception_handlers
from advance_rag.core.logging import configure_logging
from advance_rag.infra.resources import build_resources


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    resources = build_resources(settings)
    app.state.resources = resources
    app.state.settings = settings
    yield
    await resources.aclose()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(level=settings.log_level, json=settings.log_json)

    app = FastAPI(
        title="Advance RAG API",
        version="0.1.0",
        lifespan=_lifespan,
    )

    # --- middleware (outermost first)
    app.add_middleware(RequestContextMiddleware)

    # --- error handlers
    register_exception_handlers(app)

    # --- routes
    app.include_router(health.router, prefix="/v1")
    app.include_router(documents.router, prefix="/v1")

    return app
