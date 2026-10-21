# Phase 8 — Observability and Cost Tracking

**Status:** ⬜ Not started
**Depends on:** [Phase 7](phase_07_versioning_lifecycle.md)
**Next:** [Phase 9](phase_09_security.md)

## Goal

Trace any answer back to its stages, see system health, know what each tenant costs.

## Tasks

### Tracing
- [ ] OpenTelemetry SDK, span per query stage and ingestion step
- [ ] Export to Cloud Trace

### Metrics
- [ ] Latency per stage, error rates, ingestion throughput, queue depth

### Usage tracking
- [ ] `usage_events` table (tenant_id, model, tokens, timestamp)
- [ ] Cost per tenant / day / model

### Feedback
- [ ] `POST /v1/feedback` (thumbs up/down), linked to request

## Exit Criteria

- [ ] Slow/bad answers traceable to their stages
- [ ] Cost per tenant visible
