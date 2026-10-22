# Phase 4 — Evaluation Harness

**Status:** ⬜ Not started
**Depends on:** [Phase 3B](phase_03b_lightweight_eval.md)
**Next:** [Phase 5](phase_05_auth_tenancy_permissions.md)

## Goal

Measure answer quality with one command. Block changes that make it worse.

## Tasks

### Dataset
- [ ] `eval/datasets/postex_v1.jsonl` (question, expected_answer, expected_sources)
- [ ] 50–100 real questions + a ~15-question smoke subset for CI

### Metrics
- [ ] Retrieval: Recall@k, MRR
- [ ] Generation (Gemini-as-judge): faithfulness, answer relevance, citation correctness

### Runner
- [ ] CLI: `advance-rag eval run --dataset <path>`
- [ ] JSON + Markdown report
- [ ] `advance-rag eval compare <run_a> <run_b>`

### CI gate
- [ ] Smoke subset on every PR, fail if metrics drop below baseline

## Exit Criteria

- [ ] Baseline scores recorded for Phase 3 pipeline
- [ ] Gate blocks a deliberately broken config
