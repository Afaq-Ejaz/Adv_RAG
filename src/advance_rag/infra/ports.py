"""Ports: the interfaces every external system sits behind (the "no-crash" contract, rule 1).

Phase 0 ships in-memory fakes (`infra.fakes`). Real adapters arrive in the phase that needs them:
    ObjectStorage   → LocalStorage / GCSStorage            (Phase 1)
    DocumentParser  → PDF / DOCX parsers                   (Phase 1)
    Embedder        → GeminiEmbedder                       (Phase 2)
    VectorStore     → QdrantVectorStore                    (Phase 2)
    KeywordIndex    → PgKeywordIndex                       (Phase 2)
    LLMClient       → GeminiLLMClient                      (Phase 3)

Every search method takes `tenant_id` explicitly, so tenant scoping can't be forgotten.
Ports may gain *optional* parameters in later phases, but existing signatures don't change.
"""

from collections.abc import AsyncIterator, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable
from uuid import UUID

type Filters = Mapping[str, Any]
"""Equality filters on payload/metadata fields, e.g. {"document_id": "..."}."""


# --------------------------------------------------------------------------- data types
@dataclass(frozen=True, slots=True)
class VectorRecord:
    id: UUID
    tenant_id: UUID
    vector: Sequence[float]
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SearchHit:
    id: UUID
    score: float
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class KeywordRecord:
    id: UUID
    tenant_id: UUID
    text: str
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ParsedSection:
    text: str
    heading_path: tuple[str, ...] = ()
    page: int | None = None


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    sections: Sequence[ParsedSection]
    title: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class LLMUsage:
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass(frozen=True, slots=True)
class LLMResult:
    text: str
    model: str
    usage: LLMUsage = field(default_factory=LLMUsage)


# --------------------------------------------------------------------------- ports
@runtime_checkable
class ObjectStorage(Protocol):
    async def put(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        """Store bytes under `key`; return a URI for it."""
        ...

    async def get(self, key: str) -> bytes: ...

    async def delete(self, key: str) -> None: ...

    async def exists(self, key: str) -> bool: ...


@runtime_checkable
class DocumentParser(Protocol):
    def supports(self, mime_type: str) -> bool: ...

    def parse(self, data: bytes, *, filename: str | None = None) -> ParsedDocument: ...


@runtime_checkable
class Embedder(Protocol):
    @property
    def model(self) -> str: ...

    @property
    def dimension(self) -> int: ...

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

    async def embed_query(self, text: str) -> list[float]: ...


@runtime_checkable
class VectorStore(Protocol):
    async def ensure_collection(self, name: str, dimension: int) -> None: ...

    async def upsert(self, collection: str, records: Sequence[VectorRecord]) -> None: ...

    async def search(
        self,
        collection: str,
        *,
        tenant_id: UUID,
        vector: Sequence[float],
        limit: int = 10,
        filters: Filters | None = None,
    ) -> list[SearchHit]: ...

    async def delete(self, collection: str, *, tenant_id: UUID, ids: Sequence[UUID]) -> None: ...


@runtime_checkable
class KeywordIndex(Protocol):
    async def index(self, records: Sequence[KeywordRecord]) -> None: ...

    async def search(
        self,
        *,
        tenant_id: UUID,
        query: str,
        limit: int = 10,
        filters: Filters | None = None,
    ) -> list[SearchHit]: ...

    async def delete(self, *, tenant_id: UUID, ids: Sequence[UUID]) -> None: ...


@runtime_checkable
class LLMClient(Protocol):
    @property
    def model(self) -> str: ...

    async def generate(self, prompt: str, *, system: str | None = None) -> LLMResult: ...

    def stream(self, prompt: str, *, system: str | None = None) -> AsyncIterator[str]: ...
