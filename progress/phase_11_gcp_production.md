# Phase 11 — GCP Production Deployment and Scale

**Status:** ⬜ Not started
**Depends on:** [Phase 10](phase_10_streamlit_ui.md) (and all previous phases)
**Next:** — (future: extract heavy components into separate services)

## Goal

Run PostEx in production on GCP with autoscaling, backups and alerting.

## Why This Won't Break Earlier Phases

Infrastructure only. Same containers and same config interface (env vars).

> 💡 A bare-bones staging deploy should already exist from [Phase 3](phase_03_baseline_rag.md). This phase hardens it for production.

## Tasks

### Infrastructure as code (Terraform)
- [ ] Cloud Run services: API, worker, Streamlit
- [ ] Cloud SQL Postgres (HA, private IP)
- [ ] Memorystore Redis
- [ ] GCS buckets (documents, Qdrant snapshots, backups)
- [ ] Artifact Registry
- [ ] Secret Manager
- [ ] VPC + Serverless VPC connector
- [ ] Separate staging and prod environments

### Qdrant
- [ ] Decide: **Qdrant Cloud on GCP** (managed) vs. self-hosted on GCE/GKE
- [ ] Snapshots to GCS on a schedule

### Workers
- [ ] Cloud Run worker with always-on CPU (or worker pools)
- [ ] Autoscale on queue depth

### CI/CD
- [ ] build → test → eval gate → deploy to staging → manual promote to prod
- [ ] Database migrations run as a deploy step (additive-only)

### Reliability
- [ ] Backups (Cloud SQL PITR, GCS versioning, Qdrant snapshots)
- [ ] Disaster recovery runbook
- [ ] Restore drill
- [ ] Load test (Locust)
- [ ] SLOs + alerting (Cloud Monitoring)

### Future extraction points
- [ ] Document the first service extraction candidates: ingestion workers, reranking

## Exit Criteria

- [ ] PostEx live in production
- [ ] Load test meets SLOs
- [ ] Restore drill succeeds
- [ ] All Phase 0–10 tests and the eval gate pass in the pipeline

## Notes / Decisions Log

_Add decisions made during implementation here._
