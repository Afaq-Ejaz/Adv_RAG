# Phase 2 — Knowledge Plane II: Embeddings and Indexing

**Status:** ⬜ Not started
**Depends on:** [Phase 1](phase_01_ingestion_parsing.md) (chunks)
**Next:** [Phase 3 — Baseline RAG](phase_03_baseline_rag.md)

## Goal

Make every chunk searchable by meaning (Qdrant) and by keyword (Postgres full-text).

## Why This Won't Break Phase 1

It adds two pipeline steps after `CHUNKED`. Ingestion code from Phase 1 is untouched; the new steps are added to the task chain.

## Tasks

### Embeddings
- [ ] `GeminiEmbedder` adapter (`gemini-embedding-001`)
- [ ] Batching, retry/backoff, rate-limit handling
- [ ] `task_type=RETRIEVAL_DOCUMENT` for chunks (`RETRIEVAL_QUERY` reserved for Phase 3)
- [ ] Output dimensionality configurable (e.g. 768 / 1536 / 3072)
- [ ] Save `embedding_model` and `embedding_dim` per chunk/version (needed for Phase 7 migrations)

### Vector index (Qdrant)
- [ ] `QdrantVectorStore` adapter
- [ ] One collection per model+dimension, e.g. `chunks__gemini-embedding-001__768`
- [ ] Payload: `tenant_id` (tenant index), `document_id`, `version`, ACL fields, page, section
- [ ] Point ID = chunk UUID, so indexing is idempotent

### Keyword index (Postgres FTS)
- [ ] Generated `tsvector` column on `chunks` (additive migration)
- [ ] GIN index
- [ ] `PgKeywordIndex` adapter (`websearch_to_tsquery` + `ts_rank_cd`)
- [ ] FTS dictionary configurable (`english` vs `simple`, depends on the language open question)

### Pipeline
- [ ] Extend the state machine: `CHUNKED → EMBEDDING → INDEXED | FAILED`
- [ ] Re-running a job is safe (no duplicates)

### Tooling and debug endpoints
- [ ] CLI: `advance-rag reindex --tenant <id> [--document <id>]`
- [ ] `POST /v1/search/vector` (debug)
- [ ] `POST /v1/search/keyword` (debug)

### Tests
- [ ] Unit tests with a fake embedder
- [ ] Integration test: upload → `INDEXED` → both searches return the expected chunks
- [ ] Idempotency test: re-index twice → same point count

## Exit Criteria

- [ ] Documents reach `INDEXED`
- [ ] Both debug searches return the expected chunks
- [ ] Re-indexing doesn't create duplicates
- [ ] All Phase 0–1 tests still pass

## Notes / Decisions Log

_Add decisions made during implementation here._
