# Phase 10 — Streamlit Product UI

**Status:** ⬜ Not started
**Depends on:** [Phase 9](phase_09_security.md); uses the stable `/v1` API (P3–P9)
**Next:** [Phase 11 — GCP Production](phase_11_gcp_production.md)

## Goal

A complete chat + admin app for PostEx users, so they never need to call the API directly.

## Why This Won't Break Earlier Phases

Streamlit is a pure API client. It has no direct DB access and so can't break the backend. The minimal chat page from Phase 3 grows into a multipage app, so there's no rewrite.

## Tasks

### Foundation
- [ ] Multipage Streamlit app structure (`ui/streamlit_app/pages/`)
- [ ] Shared API client module (typed, handles auth + errors)
- [ ] Login (JWT) + tenant-aware session
- [ ] Role-based page visibility

### Chat
- [ ] Streaming answers
- [ ] Clickable citations (doc + page preview)
- [ ] Conversation history
- [ ] Feedback buttons (thumbs up/down + comment)

### Knowledge admin
- [ ] Upload (multi-file)
- [ ] Ingestion status with auto-refresh
- [ ] Version history per document
- [ ] Delete
- [ ] ACL editor

### Tenant admin
- [ ] Users
- [ ] Groups
- [ ] API keys (create / revoke)

### Insights
- [ ] Usage and cost charts
- [ ] Eval run comparisons
- [ ] Low-rated answers list

## Exit Criteria

- [ ] A PostEx user completes the whole workflow (login → upload → ask → feedback) in the UI
- [ ] All Phase 0–9 tests still pass

## Notes / Decisions Log

_Add decisions made during implementation here._
