"""Document service: the business logic layer for ingestion.

Coordinates:
    1. Duplicate detection (by content hash within a tenant)
    2. Storage of the original file
    3. Status transitions
    4. Parsing and chunking (called from the Dramatiq worker)
    5. Database persistence of chunks

Phase 2 will extend this with an ``embed_and_index`` method without changing
existing methods.
"""
# Batch size for flushing chunks — keeps ORM identity-map pressure bounded.
_CHUNK_FLUSH_BATCH = 500

# Maximum upload size (100 MB).  Reject larger files early to avoid OOM.
MAX_UPLOAD_BYTES = 100 * 1024 * 1024

import hashlib
import re
import uuid
from collections.abc import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from advance_rag.core.errors import ConflictError, InvalidInputError, NotFoundError
from advance_rag.core.logging import get_logger
from advance_rag.documents.chunker import ChunkResult, ChunkerConfig, chunk_document
from advance_rag.documents.models import Chunk, Document, DocumentVersion
from advance_rag.documents.parsers.registry import get_parser
from advance_rag.documents.status import DocumentStatus, can_transition
from advance_rag.infra.ports import ObjectStorage

log = get_logger(__name__)


def compute_content_hash(data: bytes) -> str:
    """SHA-256 hex digest of file contents."""
    return hashlib.sha256(data).hexdigest()


async def create_document(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    title: str,
    filename: str,
    mime_type: str,
    data: bytes,
    storage: ObjectStorage,
    source: str | None = None,
) -> Document:
    """Upload a new document: store the file, create DB records, return the Document.

    Raises ``ConflictError`` if the same content hash already exists for this tenant.
    Raises ``InvalidInputError`` if the MIME type is not supported.
    """
    # Validate MIME type
    parser = get_parser(mime_type)
    if parser is None:
        raise InvalidInputError(
            f"Unsupported file type: {mime_type}",
            details={"mime_type": mime_type},
        )

    content_hash = compute_content_hash(data)

    # Duplicate check within tenant
    existing = await session.execute(
        select(Document).where(
            Document.tenant_id == tenant_id,
            Document.content_hash == content_hash,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ConflictError(
            "A document with identical content already exists in this tenant.",
            details={"content_hash": content_hash},
        )

    doc_id = uuid.uuid4()
    storage_key = f"{tenant_id}/documents/{doc_id}/{filename}"
    storage_uri = await storage.put(storage_key, data, content_type=mime_type)

    doc = Document(
        id=doc_id,
        tenant_id=tenant_id,
        title=title,
        source=source,
        mime_type=mime_type,
        content_hash=content_hash,
        status=DocumentStatus.PENDING,
    )
    version = DocumentVersion(
        document_id=doc_id,
        version=1,
        storage_uri=storage_uri,
    )

    session.add(doc)
    session.add(version)
    await session.flush()  # assign IDs

    log.info(
        "document_created",
        document_id=str(doc_id),
        tenant_id=str(tenant_id),
        content_hash=content_hash,
    )
    return doc


async def transition_status(
    session: AsyncSession,
    doc: Document,
    new_status: DocumentStatus,
    *,
    error: str | None = None,
) -> None:
    """Transition a document to a new status, enforcing the state machine."""
    current = DocumentStatus(doc.status)
    if not can_transition(current, new_status):
        raise InvalidInputError(
            f"Invalid status transition: {current} → {new_status}",
            details={"current": current, "target": new_status},
        )
    doc.status = new_status
    doc.error = error
    await session.flush()
    log.info(
        "document_status_changed",
        document_id=str(doc.id),
        from_status=current,
        to_status=new_status,
    )


async def parse_and_chunk(
    session: AsyncSession,
    *,
    document_id: uuid.UUID,
    storage: ObjectStorage,
    chunker_config: ChunkerConfig | None = None,
) -> list[ChunkResult]:
    """Parse a document and create chunks.  Called by the Dramatiq worker.

    Transitions: PENDING → PARSING → CHUNKED (or FAILED on error).
    """
    doc = await session.get(Document, document_id)
    if doc is None:
        raise NotFoundError(f"Document {document_id} not found")

    try:
        await transition_status(session, doc, DocumentStatus.PARSING)

        # Get the latest version
        result = await session.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version.desc())
            .limit(1)
        )
        version = result.scalar_one()

        # Retrieve file from storage
        storage_key = _uri_to_key(version.storage_uri)
        data = await storage.get(storage_key)

        # Parse
        parser = get_parser(doc.mime_type)
        if parser is None:
            raise InvalidInputError(f"No parser for {doc.mime_type}")
        parsed = parser.parse(data, filename=doc.title)

        # Chunk
        chunk_results = chunk_document(parsed, config=chunker_config)

        # Persist chunks in batches to avoid ORM identity-map bloat
        batch: list[Chunk] = []
        for chunk_result in chunk_results:
            batch.append(
                Chunk(
                    tenant_id=doc.tenant_id,
                    document_version_id=version.id,
                    ordinal=chunk_result.ordinal,
                    text=chunk_result.text,
                    token_count=chunk_result.token_count,
                    page=chunk_result.page,
                    section=chunk_result.section,
                    heading_path=chunk_result.heading_path,
                    metadata_=chunk_result.metadata,
                )
            )
            if len(batch) >= _CHUNK_FLUSH_BATCH:
                session.add_all(batch)
                await session.flush()
                batch.clear()
        if batch:
            session.add_all(batch)

        await transition_status(session, doc, DocumentStatus.CHUNKED)
        await session.flush()

        log.info(
            "document_parsed_and_chunked",
            document_id=str(document_id),
            chunk_count=len(chunk_results),
        )
        return chunk_results

    except Exception as exc:
        # Rollback status to FAILED
        try:
            doc.status = DocumentStatus.FAILED
            doc.error = f"{type(exc).__name__}: {exc}"
            await session.flush()
        except Exception:
            log.exception("failed_to_set_error_status", document_id=str(document_id))
        raise


# Pre-compiled regex for extracting the storage key from local file:// URIs.
_LOCAL_KEY_RE = re.compile(r"([0-9a-f-]{36}/documents/.+)$")


def _uri_to_key(uri: str) -> str:
    """Extract the storage key from a URI.

    Handles:
        file:///path/to/root/tenant/doc/file  → tenant/doc/file (strip root)
        memory://tenant/doc/file              → tenant/doc/file
        gs://bucket/tenant/doc/file           → tenant/doc/file
    """
    if uri.startswith("memory://"):
        return uri[len("memory://"):]
    if uri.startswith("gs://"):
        # gs://bucket/key → key
        parts = uri[len("gs://"):].split("/", 1)
        return parts[1] if len(parts) > 1 else ""
    if uri.startswith("file://"):
        # For local storage, the key is embedded in the path.
        path = uri[len("file://"):]
        match = _LOCAL_KEY_RE.search(path)
        if match:
            return match.group(1)
    return uri


async def get_document(
    session: AsyncSession,
    *,
    document_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> Document:
    """Get a single document by ID, scoped to tenant."""
    doc = await session.get(Document, document_id)
    if doc is None or doc.tenant_id != tenant_id:
        raise NotFoundError(f"Document {document_id} not found")
    return doc


async def list_documents(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
) -> tuple[Sequence[Document], int]:
    """List documents for a tenant with pagination.  Returns (docs, total_count)."""
    count_stmt = select(func.count(Document.id)).where(Document.tenant_id == tenant_id)
    total = (await session.execute(count_stmt)).scalar_one()

    stmt = (
        select(Document)
        .where(Document.tenant_id == tenant_id)
        .order_by(Document.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    docs = result.scalars().all()
    return docs, total


async def get_chunk_count(
    session: AsyncSession,
    *,
    document_id: uuid.UUID,
) -> int:
    """Return the total number of chunks for a document (across all versions)."""
    stmt = (
        select(func.count(Chunk.id))
        .join(DocumentVersion, Chunk.document_version_id == DocumentVersion.id)
        .where(DocumentVersion.document_id == document_id)
    )
    return (await session.execute(stmt)).scalar_one()
