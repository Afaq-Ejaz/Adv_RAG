"""Document endpoints: upload, list, detail.

POST /v1/documents      Multipart upload → store → PENDING → enqueue Dramatiq job
GET  /v1/documents      Paginated list of documents for the current tenant
GET  /v1/documents/{id} Document detail with chunk count
"""

import uuid

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from advance_rag.api.deps import get_context, get_resources, get_session
from advance_rag.core.context import RequestContext
from advance_rag.documents import service as doc_service
from advance_rag.documents.service import MAX_UPLOAD_BYTES
from advance_rag.documents.schemas import (
    DocumentDetailResponse,
    DocumentListResponse,
    DocumentSummary,
    DocumentUploadResponse,
)
from advance_rag.infra.resources import Resources
from advance_rag.workers.broker import process_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=202,
    summary="Upload a document for processing",
)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    source: str | None = Form(None),
    session: AsyncSession = Depends(get_session),
    ctx: RequestContext = Depends(get_context),
    resources: Resources = Depends(get_resources),
) -> JSONResponse:
    """Accept a multipart file upload, store it, and queue it for async processing.

    Returns 202 Accepted because the actual parsing/chunking happens in a
    background Dramatiq worker.
    """
    data = await file.read()

    # Reject oversized uploads before doing any further work
    if len(data) > MAX_UPLOAD_BYTES:
        return JSONResponse(
            status_code=413,
            content={
                "detail": f"File too large ({len(data)} bytes). "
                           f"Maximum allowed is {MAX_UPLOAD_BYTES} bytes.",
            },
        )

    mime_type = file.content_type or "application/octet-stream"
    filename = file.filename or "untitled"
    doc_title = title or filename

    storage = resources.storage
    assert storage is not None, "Object storage not configured"

    doc = await doc_service.create_document(
        session,
        tenant_id=ctx.tenant_id,
        title=doc_title,
        filename=filename,
        mime_type=mime_type,
        data=data,
        storage=storage,
        source=source,
    )

    # Enqueue async processing via Dramatiq
    process_document.send(str(doc.id))

    response = DocumentUploadResponse(
        id=doc.id,
        title=doc.title,
        mime_type=doc.mime_type,
        status=doc.status,
        created_at=doc.created_at,
    )
    return JSONResponse(status_code=202, content=response.model_dump(mode="json"))


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List documents for the current tenant",
)
async def list_documents(
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    ctx: RequestContext = Depends(get_context),
) -> DocumentListResponse:
    """Return a paginated list of documents belonging to the current tenant."""
    docs, total = await doc_service.list_documents(
        session,
        tenant_id=ctx.tenant_id,
        limit=min(limit, 100),  # cap at 100
        offset=max(offset, 0),
    )

    return DocumentListResponse(
        items=[
            DocumentSummary(
                id=doc.id,
                title=doc.title,
                mime_type=doc.mime_type,
                status=doc.status,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
            for doc in docs
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    summary="Get document detail with chunk count",
)
async def get_document(
    document_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    ctx: RequestContext = Depends(get_context),
) -> DocumentDetailResponse:
    """Return full document details including processing status and chunk count."""
    doc = await doc_service.get_document(
        session,
        document_id=document_id,
        tenant_id=ctx.tenant_id,
    )
    chunk_count = await doc_service.get_chunk_count(session, document_id=document_id)

    return DocumentDetailResponse(
        id=doc.id,
        title=doc.title,
        source=doc.source,
        mime_type=doc.mime_type,
        content_hash=doc.content_hash,
        status=doc.status,
        error=doc.error,
        acl=doc.acl,
        chunk_count=chunk_count,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )
