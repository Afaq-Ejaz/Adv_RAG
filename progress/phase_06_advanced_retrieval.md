# Phase 6 — Query Plane II: Query Understanding, Hybrid Retrieval, Reranking, Grounding

**Status:** ⬜ Not started
**Depends on:** [Phase 5](phase_05_auth_tenancy_permissions.md); uses the P3 stage slots, P4 eval and P5 feature flags
**Next:** [Phase 7 — Versioning and Lifecycle](phase_07_versioning_lifecycle.md)

## Goal

Measurably better answers through smarter query handling, hybrid search, reranking and grounding checks.

## Why This Won't Break Earlier Phases

Each improvement replaces a no-op/passthrough stage, is **off by default** behind a per-tenant flag, and is turned on only after it beats the baseline in eval.

## Tasks

### Query understanding (`Understand` stage) — flag `query.rewrite`
- [ ] Rewrite conversational follow-ups into standalone queries (uses chat history)
- [ ] Optional multi-query expansion — flag `query.multi_query`
- [ ] Metadata filter extraction (date, doc type, …)
- [ ] Intent routing (chit-chat vs. knowledge question)

### Hybrid retrieval (`Retrieve` stage) — flag `retrieval.hybrid`
- [ ] Run vector + keyword searches in parallel
- [ ] Reciprocal Rank Fusion with configurable weights
- [ ] Permission filter still applied to both searches

### Reranking (`Rerank` stage) — flag `ranking.rerank`
- [ ] `Reranker` interface
- [ ] Vertex AI Ranking API adapter (GCP-native)
- [ ] Local cross-encoder adapter (e.g. `bge-reranker`) as a fallback

### Grounding (`Cite` stage) — flag `generation.grounding_check`
- [ ] Check every claim is backed by a cited chunk
- [ ] "Insufficient context" refusal path
- [ ] `confidence` score in the response (new **optional** field)

### Caching — flag `cache.semantic`
- [ ] Redis response cache keyed by tenant + normalised query + index version

### Evaluation per feature
- [ ] Eval report: rewrite on vs. off
- [ ] Eval report: hybrid on vs. off
- [ ] Eval report: rerank on vs. off
- [ ] Eval report: grounding on vs. off
- [ ] Latency measured per stage

## Exit Criteria

- [ ] Each enabled feature beats the baseline in eval
- [ ] Flags enabled for PostEx
- [ ] p95 latency within budget (target < 4s)
- [ ] New baseline recorded in [Phase 4](phase_04_evaluation.md)
- [ ] All Phase 0–5 tests still pass

## Notes / Decisions Log

_Add decisions made during implementation here._
