"""In-memory fake adapters for every port.

Used by unit tests and for local experiments with no infrastructure at all.
They're deterministic and enforce tenant isolation the same way real adapters must.
"""

import hashlib
import math
import re
from collections.abc import AsyncIterator, Mapping, Sequence
from typing import Any
from uuid import UUID

from advance_rag.infra.ports import (
    Filters,
    KeywordRecord,
    LLMResult,
    LLMUsage,
    ParsedDocument,
    ParsedSection,
    SearchHit,
    VectorRecord,
)

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


def _matches(payload: Mapping[str, Any], filters: Filters | None) -> bool:
    return not filters or all(payload.get(k) == v for k, v in filters.items())


class InMemoryObjectStorage:
    def __init__(self) -> None:
        self._objects: dict[str, bytes] = {}

    async def put(self, key: str, data: bytes, *, content_type: str | None = None) -> str:
        self._objects[key] = data
        return f"memory://{key}"

    async def get(self, key: str) -> bytes:
        try:
            return self._objects[key]
        except KeyError:
            raise FileNotFoundError(key) from None

    async def delete(self, key: str) -> None:
        self._objects.pop(key, None)

    async def exists(self, key: str) -> bool:
        return key in self._objects


class PlainTextParser:
    """Stub parser: one section per blank-line-separated paragraph."""

    def supports(self, mime_type: str) -> bool:
        return mime_type.startswith("text/")

    def parse(self, data: bytes, *, filename: str | None = None) -> ParsedDocument:
        text = data.decode("utf-8", errors="replace")
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        return ParsedDocument(sections=[ParsedSection(text=p) for p in paragraphs], title=filename)


class HashEmbedder:
    """Deterministic bag-of-words hashing embedder. Similar texts give similar vectors."""

    def __init__(self, dimension: int = 64) -> None:
        self._dimension = dimension

    @property
    def model(self) -> str:
        return f"fake-hash-{self._dimension}"

    @property
    def dimension(self) -> int:
        return self._dimension

    def _embed(self, text: str) -> list[float]:
        vec = [0.0] * self._dimension
        for token in _tokens(text):
            digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
            vec[int.from_bytes(digest[:4], "big") % self._dimension] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    async def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._collections: dict[str, tuple[int, dict[UUID, VectorRecord]]] = {}

    async def ensure_collection(self, name: str, dimension: int) -> None:
        if name in self._collections:
            existing_dim, _ = self._collections[name]
            if existing_dim != dimension:
                raise ValueError(f"Collection {name!r} has dimension {existing_dim}, not {dimension}")
            return
        self._collections[name] = (dimension, {})

    def _records(self, collection: str) -> dict[UUID, VectorRecord]:
        try:
            return self._collections[collection][1]
        except KeyError:
            raise KeyError(f"Unknown collection {collection!r}") from None

    async def upsert(self, collection: str, records: Sequence[VectorRecord]) -> None:
        dimension = self._collections.get(collection, (None, None))[0]
        store = self._records(collection)
        for record in records:
            if len(record.vector) != dimension:
                raise ValueError(f"Vector dimension {len(record.vector)} != {dimension}")
            store[record.id] = record

    async def search(
        self,
        collection: str,
        *,
        tenant_id: UUID,
        vector: Sequence[float],
        limit: int = 10,
        filters: Filters | None = None,
    ) -> list[SearchHit]:
        hits = [
            SearchHit(id=r.id, score=_cosine(vector, r.vector), payload=r.payload)
            for r in self._records(collection).values()
            if r.tenant_id == tenant_id and _matches(r.payload, filters)
        ]
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:limit]

    async def delete(self, collection: str, *, tenant_id: UUID, ids: Sequence[UUID]) -> None:
        store = self._records(collection)
        for id_ in ids:
            record = store.get(id_)
            if record is not None and record.tenant_id == tenant_id:
                del store[id_]


class InMemoryKeywordIndex:
    """Simple term-overlap scoring. The real adapter uses Postgres FTS (Phase 2)."""

    def __init__(self) -> None:
        self._records: dict[UUID, KeywordRecord] = {}

    async def index(self, records: Sequence[KeywordRecord]) -> None:
        for record in records:
            self._records[record.id] = record

    async def search(
        self,
        *,
        tenant_id: UUID,
        query: str,
        limit: int = 10,
        filters: Filters | None = None,
    ) -> list[SearchHit]:
        terms = set(_tokens(query))
        hits: list[SearchHit] = []
        for r in self._records.values():
            if r.tenant_id != tenant_id or not _matches(r.payload, filters):
                continue
            tokens = _tokens(r.text)
            score = sum(1 for t in tokens if t in terms) / (len(tokens) or 1)
            if score > 0:
                hits.append(SearchHit(id=r.id, score=score, payload=r.payload))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:limit]

    async def delete(self, *, tenant_id: UUID, ids: Sequence[UUID]) -> None:
        for id_ in ids:
            record = self._records.get(id_)
            if record is not None and record.tenant_id == tenant_id:
                del self._records[id_]


class EchoLLM:
    """Returns a predictable answer that includes the prompt, for pipeline tests."""

    def __init__(self, model: str = "fake-echo") -> None:
        self._model = model

    @property
    def model(self) -> str:
        return self._model

    async def generate(self, prompt: str, *, system: str | None = None) -> LLMResult:
        text = f"ECHO: {prompt}"
        return LLMResult(
            text=text,
            model=self._model,
            usage=LLMUsage(input_tokens=len(_tokens(prompt)), output_tokens=len(_tokens(text))),
        )

    async def stream(self, prompt: str, *, system: str | None = None) -> AsyncIterator[str]:
        result = await self.generate(prompt, system=system)
        for word in result.text.split(" "):
            yield word + " "


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0
