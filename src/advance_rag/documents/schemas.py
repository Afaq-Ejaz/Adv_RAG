"""Pydantic schemas for document API endpoints.

Request and response models are defined here (not in the route module) so that
the service layer and tests can import them without pulling in FastAPI.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# --- Responses ---

class DocumentUploadResponse(BaseModel):
    """Returned after POST /v1/documents (202 Accepted)."""

    id: uuid.UUID
    title: str
    mime_type: str
    status: str
    created_at: datetime


class DocumentSummary(BaseModel):
    """Slim model for list views."""

    id: uuid.UUID
    title: str
    mime_type: str
    status: str
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    """Paginated list of documents."""

    items: list[DocumentSummary]
    total: int
    limit: int
    offset: int


class DocumentDetailResponse(BaseModel):
    """Full detail for GET /v1/documents/{id}."""

    id: uuid.UUID
    title: str
    source: str | None
    mime_type: str
    content_hash: str
    status: str
    error: str | None
    acl: dict
    chunk_count: int
    created_at: datetime
    updated_at: datetime
