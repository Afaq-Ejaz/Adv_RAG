# Phase 3 — Query Plane I: Baseline RAG End-to-End + Minimal Chat

**Status:** ⬜ Not started
**Depends on:** [Phase 2](phase_02_embeddings_indexing.md) (indexes)
**Next:** [Phase 4 — Evaluation Harness](phase_04_evaluation.md)

## Goal

Ask a question and get a cited answer: the first working end-to-end version of the product.

## Why This Won't Break Phase 2

It only reads from the indexes and adds a new `/v1/query` endpoint.

## Tasks

### Pipeline framework
- [ ] `QueryContext` object (query, tenant, user, filters, candidates, context, answer, citations, timings, usage)
- [ ] `QueryPipeline` — ordered list of stages; each stage takes and returns a `QueryContext`
- [ ] Stages in this phase:
  - [ ] `Understand` — passthrough (filled in Phase 6)
  - [ ] `PermissionFilter` — no-op (filled in Phase 5)
  - [ ] `Retrieve` — vector only (`task_type=RETRIEVAL_QUERY`)
  - [ ] `Rerank` — no-op (filled in Phase 6)
  - [ ] `BuildContext`
  - [ ] `Generate`
  - [ ] `Cite`

### Context builder
- [ ] Token budget
- [ ] Dedupe overlapping chunks
- [ ] Order by score
- [ ] Each chunk labelled with a `[n]` source marker

### Generation
- [ ] `GeminiLLMClient` adapter (sync + streaming)
- [ ] Versioned prompt template `generation/prompts/v1.yaml`
- [ ] Instruction: answer only from the context, otherwise say you don't know

### Citations
- [ ] Map each `[n]` → `{document_id, title, page, chunk_id, snippet}`
- [ ] Drop citations that point to nothing

### API
- [ ] `POST /v1/query` (sync)
- [ ] `POST /v1/query/stream` (SSE)

### Usage tracking (feeds Phase 8)
- [ ] `usage_events` table: tenant_id, request_id, kind (embed/generate), model, input_tokens, output_tokens, timestamp
- [ ] Record every LLM/embedding call

### Minimal Streamlit chat
- [ ] `ui/streamlit_app/chat.py` — calls the API only, shows the answer + citations

### Staging (recommended)
- [ ] Bare-bones staging deploy (Cloud Run + Cloud SQL) to catch cloud issues early

### Tests
- [ ] Unit test per stage
- [ ] e2e test: upload → query → cited answer

## Exit Criteria

- [ ] A PostEx question returns a correct, cited answer
- [ ] Streaming works
- [ ] Usage events are recorded
- [ ] All Phase 0–2 tests still pass

## Notes / Decisions Log

_Add decisions made during implementation here._
