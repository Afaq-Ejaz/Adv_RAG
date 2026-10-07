# Phase 4 — Evaluation Harness (quality safety net)

**Status:** ⬜ Not started
**Depends on:** [Phase 3](phase_03_baseline_rag.md) (working pipeline)
**Next:** [Phase 5 — Auth, Tenancy, Permissions](phase_05_auth_tenancy_permissions.md)

## Goal

Measure answer quality with one command, and block any change that makes it worse.

## Why It Comes This Early

Every later phase changes retrieval or generation. Without a baseline you can't tell whether a change helped or broke things.

## Why This Won't Break Phase 3

Offline tooling only. It doesn't touch the runtime path.

## Tasks

### Dataset
- [ ] Format `eval/datasets/postex_v1.jsonl`: `question`, `expected_answer`, `expected_sources` (doc + pages), `tags`
- [ ] 50–100 real questions from PostEx domain experts
- [ ] A small "smoke" subset (~15 questions) for CI

### Retrieval metrics
- [ ] Recall@k
- [ ] MRR
- [ ] nDCG

### Generation metrics (Gemini as judge)
- [ ] Faithfulness / groundedness
- [ ] Answer relevance
- [ ] Citation correctness
- [ ] Judge prompts versioned

### Runner
- [ ] `advance-rag eval run --dataset <path> --config <pipeline-config>`
- [ ] JSON + Markdown report
- [ ] Store runs in an `eval_runs` table (config, scores, timestamp, git SHA)
- [ ] `advance-rag eval compare <run_a> <run_b>`

### CI quality gate
- [ ] Run the smoke subset on every PR
- [ ] Fail if any metric drops more than X% below the stored baseline (X configurable)

## Exit Criteria

- [ ] Baseline scores for the Phase 3 pipeline are recorded
- [ ] The gate blocks a deliberately broken change (e.g. top_k=1)
- [ ] All Phase 0–3 tests still pass

## Baseline Scores

| Metric | Baseline (P3) |
|---|---|
| Recall@5 | |
| MRR | |
| Faithfulness | |
| Answer relevance | |
| Citation correctness | |

## Notes / Decisions Log

_Add decisions made during implementation here._
