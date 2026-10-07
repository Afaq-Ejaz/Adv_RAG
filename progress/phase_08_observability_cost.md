# Phase 8 — Observability and Cost Tracking

**Status:** ⬜ Not started
**Depends on:** [Phase 7](phase_07_versioning_lifecycle.md); uses the P0 structured logs and P3 `usage_events`
**Next:** [Phase 9 — Security Hardening](phase_09_security.md)

## Goal

Trace any answer back to its stages, see system health, and know what each tenant costs.

## Why This Won't Break Earlier Phases

Instrumentation only (decorators/middleware). No business-logic changes.

## Tasks

### Tracing
- [ ] OpenTelemetry SDK set up
- [ ] A span per query pipeline stage
- [ ] A span per ingestion step (parse, chunk, embed, index)
- [ ] Trace context passed into Dramatiq jobs
- [ ] Export to **Cloud Trace**

### Metrics
- [ ] Latency per stage
- [ ] Retrieval hit counts / empty-result rate
- [ ] Ingestion throughput and failure rate
- [ ] Queue depth
- [ ] Error rates per endpoint

### LLM inspection (optional)
- [ ] Self-hosted Langfuse (or similar) for prompt/response inspection

### Cost tracking
- [ ] Model pricing table (versioned)
- [ ] Turn `usage_events` into cost per tenant / day / model
- [ ] Per-tenant quotas (requests, tokens, storage)
- [ ] Budget alerts

### Feedback loop
- [ ] `POST /v1/feedback` (thumbs up/down + comment), linked to request/trace
- [ ] Negative feedback exported as candidate eval questions

## Exit Criteria

- [ ] Any slow or bad answer can be traced to its stages
- [ ] Cost per tenant visible
- [ ] Quotas enforced
- [ ] All Phase 0–7 tests still pass

## Notes / Decisions Log

_Add decisions made during implementation here._
