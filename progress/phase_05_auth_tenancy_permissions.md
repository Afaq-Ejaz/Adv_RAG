# Phase 5 — Auth, Multi-Tenancy, Permissions

**Status:** ⬜ Not started
**Depends on:** [Phase 4](phase_04_evaluation.md)
**Next:** [Phase 6](phase_06_advanced_retrieval.md)

## Goal

Real users, real tenants, isolated data, document-level permissions during retrieval.

## Tasks

### Authentication
- [ ] API keys (hashed) for service clients
- [ ] JWT login for UI users
- [ ] `auth/` resolves real `RequestContext`

### Authorization
- [ ] Roles: owner, admin, member, viewer
- [ ] Groups + memberships
- [ ] Document ACL (uses existing `acl` column)

### Tenant isolation
- [ ] Postgres RLS on tenant tables
- [ ] Qdrant adapter enforces tenant_id filter
- [ ] Storage paths enforced as `{tenant_id}/...`

### Permission filter
- [ ] Fill the PermissionFilter stage (push ACL into Qdrant + SQL filters)

### Admin endpoints
- [ ] Create tenant, manage users/groups/API keys, update document ACL

### Tests
- [ ] Cross-tenant leak tests (vector, keyword, API, storage)
- [ ] ACL tests: users see only allowed docs
- [ ] Auth tests: invalid credentials → 401/403

## Exit Criteria

- [ ] All leak and ACL tests pass
- [ ] Eval scores unchanged
