# Phase 9 — Security Hardening

**Status:** ⬜ Not started
**Depends on:** [Phase 8](phase_08_observability_cost.md); uses P5 auth and P8 logging
**Next:** [Phase 10 — Streamlit Product UI](phase_10_streamlit_ui.md)

## Goal

Make the platform safe enough to sell to enterprise clients.

## Why This Won't Break Earlier Phases

Middleware and config changes, covered by the full regression and eval suite.

## Tasks

### Abuse protection
- [ ] Rate limiting per API key / tenant (Redis)
- [ ] Request size limits

### Upload safety
- [ ] MIME sniffing (don't trust file extensions)
- [ ] File size limits
- [ ] Malware scan hook
- [ ] Handle password-protected / corrupt files cleanly

### LLM safety
- [ ] Retrieved content treated as data (delimited, never as instructions)
- [ ] System-prompt isolation pattern
- [ ] Output filtering
- [ ] Prompt-injection test cases added to the eval dataset

### Data protection
- [ ] PII detection/redaction option per tenant (Google Cloud DLP adapter)
- [ ] CMEK option for enterprise tenants
- [ ] TLS everywhere

### Audit
- [ ] Audit log: uploads, queries, permission changes, admin actions
- [ ] Audit log export per tenant

### Secrets and supply chain
- [ ] Secrets moved to **GCP Secret Manager**
- [ ] Dependency vulnerability scanning in CI
- [ ] Container image scanning

## Exit Criteria

- [ ] OWASP API Top 10 checklist passed
- [ ] Prompt-injection eval cases pass
- [ ] All Phase 0–8 tests still pass

## Notes / Decisions Log

_Add decisions made during implementation here._
