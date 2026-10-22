# Phase 6 — Advanced Retrieval and Grounding

**Status:** ⬜ Not started
**Depends on:** [Phase 4](phase_04_evaluation.md) (runs in parallel with [Phase 5](phase_05_auth_tenancy_permissions.md))
**Next:** [Phase 7](phase_07_versioning_lifecycle.md)

## Goal

Better answers through query rewriting, hybrid search, reranking, and grounding.

## Tasks

### Query understanding (Understand stage)
- [ ] Rewrite follow-ups into standalone queries
- [ ] Metadata filter extraction (date, doc type)

### Hybrid retrieval (Retrieve stage)
- [ ] Vector + keyword in parallel, Reciprocal Rank Fusion

### Reranking (Rerank stage)
- [ ] `Reranker` interface + Vertex AI Ranking adapter

### Grounding (Cite stage)
- [ ] Verify claims are backed by cited chunks
- [ ] "Insufficient context" refusal path

### Evaluation
- [ ] Eval each feature on vs. off, enable only if it beats baseline

## Exit Criteria

- [ ] Each enabled feature beats baseline in eval
- [ ] p95 latency < 4s
- [ ] New baseline recorded
