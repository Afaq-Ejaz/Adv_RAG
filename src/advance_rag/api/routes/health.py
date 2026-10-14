"""Health-check endpoint.

Returns the connectivity status of every infrastructure dependency in a
single JSON response.  Used by load balancers, Kubernetes probes, and
the human debugging experience.
"""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from advance_rag.infra.health import run_health_checks

router = APIRouter(tags=["health"])


class _CheckDetail(BaseModel):
    name: str
    ok: bool
    latency_ms: float
    error: str | None = None


class HealthResponse(BaseModel):
    status: str
    checks: list[_CheckDetail]


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    resources = request.app.state.resources
    settings = request.app.state.settings

    report = await run_health_checks(
        resources.health_checks,
        timeout_s=settings.health_check_timeout_s,
    )

    return HealthResponse(
        status="healthy" if report.ok else "unhealthy",
        checks=[
            _CheckDetail(
                name=c.name,
                ok=c.ok,
                latency_ms=c.latency_ms,
                error=c.error,
            )
            for c in report.checks
        ],
    )
