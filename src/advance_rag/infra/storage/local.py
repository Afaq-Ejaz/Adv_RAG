"""Local filesystem object storage adapter (development).

Files are stored under ``{root}/{key}`` where ``root`` comes from
``settings.storage_local_root``.  The key is expected to already be
tenant-prefixed (``{tenant_id}/documents/{doc_id}/{filename}``).
"""

import os
from pathlib import Path

from advance_rag.core.logging import get_logger

log = get_logger(__name__)


class LocalStorage:
    """Store and retrieve files on the local filesystem."""

    def __init__(self, root: str) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        # Prevent path traversal
        safe = Path(key).as_posix().lstrip("/")
        return self._root / safe

    async def put(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        log.debug("local_storage_put", key=key, size=len(data))
        return f"file://{path.resolve().as_posix()}"

    async def get(self, key: str) -> bytes:
        path = self._path(key)
        if not path.exists():
            raise FileNotFoundError(f"Object not found: {key}")
        return path.read_bytes()

    async def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            os.remove(path)

    async def exists(self, key: str) -> bool:
        return self._path(key).exists()
