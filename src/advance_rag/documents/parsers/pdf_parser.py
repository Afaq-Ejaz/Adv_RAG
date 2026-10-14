"""PDF parser using pdfplumber.

Extracts text page-by-page.  Each page becomes a ``ParsedSection`` with the
page number preserved.  Tables are extracted as pipe-delimited text and
appended to the page's content.

Licensing note: pdfplumber is MIT-licensed (safe for commercial use).
"""

import io

import pdfplumber

from advance_rag.infra.ports import ParsedDocument, ParsedSection


class PDFParser:
    """Parse PDF files into structured sections using pdfplumber."""

    _SUPPORTED = frozenset({"application/pdf"})

    def supports(self, mime_type: str) -> bool:
        return mime_type in self._SUPPORTED

    def parse(self, data: bytes, *, filename: str | None = None) -> ParsedDocument:
        sections: list[ParsedSection] = []

        with pdfplumber.open(io.BytesIO(data)) as pdf:
            title = pdf.metadata.get("Title") if pdf.metadata else None

            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""

                # Extract tables and append as structured text
                tables = page.extract_tables()
                if tables:
                    table_lines: list[str] = []
                    for table in tables:
                        for row in table:
                            cells = [cell or "" for cell in row]
                            table_lines.append(" | ".join(cells))
                        table_lines.append("")  # blank line between tables
                    text = text + "\n\n" + "\n".join(table_lines) if text else "\n".join(table_lines)

                if text.strip():
                    sections.append(
                        ParsedSection(
                            text=text.strip(),
                            page=page_num,
                        )
                    )

        return ParsedDocument(
            sections=sections,
            title=title or filename,
            metadata={"parser": "pdfplumber", "page_count": len(sections)},
        )
