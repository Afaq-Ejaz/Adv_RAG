"""Google Cloud Storage adapter (production).

Uses the ``google-cloud-storage`` library.  The bucket name comes from
``settings.gcs_bucket``.  Keys are the same tenant-prefixed paths used
by ``LocalStorage``.
"""

from advance_rag.core.logging import get_logger

log = get_logger(__name__)


class GCSStorage:
    """Store and retrieve files in a GCS bucket.

    Requires ``google-cloud-storage`` to be installed (added in production
    dependencies).  The dependency is imported lazily so that dev environments
    without it still work.
    """

    def __init__(self, bucket_name: str) -> None:
        from google.cloud import storage  # lazy import

        self._client = storage.Client()
        self._bucket = self._client.bucket(bucket_name)
        self._bucket_name = bucket_name

    async def put(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        blob = self._bucket.blob(key)
        blob.upload_from_string(data, content_type=content_type)
        uri = f"gs://{self._bucket_name}/{key}"
        log.debug("gcs_storage_put", key=key, size=len(data))
        return uri

    async def get(self, key: str) -> bytes:
        blob = self._bucket.blob(key)
        if not blob.exists():
            raise FileNotFoundError(f"Object not found: gs://{self._bucket_name}/{key}")
        return blob.download_as_bytes()

    async def delete(self, key: str) -> None:
        blob = self._bucket.blob(key)
        if blob.exists():
            blob.delete()

    async def exists(self, key: str) -> bool:
        return self._bucket.blob(key).exists()
