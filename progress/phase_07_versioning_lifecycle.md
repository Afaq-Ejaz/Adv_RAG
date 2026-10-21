# Phase 7 — Versioning and Document Lifecycle

**Status:** ⬜ Not started
**Depends on:** [Phase 6](phase_06_advanced_retrieval.md)
**Next:** [Phase 8](phase_08_observability_cost.md)

## Goal

Update and delete documents safely with no query downtime.

## Tasks

### Document versions
- [ ] Re-upload creates a new version
- [ ] Index new version before retiring old (no gap)
- [ ] Retrieval returns only active version
- [ ] `GET /v1/documents/{id}/versions`

### Deletion
- [ ] Soft delete (hidden from retrieval immediately)
- [ ] Async purge from Qdrant, FTS, storage

### Tests
- [ ] Queries work during re-index
- [ ] Deleted content never returned

## Exit Criteria

- [ ] Update and delete with zero query downtime
- [ ] Eval scores unchanged
