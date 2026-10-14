"""Dramatiq broker configuration and actors.

Uses Redis as the message broker.  The broker is configured once at import time,
which is the Dramatiq convention.

Workers are started with: ``dramatiq advance_rag.workers.broker``
"""

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.results import Results
from dramatiq.results.backends import RedisBackend

from advance_rag.core.config import get_settings

_settings = get_settings()
_redis_broker = RedisBroker(url=_settings.redis_url)
_result_backend = RedisBackend(url=_settings.redis_url)
_redis_broker.add_middleware(Results(backend=_result_backend))
dramatiq.set_broker(_redis_broker)


@dramatiq.actor
def ping() -> str:
    """Smoke-test actor: verifies that the Dramatiq worker is running and can process jobs."""
    return "pong"
