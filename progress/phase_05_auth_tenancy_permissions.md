# Phase 5 — Auth, Multi-Tenancy Enforcement, Permission Filter

**Status:** ⬜ Not started
**Depends on:** [Phase 4](phase_04_evaluation.md); uses the P0 `RequestContext`, the P1/P2 `tenant_id`/`acl` columns, and the P3 no-op `PermissionFilter` stage
**Next:** [Phase 6 — Advanced Retrieval](phase_06_advanced_retrieval.md)

## Goal

Real users, real tenants, fully isolated data, and document-level permissions applied during retrieval.

## Why This Won't Break Earlier Phases

The schema is already there; this phase switches enforcement on. Existing data sits in the default tenant with public ACLs, so behaviour for current data doesn't change.

## Tasks

### Authentication
- [ ] Tenant-scoped **API keys** (stored hashed, prefix shown) for service clients
- [ ] **JWT** login for UI users
- [ ] `auth/` resolves the real `RequestContext` (replaces the default-tenant resolver)

### Authorization model
- [ ] Roles: `owner`, `admin`, `member`, `viewer`
- [ ] Groups + memberships
- [ ] Document ACL = allowed users / groups / roles (uses the existing `acl` column)

### Tenant isolation (three layers)
- [ ] Postgres **Row-Level Security** on all tenant tables; session sets `app.tenant_id`
- [ ] Qdrant adapter adds a **mandatory** `tenant_id` filter internally (callers can't skip it)
- [ ] Object storage paths enforced as `{tenant_id}/...`

### Permission filter (pre-retrieval)
- [ ] Make the `PermissionFilter` stage real
- [ ] Push ACL conditions into Qdrant payload filters
- [ ] Push ACL conditions into the SQL `WHERE` clause for FTS
- [ ] Mirror ACL changes into the Qdrant payload (no re-embedding needed)

### Admin endpoints
- [ ] Create tenant
- [ ] Manage users, groups, API keys
- [ ] Update document ACL

### Feature flags
- [ ] Per-tenant `feature_flags` table + helper (used from Phase 6)

### Tests
- [ ] Cross-tenant leak tests: tenant A can never retrieve tenant B's data through vector search, keyword search, document APIs, or storage
- [ ] ACL tests: users see only allowed docs
- [ ] Auth tests: invalid/expired key or JWT → 401/403

## Exit Criteria

- [ ] All leak and ACL tests pass
- [ ] Eval scores unchanged vs. baseline (existing data is public in the default tenant)
- [ ] All Phase 0–4 tests still pass

## Notes / Decisions Log

_Add decisions made during implementation here._
