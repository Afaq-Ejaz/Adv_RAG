"""Process-wide infrastructure clients, built once at startup and closed at shutdown.

Clients connect lazily, so building `Resources` doesn't need the services to be up.
Tests inject their own `Resources` (fake health checks, no clients).
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis

from advance_rag.core.config import Settings
from advance_rag.core.db import Database
from advance_rag.infra.health import HealthCheck


@dataclass
class Resources:
    health_checks: Sequence[HealthCheck] = field(default_factory=tuple)
    db: Database | None = None
    redis: Redis | None = None
    qdrant: AsyncQdrantClient | None = None

    async def aclose(self) -> None:
        if self.db is not None:
            await self.db.dispose()
        if self.redis is not None:
            await self.redis.aclose()
        if self.qdrant is not None:
            await self.qdrant.close()


def build_resources(settings: Settings) -> Resources:
    db = Database(settings.database_url)
    redis = Redis.from_url(settings.redis_url)
    qdrant = AsyncQdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key.get_secret_value() if settings.qdrant_api_key else None,
    )

    async def ping_redis() -> None:
        await redis.ping()

    async def ping_qdrant() -> None:
        await qdrant.get_collections()

    return Resources(
        health_checks=(
            HealthCheck("database", db.ping),
            HealthCheck("redis", ping_redis),
            HealthCheck("qdrant", ping_qdrant),
        ),
        db=db,
        redis=redis,
        qdrant=qdrant,
    )
