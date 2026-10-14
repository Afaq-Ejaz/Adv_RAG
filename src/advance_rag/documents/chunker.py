"""Structure-aware recursive chunker with token-based sizing.

Strategy:
    1. Each ``ParsedSection`` is split by headings (if the section text contains
       markdown-style headings, e.g. ``## Subsection``).
    2. Then by paragraphs (double newline).
    3. Then by sentences (``re``-based sentence splitter).

Chunks respect a configurable maximum token count with overlap.  Page, section,
and heading-path metadata from the ``ParsedSection`` are preserved on each chunk.

Token counting uses a simple whitespace-split approximation.  For production
accuracy, swap in ``tiktoken`` or a model-specific tokenizer.

Phase 2 notes:
    - Chunk IDs are generated deterministically from (document_version_id, ordinal)
      so that re-indexing in Phase 2 is idempotent.
"""

import re
import uuid
from collections.abc import Sequence
from dataclasses import dataclass, field

from advance_rag.infra.ports import ParsedDocument, ParsedSection

# Simple sentence boundary regex.  Not perfect, but good enough for chunking.
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class ChunkResult:
    """A single chunk produced by the chunker."""

    text: str
    token_count: int
    ordinal: int
    page: int | None = None
    section: str | None = None
    heading_path: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ChunkerConfig:
    """Chunker configuration."""

    max_tokens: int = 512
    overlap_tokens: int = 64
    min_chunk_tokens: int = 30


def _count_tokens(text: str) -> int:
    """Approximate token count via whitespace splitting."""
    return len(text.split())


def _split_text_units(text: str) -> list[str]:
    """Split text into atomic units: first by paragraphs, then sentences."""
    paragraphs = re.split(r"\n\s*\n", text)
    units: list[str] = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        sentences = _SENTENCE_RE.split(para)
        units.extend(s.strip() for s in sentences if s.strip())
    return units


def _merge_units_with_overlap(
    units: list[str],
    max_tokens: int,
    overlap_tokens: int,
    min_chunk_tokens: int,
) -> list[str]:
    """Merge text units into chunks respecting token limits and overlap."""
    if not units:
        return []

    chunks: list[str] = []
    current_parts: list[str] = []
    current_tokens = 0

    for unit in units:
        unit_tokens = _count_tokens(unit)

        # If this single unit exceeds max_tokens, it becomes its own chunk
        if unit_tokens > max_tokens:
            # Flush current
            if current_parts:
                chunks.append("\n\n".join(current_parts))
            chunks.append(unit)
            current_parts = []
            current_tokens = 0
            continue

        if current_tokens + unit_tokens > max_tokens and current_parts:
            # Flush the current chunk
            chunks.append("\n\n".join(current_parts))

            # Build overlap: take units from the end of current_parts
            overlap_parts: list[str] = []
            overlap_count = 0
            for part in reversed(current_parts):
                part_tokens = _count_tokens(part)
                if overlap_count + part_tokens > overlap_tokens:
                    break
                overlap_parts.insert(0, part)
                overlap_count += part_tokens

            current_parts = overlap_parts
            current_tokens = overlap_count

        current_parts.append(unit)
        current_tokens += unit_tokens

    # Final chunk
    if current_parts:
        text = "\n\n".join(current_parts)
        if _count_tokens(text) >= min_chunk_tokens or not chunks:
            chunks.append(text)
        elif chunks:
            # Too small — merge with the last chunk
            chunks[-1] = chunks[-1] + "\n\n" + text

    return chunks


def chunk_document(
    parsed: ParsedDocument,
    config: ChunkerConfig | None = None,
) -> list[ChunkResult]:
    """Split a parsed document into chunks.

    Returns a list of ``ChunkResult`` with sequential ordinals starting from 0.
    """
    if config is None:
        config = ChunkerConfig()

    results: list[ChunkResult] = []
    ordinal = 0

    for section in parsed.sections:
        heading_path_str = " > ".join(section.heading_path) if section.heading_path else None

        units = _split_text_units(section.text)
        chunk_texts = _merge_units_with_overlap(
            units,
            max_tokens=config.max_tokens,
            overlap_tokens=config.overlap_tokens,
            min_chunk_tokens=config.min_chunk_tokens,
        )

        for chunk_text in chunk_texts:
            token_count = _count_tokens(chunk_text)
            results.append(
                ChunkResult(
                    text=chunk_text,
                    token_count=token_count,
                    ordinal=ordinal,
                    page=section.page,
                    section=section.heading_path[-1] if section.heading_path else None,
                    heading_path=heading_path_str,
                    metadata={
                        "document_title": parsed.title,
                    },
                )
            )
            ordinal += 1

    return results
