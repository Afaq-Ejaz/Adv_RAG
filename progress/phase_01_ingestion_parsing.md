# Phase 1 — Ingestion, Parsing, Chunking

**Status:** ✅ Complete
**Depends on:** [Phase 0](phase_00_foundation.md)
**Next:** [Phase 2](phase_02_embeddings_indexing.md)

## Goal

Upload PDF/DOCX → store originals → produce structured chunks with metadata. Async processing.

## Tasks

### Schema
- [x] `documents` table (tenant_id, title, mime, content_hash, status, acl)
- [x] `document_versions` table (document_id, version, storage_uri)
- [x] `chunks` table (tenant_id, document_version_id, ordinal, text, token_count, page, section)

### Storage
- [x] `LocalStorage` adapter (dev) + `GCSStorage` adapter (prod)

### Upload flow
- [x] `POST /v1/documents` → store → queue Dramatiq job
- [x] Status: `PENDING → PARSING → CHUNKED | FAILED`
- [x] Duplicate check by content_hash per tenant

### Parsing
- [x] PDF parser (pdfplumber)
- [x] DOCX parser (python-docx)

### Chunking
- [x] Structure-aware recursive chunker (heading → paragraph → sentence)
- [x] Token-based size/overlap, page/section metadata kept

### Read endpoints
- [x] `GET /v1/documents` (paginated) + `GET /v1/documents/{id}`

### Tests
- [x] Parser + chunker unit tests
- [x] Integration test: upload → CHUNKED

## Exit Criteria

- [x] Sample PDFs/DOCX produce correct chunks with metadata
- [x] Failed documents show clear error status
- [x] Phase 0 tests still pass
