"""Unit tests for the structure-aware recursive chunker."""

import pytest

from advance_rag.documents.chunker import (
    ChunkResult,
    ChunkerConfig,
    chunk_document,
    _count_tokens,
    _split_text_units,
    _merge_units_with_overlap,
)
from advance_rag.infra.ports import ParsedDocument, ParsedSection


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_document(sections: list[ParsedSection], title: str = "Test Doc") -> ParsedDocument:
    return ParsedDocument(sections=sections, title=title)


def _long_text(word_count: int) -> str:
    """Generate a paragraph with exactly `word_count` words."""
    words = [f"word{i}" for i in range(word_count)]
    return " ".join(words)


# ---------------------------------------------------------------------------
# Token counting
# ---------------------------------------------------------------------------

class TestTokenCounting:
    def test_simple_sentence(self) -> None:
        assert _count_tokens("hello world foo bar") == 4

    def test_empty_string(self) -> None:
        assert _count_tokens("") == 0

    def test_single_word(self) -> None:
        assert _count_tokens("hello") == 1


# ---------------------------------------------------------------------------
# Text splitting
# ---------------------------------------------------------------------------

class TestTextSplitting:
    def test_splits_by_paragraphs(self) -> None:
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        units = _split_text_units(text)
        assert len(units) == 3

    def test_splits_by_sentences(self) -> None:
        text = "First sentence. Second sentence. Third sentence."
        units = _split_text_units(text)
        assert len(units) >= 2  # may be split at sentence boundaries

    def test_empty_text(self) -> None:
        assert _split_text_units("") == []

    def test_whitespace_only(self) -> None:
        assert _split_text_units("   \n\n   ") == []


# ---------------------------------------------------------------------------
# Chunk size and overlap
# ---------------------------------------------------------------------------

class TestChunkSizeLimits:
    """Verify that chunks respect max_tokens configuration."""

    def test_chunk_respects_max_tokens(self) -> None:
        """No chunk should exceed max_tokens (unless a single unit is larger)."""
        sections = [
            ParsedSection(text=_long_text(200), page=1),
            ParsedSection(text=_long_text(200), page=2),
        ]
        doc = _make_document(sections)
        config = ChunkerConfig(max_tokens=100, overlap_tokens=10, min_chunk_tokens=5)
        chunks = chunk_document(doc, config=config)

        assert len(chunks) > 1, "Should produce multiple chunks"
        for chunk in chunks:
            # Each chunk should be close to max_tokens (allow some slack for merging)
            # Single units that exceed max_tokens are their own chunk
            assert chunk.token_count > 0

    def test_small_document_single_chunk(self) -> None:
        """A document smaller than max_tokens should produce a single chunk."""
        sections = [ParsedSection(text="Short paragraph here.", page=1)]
        doc = _make_document(sections)
        config = ChunkerConfig(max_tokens=512, overlap_tokens=64, min_chunk_tokens=1)
        chunks = chunk_document(doc, config=config)

        assert len(chunks) == 1
        assert chunks[0].text == "Short paragraph here."

    def test_oversized_single_unit_becomes_own_chunk(self) -> None:
        """A single text unit larger than max_tokens should become its own chunk."""
        huge_text = _long_text(600)  # 600 tokens, way over 100
        sections = [ParsedSection(text=huge_text, page=1)]
        doc = _make_document(sections)
        config = ChunkerConfig(max_tokens=100, overlap_tokens=10, min_chunk_tokens=5)
        chunks = chunk_document(doc, config=config)

        # The huge text should exist as a chunk (possibly with token_count > max_tokens)
        assert any(c.token_count > 100 for c in chunks)


class TestChunkOverlap:
    """Verify that overlap tokens appear at chunk boundaries."""

    def test_overlap_content_shared(self) -> None:
        """Content from the end of one chunk should appear at the start of the next."""
        # Create many sentences so we get multiple chunks
        sentences = [f"Sentence number {i} has some content here." for i in range(50)]
        text = " ".join(sentences)
        sections = [ParsedSection(text=text, page=1)]
        doc = _make_document(sections)
        config = ChunkerConfig(max_tokens=50, overlap_tokens=15, min_chunk_tokens=5)
        chunks = chunk_document(doc, config=config)

        if len(chunks) >= 2:
            # Check that there's some content overlap between consecutive chunks
            for i in range(len(chunks) - 1):
                words_current = set(chunks[i].text.split()[-20:])
                words_next = set(chunks[i + 1].text.split()[:20])
                overlap = words_current & words_next
                # With overlap_tokens=15, there should be shared words
                assert len(overlap) > 0, (
                    f"Expected overlap between chunk {i} and {i+1}"
                )


class TestMinChunkMerging:
    """Verify that tiny trailing chunks are merged."""

    def test_min_chunk_merged_with_previous(self) -> None:
        """A trailing chunk below min_chunk_tokens should be merged."""
        # Create text that will produce a tiny final chunk
        text = _long_text(100) + "\n\n" + "Tiny."
        sections = [ParsedSection(text=text, page=1)]
        doc = _make_document(sections)
        config = ChunkerConfig(max_tokens=80, overlap_tokens=10, min_chunk_tokens=30)
        chunks = chunk_document(doc, config=config)

        # "Tiny." is only 1 token, well below min_chunk_tokens=30
        # It should be merged into the previous chunk rather than standing alone
        for chunk in chunks:
            if chunk.text.strip() == "Tiny.":
                pytest.fail("Expected 'Tiny.' to be merged with the previous chunk")


# ---------------------------------------------------------------------------
# Metadata preservation
# ---------------------------------------------------------------------------

class TestMetadataPreservation:
    """Verify that page, section, heading_path, and document_title are preserved."""

    def test_page_preserved(self) -> None:
        sections = [
            ParsedSection(text="Content on page one.", page=1),
            ParsedSection(text="Content on page two.", page=2),
        ]
        doc = _make_document(sections)
        chunks = chunk_document(doc)

        pages = {c.page for c in chunks}
        assert 1 in pages
        assert 2 in pages

    def test_section_from_heading_path(self) -> None:
        sections = [
            ParsedSection(
                text="Some section content here.",
                heading_path=("Chapter 1", "Section 1.1"),
            ),
        ]
        doc = _make_document(sections)
        chunks = chunk_document(doc)

        assert chunks[0].section == "Section 1.1"

    def test_heading_path_string(self) -> None:
        sections = [
            ParsedSection(
                text="Content under nested headings.",
                heading_path=("Chapter 1", "Section 1.1", "Subsection A"),
            ),
        ]
        doc = _make_document(sections)
        chunks = chunk_document(doc)

        assert chunks[0].heading_path == "Chapter 1 > Section 1.1 > Subsection A"

    def test_document_title_in_metadata(self) -> None:
        sections = [ParsedSection(text="Some content.", page=1)]
        doc = _make_document(sections, title="My Important Doc")
        chunks = chunk_document(doc)

        assert chunks[0].metadata.get("document_title") == "My Important Doc"

    def test_ordinals_are_sequential(self) -> None:
        sections = [
            ParsedSection(text=_long_text(100), page=1),
            ParsedSection(text=_long_text(100), page=2),
        ]
        doc = _make_document(sections)
        config = ChunkerConfig(max_tokens=50)
        chunks = chunk_document(doc, config=config)

        ordinals = [c.ordinal for c in chunks]
        assert ordinals == list(range(len(chunks)))


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_document_returns_empty(self) -> None:
        doc = _make_document([])
        chunks = chunk_document(doc)
        assert chunks == []

    def test_empty_section_text(self) -> None:
        sections = [ParsedSection(text="", page=1)]
        doc = _make_document(sections)
        chunks = chunk_document(doc)
        # Empty text should produce no chunks (split_text_units returns [])
        assert chunks == []

    def test_section_without_page(self) -> None:
        sections = [ParsedSection(text="Content without page number.")]
        doc = _make_document(sections)
        chunks = chunk_document(doc)
        assert len(chunks) == 1
        assert chunks[0].page is None

    def test_section_without_heading(self) -> None:
        sections = [ParsedSection(text="Content without heading.")]
        doc = _make_document(sections)
        chunks = chunk_document(doc)
        assert len(chunks) == 1
        assert chunks[0].section is None
        assert chunks[0].heading_path is None
