"""Document domain models and status state machine.

Status flow:
    Phase 1: PENDING → PARSING → CHUNKED | FAILED
    Phase 2: extends to CHUNKED → EMBEDDING → INDEXED | FAILED

The enum is defined here (not in models.py) so both ORM models and API schemas
can import it without circular dependencies.
"""

from enum import StrEnum


class DocumentStatus(StrEnum):
    """Document processing status.  New states are appended, never removed."""

    PENDING = "PENDING"
    PARSING = "PARSING"
    CHUNKED = "CHUNKED"
    # Phase 2 will use these:
    EMBEDDING = "EMBEDDING"
    INDEXED = "INDEXED"
    # Terminal failure:
    FAILED = "FAILED"


# Valid state transitions.  Used by the service layer to enforce the state machine.
_TRANSITIONS: dict[DocumentStatus, frozenset[DocumentStatus]] = {
    DocumentStatus.PENDING: frozenset({DocumentStatus.PARSING, DocumentStatus.FAILED}),
    DocumentStatus.PARSING: frozenset({DocumentStatus.CHUNKED, DocumentStatus.FAILED}),
    DocumentStatus.CHUNKED: frozenset({DocumentStatus.EMBEDDING, DocumentStatus.FAILED}),
    DocumentStatus.EMBEDDING: frozenset({DocumentStatus.INDEXED, DocumentStatus.FAILED}),
    DocumentStatus.INDEXED: frozenset({DocumentStatus.EMBEDDING}),  # re-index
    DocumentStatus.FAILED: frozenset({DocumentStatus.PENDING}),     # retry
}


def can_transition(current: DocumentStatus, target: DocumentStatus) -> bool:
    return target in _TRANSITIONS.get(current, frozenset())
