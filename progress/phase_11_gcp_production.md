# Phase 11 — GCP Production Deployment

**Status:** ⬜ Not started
**Depends on:** [Phase 10](phase_10_streamlit_ui.md)
**Next:** —

## Goal

Run in production on GCP with autoscaling and backups.

## Tasks

### Infrastructure (Terraform)
- [ ] Cloud Run: API, worker, Streamlit
- [ ] Cloud SQL Postgres (HA), Memorystore Redis, GCS buckets
- [ ] Artifact Registry, Secret Manager, VPC
- [ ] Staging + prod environments

### Qdrant
- [ ] Qdrant Cloud (managed) or self-hosted on GCE
- [ ] Scheduled snapshots to GCS

### CI/CD
- [ ] Build → test → eval gate → deploy staging → promote to prod
- [ ] Migrations run as deploy step

### Reliability
- [ ] Backups (Cloud SQL PITR, GCS versioning, Qdrant snapshots)
- [ ] SLOs + alerting (Cloud Monitoring)

## Exit Criteria

- [ ] Running in production
- [ ] CI/CD pipeline passes all tests and eval gate
