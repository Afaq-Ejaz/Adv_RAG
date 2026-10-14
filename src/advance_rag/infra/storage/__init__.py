"""Object storage adapters.

Usage:
    storage = create_storage(settings)
"""

from advance_rag.core.config import Settings
from advance_rag.infra.ports import ObjectStorage
from advance_rag.infra.storage.local import LocalStorage


def create_storage(settings: Settings) -> ObjectStorage:
    """Factory: picks the adapter based on ``settings.storage_backend``."""
    if settings.storage_backend == "gcs":
        from advance_rag.infra.storage.gcs import GCSStorage

        if not settings.gcs_bucket:
            raise ValueError("RAG_GCS_BUCKET must be set when storage_backend=gcs")
        return GCSStorage(settings.gcs_bucket)  # type: ignore[return-value]
    return LocalStorage(settings.storage_local_root)  # type: ignore[return-value]
