# Phase 3B — Lightweight Evaluation

**Status:** ⬜ Not started
**Depends on:** [Phase 3](phase_03_baseline_rag.md)
**Next:** [Phase 4](phase_04_evaluation.md)

## Goal

Get a quality signal immediately. No CI gate yet — just a script you run by hand to know if your RAG is actually working.

## Tasks

### Dataset
- [ ] `eval/datasets/smoke_v1.jsonl` — 15–20 real Q/A pairs with expected source documents
- [ ] Cover: factual lookup, multi-chunk reasoning, "not in docs" refusal

### Metrics script
- [ ] `advance-rag eval quick --dataset <path>`
- [ ] Retrieval: Recall@5, Recall@10
- [ ] Generation: simple faithfulness check (does the answer contradict the sources?)
- [ ] Print results to terminal + save JSON

### Baseline snapshot
- [ ] Record initial scores as the baseline to beat

## Exit Criteria

- [ ] Script runs end-to-end and produces scores
- [ ] Baseline scores saved to `eval/baselines/`
- [ ] All previous tests still pass
