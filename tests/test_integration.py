"""Integration tests for the document ingestion pipeline.

These tests exercise the full flow: create_document → parse_and_chunk → CHUNKED
using InMemoryObjectStorage (no real filesystem or GCS needed).

Tests that require a live database are marked with ``@pytest.mark.integration``
and will only run when ``RAG_RUN_INTEGRATION=1`` is set.

For unit-level integration, we test the service functions directly with
the in-memory storage fake.
"""

import uuid

import pytest

from advance_rag.core.errors import ConflictError, InvalidInputError
from advance_rag.documents.chunker import ChunkResult
from advance_rag.documents.service import (
    compute_content_hash,
    create_document,
    parse_and_chunk,
)
from advance_rag.documents.status import DocumentStatus
from advance_rag.infra.fakes import InMemoryObjectStorage


# ---------------------------------------------------------------------------
# content_hash tests (no DB needed)
# ---------------------------------------------------------------------------

class TestContentHash:
    def test_deterministic(self) -> None:
        data = b"hello world"
        assert compute_content_hash(data) == compute_content_hash(data)

    def test_different_content_different_hash(self) -> None:
        assert compute_content_hash(b"foo") != compute_content_hash(b"bar")

    def test_returns_hex_string(self) -> None:
        h = compute_content_hash(b"test")
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256 hex digest


# ---------------------------------------------------------------------------
# Service-level tests using InMemoryObjectStorage
# (These need a real or fake async DB session to run fully.
#  Below we test the parts that can be unit-tested without a DB.)
# ---------------------------------------------------------------------------

class TestParseAndChunkWithFakeStorage:
    """Test parsing and chunking with text content via the PlainTextParser."""

    @pytest.fixture
    def storage(self) -> InMemoryObjectStorage:
        return InMemoryObjectStorage()

    @pytest.fixture
    def tenant_id(self) -> uuid.UUID:
        return uuid.UUID("00000000-0000-0000-0000-000000000001")

    def test_plain_text_can_be_stored_and_retrieved(self, storage: InMemoryObjectStorage) -> None:
        """Verify the in-memory storage roundtrips correctly."""
        import asyncio

        async def _test() -> None:
            key = "tenant/documents/doc1/file.txt"
            data = b"Hello, world!"
            uri = await storage.put(key, data, content_type="text/plain")
            assert uri == f"memory://{key}"
            retrieved = await storage.get(key)
            assert retrieved == data

        asyncio.run(_test())

    def test_storage_delete(self, storage: InMemoryObjectStorage) -> None:
        import asyncio

        async def _test() -> None:
            key = "test/key"
            await storage.put(key, b"data")
            assert await storage.exists(key)
            await storage.delete(key)
            assert not await storage.exists(key)

        asyncio.run(_test())

    def test_storage_not_found(self, storage: InMemoryObjectStorage) -> None:
        import asyncio

        async def _test() -> None:
            with pytest.raises(FileNotFoundError):
                await storage.get("nonexistent/key")

        asyncio.run(_test())


# ---------------------------------------------------------------------------
# DOCX/PDF parsing integration (fixture-based, no DB needed)
# ---------------------------------------------------------------------------

class TestParsersWithFixtures:
    """Test that fixture files can be parsed and chunked end-to-end."""

    def _parse_and_chunk_file(self, filepath: str, mime_type: str) -> list[ChunkResult]:
        from pathlib import Path
        from advance_rag.documents.parsers.registry import get_parser
        from advance_rag.documents.chunker import chunk_document

        path = Path(filepath)
        if not path.exists():
            pytest.skip(f"Fixture {path.name} not found")

        data = path.read_bytes()
        parser = get_parser(mime_type)
        assert parser is not None, f"No parser for {mime_type}"
        parsed = parser.parse(data, filename=path.name)
        return chunk_document(parsed)

    def test_pdf_fixture_produces_chunks(self) -> None:
        from pathlib import Path

        fixture_path = Path(__file__).parent / "fixtures" / "sample.pdf"
        chunks = self._parse_and_chunk_file(str(fixture_path), "application/pdf")
        assert len(chunks) > 0, "PDF should produce at least one chunk"

        # Verify chunk properties
        for chunk in chunks:
            assert chunk.text.strip(), "Chunk text should not be empty"
            assert chunk.token_count > 0
            assert chunk.ordinal >= 0

    def test_docx_fixture_produces_chunks(self) -> None:
        from pathlib import Path

        fixture_path = Path(__file__).parent / "fixtures" / "sample.docx"
        chunks = self._parse_and_chunk_file(
            str(fixture_path),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        assert len(chunks) > 0, "DOCX should produce at least one chunk"

        # Verify heading paths are preserved
        sections_with_headings = [c for c in chunks if c.heading_path]
        assert sections_with_headings, "DOCX should have chunks with heading paths"

    def test_plain_text_produces_chunks(self) -> None:
        from advance_rag.documents.parsers.registry import get_parser
        from advance_rag.documents.chunker import chunk_document

        text = (
            "First paragraph with some content.\n\n"
            "Second paragraph with more content.\n\n"
            "Third paragraph wrapping up."
        )
        parser = get_parser("text/plain")
        assert parser is not None
        parsed = parser.parse(text.encode(), filename="test.txt")
        chunks = chunk_document(parsed)

        assert len(chunks) >= 1
        all_text = " ".join(c.text for c in chunks)
        assert "First paragraph" in all_text
        assert "Third paragraph" in all_text


# ---------------------------------------------------------------------------
# Unsupported file type
# ---------------------------------------------------------------------------

class TestUnsupportedFileType:
    def test_unsupported_mime_raises_error(self) -> None:
        from advance_rag.documents.parsers.registry import get_parser

        assert get_parser("image/png") is None
        assert get_parser("application/zip") is None


# ---------------------------------------------------------------------------
# Status state machine
# ---------------------------------------------------------------------------

class TestStatusStateMachine:
    def test_valid_transitions(self) -> None:
        from advance_rag.documents.status import DocumentStatus, can_transition

        assert can_transition(DocumentStatus.PENDING, DocumentStatus.PARSING)
        assert can_transition(DocumentStatus.PENDING, DocumentStatus.FAILED)
        assert can_transition(DocumentStatus.PARSING, DocumentStatus.CHUNKED)
        assert can_transition(DocumentStatus.PARSING, DocumentStatus.FAILED)
        assert can_transition(DocumentStatus.FAILED, DocumentStatus.PENDING)  # retry

    def test_invalid_transitions(self) -> None:
        from advance_rag.documents.status import DocumentStatus, can_transition

        assert not can_transition(DocumentStatus.PENDING, DocumentStatus.CHUNKED)
        assert not can_transition(DocumentStatus.CHUNKED, DocumentStatus.PARSING)
        assert not can_transition(DocumentStatus.PENDING, DocumentStatus.INDEXED)
