"""Dependency health checks, run concurrently with a per-check timeout."""

import asyncio
import time
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HealthCheck:
    name: str
    probe: Callable[[], Awaitable[object]]


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    ok: bool
    latency_ms: float
    error: str | None = None


@dataclass(frozen=True, slots=True)
class HealthReport:
    checks: tuple[CheckResult, ...]

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks)


async def _run_one(check: HealthCheck, timeout_s: float) -> CheckResult:
    start = time.perf_counter()
    try:
        async with asyncio.timeout(timeout_s):
            await check.probe()
    except TimeoutError:
        error: str | None = f"timed out after {timeout_s}s"
    except Exception as exc:  # health checks report failures; they never raise
        error = f"{type(exc).__name__}: {exc}"
    else:
        error = None
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    return CheckResult(name=check.name, ok=error is None, latency_ms=latency_ms, error=error)


async def run_health_checks(checks: Sequence[HealthCheck], *, timeout_s: float) -> HealthReport:
    results = await asyncio.gather(*(_run_one(c, timeout_s) for c in checks))
    return HealthReport(checks=tuple(results))
