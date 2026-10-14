"""ORM models for the documents domain.

Tables:
    documents          — uploaded file metadata and processing status
    document_versions  — storage URIs for each version of a document
    chunks             — structured text fragments extracted from documents

Design notes for Phase 2 forward-compatibility:
    - ``chunks`` includes nullable ``embedding_model`` and ``embedding_dim``
      columns that Phase 2 will populate once embeddings are generated.
    - ``chunks.id`` is a UUID that will become the Qdrant point ID, making
      re-indexing idempotent.
    - ``document_versions.version`` is always 1 in this phase; Phase 7 extends
      the versioning system.
"""

import uuid
from typing import Any

from sqlalchemy import ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from advance_rag.core.db import Base, TimestampMixin, UUIDPrimaryKeyMixin
from advance_rag.documents.status import DocumentStatus


class Document(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_tenant_id_content_hash", "tenant_id", "content_hash"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(512))
    source: Mapped[str | None] = mapped_column(String(1024))
    mime_type: Mapped[str] = mapped_column(String(128))
    content_hash: Mapped[str] = mapped_column(String(64))  # SHA-256 hex
    status: Mapped[str] = mapped_column(
        String(32), server_default=text(f"'{DocumentStatus.PENDING}'")
    )
    error: Mapped[str | None] = mapped_column(Text)
    acl: Mapped[dict[str, Any]] = mapped_column(
        JSONB, server_default=text("'{\"public\": true}'::jsonb")
    )

    # relationships
    versions: Mapped[list["DocumentVersion"]] = relationship(
        back_populates="document", cascade="all, delete-orphan", order_by="DocumentVersion.version"
    )


class DocumentVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "document_versions"

    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1, server_default=text("1"))
    storage_uri: Mapped[str] = mapped_column(String(1024))

    # relationships
    document: Mapped[Document] = relationship(back_populates="versions")
    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document_version", cascade="all, delete-orphan", order_by="Chunk.ordinal"
    )


class Chunk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "chunks"
    __table_args__ = (
        Index("ix_chunks_tenant_id", "tenant_id"),
        Index("ix_chunks_document_version_id", "document_version_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
    )
    document_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("document_versions.id", ondelete="CASCADE"),
    )
    ordinal: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    token_count: Mapped[int] = mapped_column(Integer)
    page: Mapped[int | None] = mapped_column(Integer)
    section: Mapped[str | None] = mapped_column(String(512))
    heading_path: Mapped[str | None] = mapped_column(String(1024))
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, server_default=text("'{}'::jsonb")
    )

    # Phase 2 will populate these:
    embedding_model: Mapped[str | None] = mapped_column(String(128))
    embedding_dim: Mapped[int | None] = mapped_column(Integer)

    # relationships
    document_version: Mapped[DocumentVersion] = relationship(back_populates="chunks")
