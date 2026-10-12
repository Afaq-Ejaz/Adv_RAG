"""Per-request (or per-job) execution context.

Every operation runs with a `RequestContext`. In Phase 0 it always resolves to the default
tenant; Phase 5 swaps the resolver for real authentication without changing any caller.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from uuid import UUID, uuid4

DEFAULT_TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


@dataclass(frozen=True, slots=True)
class RequestContext:
    tenant_id: UUID
    request_id: str
    user_id: UUID | None = None
    roles: frozenset[str] = field(default_factory=frozenset)


_current: ContextVar[RequestContext | None] = ContextVar("advance_rag_context", default=None)


def current_context() -> RequestContext | None:
    return _current.get()


def require_context() -> RequestContext:
    ctx = _current.get()
    if ctx is None:
        raise RuntimeError("No RequestContext is active for this operation.")
    return ctx


def set_context(ctx: RequestContext) -> Token[RequestContext | None]:
    return _current.set(ctx)


def reset_context(token: Token[RequestContext | None]) -> None:
    _current.reset(token)


def system_context(request_id: str | None = None) -> RequestContext:
    """Context for background jobs / CLI before real tenants exist."""
    return RequestContext(tenant_id=DEFAULT_TENANT_ID, request_id=request_id or uuid4().hex)


@contextmanager
def use_context(ctx: RequestContext) -> Iterator[RequestContext]:
    token = set_context(ctx)
    try:
        yield ctx
    finally:
        reset_context(token)
