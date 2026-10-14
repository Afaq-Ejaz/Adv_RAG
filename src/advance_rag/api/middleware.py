"""Request-context middleware.

Assigns a unique ``request_id`` to every request and sets up a
``RequestContext`` for the duration of the request.  In Phase 0 the tenant
always resolves to the default; Phase 5 replaces the resolver.

The middleware also emits a structured access log line on every response.
"""

import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

import structlog

from advance_rag.core.context import (
    DEFAULT_TENANT_ID,
    RequestContext,
    reset_context,
    set_context,
)
from advance_rag.core.logging import get_logger

log = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("x-request-id", uuid4().hex)

        # Phase 0: always the default tenant.  Phase 5 resolves from auth token.
        ctx = RequestContext(tenant_id=DEFAULT_TENANT_ID, request_id=request_id)
        token = set_context(ctx)

        # Make request_id available for error responses and access logs.
        request.state.request_id = request_id

        # Bind to structlog contextvars so every log line carries them.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            tenant_id=str(ctx.tenant_id),
        )

        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            log.info(
                "http_request",
                method=request.method,
                path=request.url.path,
                status=response.status_code if "response" in dir() else 500,
                duration_ms=duration_ms,
            )
            structlog.contextvars.clear_contextvars()
            reset_context(token)

        response.headers["x-request-id"] = request_id
        return response
