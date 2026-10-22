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

### Conversation memory
- [ ] `conversations` table (tenant_id, user_id, created_at)
- [ ] `messages` table (conversation_id, role, content, citations, created_at)
- [ ] Store query + answer per turn
- [ ] Pass last N turns as context to Understand stage (no-op for now, wired in Phase 6)

### API
- [ ] `POST /v1/query` (sync) + `POST /v1/query/stream` (SSE)
- [ ] `POST /v1/conversations` + `GET /v1/conversations/{id}/messages`

### Minimal Streamlit shell
- [ ] Single-page app: upload documents + ask questions + show cited answers
- [ ] Calls only the public `/v1` API (no direct DB access)
- [ ] Good enough for demos and debugging — Phase 10 polishes this into a product

### Tests
- [ ] Unit test per stage
- [ ] E2E: upload → query → cited answer
- [ ] Conversation history persisted and retrievable

## Exit Criteria

- [ ] A question returns a correct, cited answer
- [ ] Streaming works
- [ ] Conversation history works
- [ ] Streamlit shell can upload + query
- [ ] All previous tests still pass
