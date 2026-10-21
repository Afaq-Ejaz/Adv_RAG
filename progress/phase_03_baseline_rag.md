# Phase 3 — Baseline RAG End-to-End

**Status:** ⬜ Not started
**Depends on:** [Phase 2](phase_02_embeddings_indexing.md)
**Next:** [Phase 4](phase_04_evaluation.md)

## Goal

Ask a question, get a cited answer. First working end-to-end RAG.

## Tasks

### Query pipeline
- [ ] `QueryContext` object + `QueryPipeline` (ordered stages)
- [ ] Stages: Retrieve (vector) → BuildContext → Generate → Cite
- [ ] No-op placeholders for Understand, PermissionFilter, Rerank (filled later)

### Context builder
- [ ] Token budget, dedupe overlapping chunks, source markers `[n]`

### Generation
- [ ] `GeminiLLMClient` adapter (sync + streaming)
- [ ] Prompt template: answer from context only, else say "I don't know"

### Citations
- [ ] Map `[n]` → {document_id, title, page, chunk_id}

### API
- [ ] `POST /v1/query` (sync) + `POST /v1/query/stream` (SSE)

### Tests
- [ ] Unit test per stage
- [ ] E2E: upload → query → cited answer

## Exit Criteria

- [ ] A question returns a correct, cited answer
- [ ] Streaming works
- [ ] All previous tests still pass
