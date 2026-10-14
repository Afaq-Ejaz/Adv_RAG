"""DOCX parser using python-docx.

Extracts text with heading hierarchy preserved.  Each heading starts a new
section; paragraphs under a heading are grouped together.  Tables are extracted
as pipe-delimited text rows within their containing section.

The heading path (e.g. ``("Chapter 1", "Section 1.1")``) is carried on every
``ParsedSection`` so the chunker can preserve structural context.
"""

import io
from collections.abc import Sequence

from docx import Document as DocxDocument
from docx.table import Table
from docx.text.paragraph import Paragraph

from advance_rag.infra.ports import ParsedDocument, ParsedSection


def _table_to_text(table: Table) -> str:
    """Convert a python-docx Table to pipe-delimited text."""
    rows: list[str] = []
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        rows.append(" | ".join(cells))
    return "\n".join(rows)


class DOCXParser:
    """Parse DOCX files preserving heading hierarchy."""

    _SUPPORTED = frozenset({
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    })

    def supports(self, mime_type: str) -> bool:
        return mime_type in self._SUPPORTED

    def parse(self, data: bytes, *, filename: str | None = None) -> ParsedDocument:
        doc = DocxDocument(io.BytesIO(data))
        sections: list[ParsedSection] = []

        heading_stack: list[str] = []
        current_text_parts: list[str] = []
        current_heading_path: tuple[str, ...] = ()

        def _flush() -> None:
            nonlocal current_text_parts
            text = "\n".join(current_text_parts).strip()
            if text:
                sections.append(
                    ParsedSection(text=text, heading_path=current_heading_path)
                )
            current_text_parts = []

        for element in doc.element.body:
            # Tables
            if element.tag.endswith("}tbl"):
                table = Table(element, doc)
                current_text_parts.append(_table_to_text(table))
                continue

            # Paragraphs
            if element.tag.endswith("}p"):
                para = Paragraph(element, doc)
                style_name = para.style.name if para.style else ""

                if style_name.startswith("Heading"):
                    _flush()
                    # Determine heading level (e.g. "Heading 1" → level 1)
                    try:
                        level = int(style_name.split()[-1])
                    except (ValueError, IndexError):
                        level = 1

                    # Update heading stack
                    heading_stack = heading_stack[: level - 1]
                    heading_stack.append(para.text.strip())
                    current_heading_path = tuple(heading_stack)
                elif para.text.strip():
                    current_text_parts.append(para.text)

        _flush()  # final section

        # Try to get title from core properties
        title: str | None = None
        if doc.core_properties and doc.core_properties.title:
            title = doc.core_properties.title

        return ParsedDocument(
            sections=sections,
            title=title or filename,
            metadata={"parser": "python-docx", "section_count": len(sections)},
        )
