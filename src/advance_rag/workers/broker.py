"""Dramatiq broker configuration and actors.

Uses Redis as the message broker.  The broker is configured once at import time,
which is the Dramatiq convention.

Workers are started with: ``dramatiq advance_rag.workers.broker``
"""

import asyncio
import uuid

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend

from advance_rag.core.config import get_settings
from advance_rag.core.logging import get_logger

log = get_logger(__name__)

_settings = get_settings()
_redis_broker = RedisBroker(url=_settings.redis_url)
_result_backend = RedisBackend(url=_settings.redis_url)
_redis_broker.add_middleware(Results(backend=_result_backend))
dramatiq.set_broker(_redis_broker)


@dramatiq.actor
def ping() -> str:
    """Smoke-test actor: verifies that the Dramatiq worker is running and can process jobs."""
    return "pong"


@dramatiq.actor(max_retries=3, min_backoff=1_000, max_backoff=60_000)
def process_document(document_id: str) -> None:
    """Parse and chunk a document.  Runs in a Dramatiq worker process.

    This bridges the synchronous Dramatiq world with the async service layer
    by using ``asyncio.run()`` for the DB/storage calls.
    """
    log.info("process_document_started", document_id=document_id)

    async def _run() -> None:
        from advance_rag.documents import service as doc_service
        from advance_rag.infra.storage import create_storage

        settings = get_settings()
        storage = create_storage(settings)

        from advance_rag.core.db import Database

        db = Database(settings.database_url)
        try:
            async with db.session_factory() as session:
                try:
                    chunks = await doc_service.parse_and_chunk(
                        session,
                        document_id=uuid.UUID(document_id),
                        storage=storage,
                    )
                    await session.commit()
                    log.info(
                        "process_document_completed",
                        document_id=document_id,
                        chunk_count=len(chunks),
                    )
                except Exception:
                    await session.rollback()
                    raise
        finally:
            await db.dispose()

    asyncio.run(_run())

