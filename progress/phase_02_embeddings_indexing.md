# Phase 2 — Embeddings and Indexing

**Status:** ⬜ Not started
**Depends on:** [Phase 1](phase_01_ingestion_parsing.md)
**Next:** [Phase 3](phase_03_baseline_rag.md)

## Goal

Make every chunk searchable by meaning (Qdrant) and by keyword (Postgres FTS).

## Tasks

### Embeddings
- [ ] `GeminiEmbedder` adapter (gemini-embedding-001, batching, retry)
- [ ] Save embedding_model and dimension per chunk

### Vector index
- [ ] `QdrantVectorStore` adapter (tenant_id filter, idempotent upsert)

### Keyword index
- [ ] `tsvector` column + GIN index on `chunks`
- [ ] `PgKeywordIndex` adapter (websearch_to_tsquery)

### Pipeline
- [ ] Extend status: `CHUNKED → EMBEDDING → INDEXED | FAILED`
- [ ] Re-indexing is idempotent

### Debug endpoints
- [ ] `POST /v1/search/vector` + `POST /v1/search/keyword`

### Tests
- [ ] Unit tests with fake embedder
- [ ] Integration: upload → INDEXED → both searches return expected chunks
- [ ] Idempotency test

## Exit Criteria

- [ ] Documents reach INDEXED
- [ ] Both searches return expected chunks
- [ ] Re-indexing creates no duplicates
