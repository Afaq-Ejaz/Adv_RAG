# Phase 0 — Foundation and Skeleton

**Status:** ⬜ Not started
**Depends on:** —
**Next:** [Phase 1 — Ingestion and Parsing](phase_01_ingestion_parsing.md)

## Goal

A running, tested app shell with every boundary in place and no business logic yet.

## Pre-flight Check

> ⚠️ **Python 3.14 risk:** `pyproject.toml` requires `>=3.14`. Before anything else, check that `qdrant-client`, `dramatiq`, `asyncpg`/`psycopg`, `google-genai`, `pdfplumber` and `python-docx` all ship 3.14 wheels. If any don't, pin to **3.12/3.13** now. Changing Python versions later is disruptive.

- [x] Python version compatibility verified (2026-10-07: every core dependency resolves **binary-only** for Python 3.14 on `x86_64-pc-windows-msvc` and `x86_64-manylinux_2_28` → **keep 3.14**)

## Tasks

### Tooling
- [ ] Add dependencies via `uv` (FastAPI, uvicorn, pydantic-settings, SQLAlchemy 2, Alembic, psycopg/asyncpg, redis, dramatiq, qdrant-client, structlog)
- [ ] Configure ruff, mypy, pytest (+ pytest-asyncio)
- [ ] Pre-commit hooks

### Core
- [ ] `core/config.py` — pydantic-settings, `.env` + `.env.example`
- [ ] `core/logging.py` — structlog, JSON logs, `request_id` middleware
- [ ] `core/db.py` — SQLAlchemy engine/session factory
- [ ] `core/context.py` — `RequestContext` (tenant_id, user_id, request_id), always resolves to the **default tenant** in this phase
- [ ] `core/errors.py` — error types + FastAPI exception handlers

### Infrastructure
- [ ] `docker-compose.yml` — Postgres 16, Redis, Qdrant
- [ ] Alembic initialised
- [ ] Base migration: `tenants`, `users` tables
- [ ] Seed the **default tenant**

### Interfaces (ports) with stub adapters
- [ ] `ObjectStorage`
- [ ] `VectorStore`
- [ ] `KeywordIndex`
- [ ] `Embedder`
- [ ] `LLMClient`
- [ ] `DocumentParser`

### API and workers
- [ ] FastAPI app factory, `/v1` router
- [ ] `GET /v1/health` — checks DB, Redis and Qdrant connectivity
- [ ] Dramatiq broker (Redis) + a `ping` actor

### CI
- [ ] GitHub Actions: lint → type-check → tests, with Postgres/Redis/Qdrant service containers

## Exit Criteria

- [ ] `docker compose up` brings up all services
- [ ] `/v1/health` returns healthy for DB, Redis and Qdrant
- [ ] `uv run pytest` is green
- [ ] CI pipeline is green

## Notes / Decisions Log

_Add decisions made during implementation here._
