# Phase 7 — Versioning and Document Lifecycle

**Status:** ⬜ Not started
**Depends on:** [Phase 6](phase_06_advanced_retrieval.md); uses `document_versions` (P1) and per-chunk `embedding_model` (P2)
**Next:** [Phase 8 — Observability and Cost](phase_08_observability_cost.md)

## Goal

Update, delete and re-embed documents safely, with no query downtime, and be able to reproduce any past answer.

## Why This Won't Break Earlier Phases

It turns on version > 1 flows on a schema that has existed since Phase 1.

## Tasks

### Document versions
- [ ] Re-upload creates a new version
- [ ] Index the new version **before** retiring the old one (no gap)
- [ ] Retrieval only returns the active version
- [ ] `GET /v1/documents/{id}/versions`

### Deletion
- [ ] Soft delete (hidden from retrieval immediately)
- [ ] Async purge from Qdrant, FTS and storage
- [ ] Tombstones kept for audit

### Embedding model migration (blue/green)
- [ ] Build a new Qdrant collection in the background
- [ ] Run eval against the new collection
- [ ] Switch the per-tenant "active collection" pointer
- [ ] Remove the old collection after a grace period
- [ ] CLI: `advance-rag embeddings migrate --tenant <id> --model <name> --dim <n>`

### Config versioning and reproducibility
- [ ] Prompt and pipeline config versions stored
- [ ] Each answer records prompt version, pipeline version, index/collection version and chunk IDs used

### Tests
- [ ] Update flow: queries keep working during re-index
- [ ] Delete flow: deleted content never returned
- [ ] Migration flow on staging

## Exit Criteria

- [ ] Update and delete with zero query downtime
- [ ] Embedding switch done end-to-end on staging
- [ ] Eval scores unchanged
- [ ] All Phase 0–6 tests still pass

## Notes / Decisions Log

_Add decisions made during implementation here._
