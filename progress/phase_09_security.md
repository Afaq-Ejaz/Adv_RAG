# Phase 9 — Security Hardening

**Status:** ⬜ Not started
**Depends on:** [Phase 8](phase_08_observability_cost.md)
**Next:** [Phase 10](phase_10_streamlit_ui.md)

## Goal

Secure the platform for production use.

## Tasks

### Abuse protection
- [ ] Rate limiting per API key / tenant (Redis)
- [ ] Request and file size limits

### Upload safety
- [ ] MIME sniffing (don't trust extensions)
- [ ] Handle corrupt / password-protected files

### LLM safety
- [ ] Retrieved content delimited as data, never as instructions
- [ ] Output filtering
- [ ] Prompt-injection test cases in eval dataset

### Secrets
- [ ] Move secrets to GCP Secret Manager

### Audit
- [ ] Audit log: uploads, queries, permission changes

## Exit Criteria

- [ ] Prompt-injection eval cases pass
- [ ] Rate limiting enforced
