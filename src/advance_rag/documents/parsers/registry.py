"""Parser registry: maps MIME types to concrete parsers.

The ``get_parser`` function returns the first parser that supports the given
MIME type, or ``None`` if no parser matches.  This makes it trivial to add
new parsers (e.g. OCR, Docling) later.
"""

from advance_rag.documents.parsers.docx_parser import DOCXParser
from advance_rag.documents.parsers.pdf_parser import PDFParser
from advance_rag.infra.fakes import PlainTextParser
from advance_rag.infra.ports import DocumentParser

# Registration order matters: first match wins.
_PARSERS: list[DocumentParser] = [
    PDFParser(),   # type: ignore[list-item]
    DOCXParser(),  # type: ignore[list-item]
    PlainTextParser(),  # type: ignore[list-item]  # fallback for text/*
]


def get_parser(mime_type: str) -> DocumentParser | None:
    """Return the first parser that supports ``mime_type``, or None."""
    for parser in _PARSERS:
        if parser.supports(mime_type):
            return parser
    return None


def supported_mime_types() -> list[str]:
    """Return a list of all supported MIME types (for documentation / validation)."""
    return [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]
