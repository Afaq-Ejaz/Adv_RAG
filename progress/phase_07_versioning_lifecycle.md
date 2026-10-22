# Phase 7 — Versioning and Document Lifecycle

**Status:** ⬜ Not started
**Depends on:** [Phase 5](phase_05_auth_tenancy_permissions.md) + [Phase 6](phase_06_advanced_retrieval.md) (both must complete)
**Next:** [Phase 8](phase_08_observability_cost.md)

## Goal

Zero-downtime document updates and safe deletion with index consistency. (Basic soft delete and re-upload were added in Phase 1; this phase handles the hard concurrent-indexing problem.)

## Tasks

### Zero-downtime re-indexing
- [ ] Re-upload triggers: parse → chunk → embed → index new version
- [ ] New version indexed *before* old version is retired (no search gap)
- [ ] Retrieval returns only the active version during the transition

### Deletion
- [ ] Soft delete (hidden from retrieval immediately)
- [ ] Async purge from Qdrant, FTS, storage

### Tests
- [ ] Queries work during re-index
- [ ] Deleted content never returned

## Exit Criteria

- [ ] Update and delete with zero query downtime
- [ ] Eval scores unchanged
