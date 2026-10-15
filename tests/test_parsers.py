"""Unit tests for PDF and DOCX parsers."""

from pathlib import Path

import pytest

from advance_rag.documents.parsers.pdf_parser import PDFParser
from advance_rag.documents.parsers.docx_parser import DOCXParser
from advance_rag.documents.parsers.registry import get_parser, supported_mime_types
from advance_rag.infra.ports import ParsedDocument

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# PDF Parser
# ---------------------------------------------------------------------------

class TestPDFParser:
    """Tests for the pdfplumber-based PDF parser."""

    parser = PDFParser()

    @pytest.fixture
    def sample_pdf(self) -> bytes:
        path = FIXTURES_DIR / "sample.pdf"
        if not path.exists():
            pytest.skip("sample.pdf fixture not found — run generate_fixtures.py first")
        return path.read_bytes()

    def test_supports_pdf_mime(self) -> None:
        assert self.parser.supports("application/pdf")

    def test_rejects_non_pdf_mime(self) -> None:
        assert not self.parser.supports("text/plain")
        assert not self.parser.supports("application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    def test_parse_returns_parsed_document(self, sample_pdf: bytes) -> None:
        result = self.parser.parse(sample_pdf, filename="test.pdf")
        assert isinstance(result, ParsedDocument)
        assert result.sections  # at least one section

    def test_extracts_pages(self, sample_pdf: bytes) -> None:
        result = self.parser.parse(sample_pdf, filename="test.pdf")
        pages = [s.page for s in result.sections]
        # Should have sections from at least 2 pages
        assert len(set(pages)) >= 2, f"Expected multiple pages, got {pages}"

    def test_page_numbers_are_sequential(self, sample_pdf: bytes) -> None:
        result = self.parser.parse(sample_pdf, filename="test.pdf")
        pages = [s.page for s in result.sections if s.page is not None]
        for i in range(1, len(pages)):
            assert pages[i] >= pages[i - 1], "Page numbers should be non-decreasing"

    def test_extracts_tables_as_text(self, sample_pdf: bytes) -> None:
        result = self.parser.parse(sample_pdf, filename="test.pdf")
        all_text = " ".join(s.text for s in result.sections)
        # The fixture has a table with "Metric | Value | Status"
        assert "Metric" in all_text or "Documents Processed" in all_text, (
            "Expected table content in parsed output"
        )

    def test_metadata_includes_parser_name(self, sample_pdf: bytes) -> None:
        result = self.parser.parse(sample_pdf, filename="test.pdf")
        assert result.metadata.get("parser") == "pdfplumber"

    def test_title_falls_back_to_filename(self, sample_pdf: bytes) -> None:
        result = self.parser.parse(sample_pdf, filename="my_doc.pdf")
        assert result.title is not None


# ---------------------------------------------------------------------------
# DOCX Parser
# ---------------------------------------------------------------------------

class TestDOCXParser:
    """Tests for the python-docx based DOCX parser."""

    parser = DOCXParser()

    @pytest.fixture
    def sample_docx(self) -> bytes:
        path = FIXTURES_DIR / "sample.docx"
        if not path.exists():
            pytest.skip("sample.docx fixture not found — run generate_fixtures.py first")
        return path.read_bytes()

    def test_supports_docx_mime(self) -> None:
        assert self.parser.supports(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    def test_rejects_non_docx_mime(self) -> None:
        assert not self.parser.supports("application/pdf")
        assert not self.parser.supports("text/plain")

    def test_parse_returns_parsed_document(self, sample_docx: bytes) -> None:
        result = self.parser.parse(sample_docx, filename="test.docx")
        assert isinstance(result, ParsedDocument)
        assert result.sections

    def test_extracts_heading_hierarchy(self, sample_docx: bytes) -> None:
        result = self.parser.parse(sample_docx, filename="test.docx")
        heading_paths = [s.heading_path for s in result.sections if s.heading_path]
        assert heading_paths, "Expected at least one section with heading_path"

        # Should have both level-1 and level-2 headings
        max_depth = max(len(hp) for hp in heading_paths)
        assert max_depth >= 2, f"Expected heading depth >= 2, got {max_depth}"

    def test_heading_path_contains_parent_headings(self, sample_docx: bytes) -> None:
        result = self.parser.parse(sample_docx, filename="test.docx")
        # Find a section under "Introduction" > "Background"
        deep_sections = [s for s in result.sections if len(s.heading_path) >= 2]
        assert deep_sections, "Expected sections with nested heading paths"
        # The parent heading should be included in the path
        for section in deep_sections:
            assert len(section.heading_path) >= 2

    def test_extracts_tables(self, sample_docx: bytes) -> None:
        result = self.parser.parse(sample_docx, filename="test.docx")
        all_text = " ".join(s.text for s in result.sections)
        assert "Metric" in all_text or "Documents Processed" in all_text, (
            "Expected table content in parsed output"
        )

    def test_metadata_includes_parser_name(self, sample_docx: bytes) -> None:
        result = self.parser.parse(sample_docx, filename="test.docx")
        assert result.metadata.get("parser") == "python-docx"

    def test_title_from_core_properties(self, sample_docx: bytes) -> None:
        result = self.parser.parse(sample_docx, filename="test.docx")
        # The fixture sets core_properties.title = "Sample DOCX for Testing"
        assert result.title == "Sample DOCX for Testing"


# ---------------------------------------------------------------------------
# Parser Registry
# ---------------------------------------------------------------------------

class TestParserRegistry:
    """Tests for the parser registry (get_parser / supported_mime_types)."""

    def test_pdf_mime_resolves(self) -> None:
        parser = get_parser("application/pdf")
        assert parser is not None
        assert isinstance(parser, PDFParser)

    def test_docx_mime_resolves(self) -> None:
        parser = get_parser(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        assert parser is not None
        assert isinstance(parser, DOCXParser)

    def test_text_mime_resolves_to_fallback(self) -> None:
        parser = get_parser("text/plain")
        assert parser is not None

    def test_unsupported_mime_returns_none(self) -> None:
        assert get_parser("image/png") is None
        assert get_parser("video/mp4") is None
        assert get_parser("application/json") is None

    def test_supported_mime_types_list(self) -> None:
        types = supported_mime_types()
        assert "application/pdf" in types
        assert "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in types
        assert "text/plain" in types
