# Phase 1 — Knowledge Plane I: Ingestion, Parsing, Chunking, Metadata

**Status:** ✅ Complete
**Depends on:** [Phase 0](phase_00_foundation.md) (interfaces, DB, worker)
**Next:** [Phase 2 — Embeddings and Indexing](phase_02_embeddings_indexing.md)

## Goal

Upload PDF/DOCX files, store the originals, and turn them into structured chunks with metadata. All processing runs asynchronously.

## Why This Won't Break Phase 0

New tables and new endpoints only. No existing code paths change.

## Tasks

### Schema (additive migration)
- [x] `documents` — tenant_id, title, source, mime, content_hash, status, error, `acl` JSONB (default `{"public": true}`)
- [x] `document_versions` — document_id, version (always `1` in this phase), storage_uri, created_at
- [x] `chunks` — tenant_id, document_version_id, ordinal, text, token_count, page, section, metadata JSONB

### Object storage
- [x] `LocalStorage` adapter (dev)
- [x] `GCSStorage` adapter (prod), picked by config
- [x] Storage paths already prefixed `{tenant_id}/...`

### Upload and job flow
- [x] `POST /v1/documents` (multipart) → store original → status `PENDING` → queue Dramatiq job
- [x] Status state machine: `PENDING → PARSING → CHUNKED | FAILED` (P2 extends it with `EMBEDDING → INDEXED`)
- [x] Error details saved on failure; jobs retry with backoff
- [x] Duplicate check by `content_hash` within a tenant

### Parsing
- [x] Common `ParsedDocument` model (sections, pages, tables as text)
- [x] PDF parser (`pdfplumber` / `pypdf`)
- [x] DOCX parser (`python-docx`), including headings and tables

### Chunking and metadata
- [x] Structure-aware recursive chunker (heading → paragraph → sentence)
- [x] Token-based size and overlap (configurable)
- [x] Page / section / heading path kept on each chunk

### Read endpoints
- [x] `GET /v1/documents` (list, paginated)
- [x] `GET /v1/documents/{id}` (status + chunk count)

### Tests
- [x] Parser unit tests on fixture PDFs/DOCX (add sample PostEx docs to `tests/fixtures/`)
- [x] Chunker unit tests (size limits, overlap, metadata kept)
- [x] Integration test: upload → `CHUNKED`

## Exit Criteria

- [x] Sample PostEx PDFs/DOCX produce correct chunks with page/section metadata
- [x] Failed documents show a clear error status
- [x] All Phase 0 tests still pass

## Risks

> 🚫 **Licensing:** PyMuPDF is **AGPL**. A sellable product would need a commercial licence. Use MIT/BSD parsers. Docling (MIT) can be added later as an optional adapter for complex tables or layouts.

> ❓ **Open question:** If any PDFs are scanned images, add an OCR adapter (Document AI / Gemini multimodal) in this phase.

## Notes / Decisions Log

_Add decisions made during implementation here._
