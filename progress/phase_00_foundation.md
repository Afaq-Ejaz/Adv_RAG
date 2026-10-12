# Phase 0 — Foundation and Skeleton

**Status:** 🟨 In progress
**Depends on:** —
**Next:** [Phase 1 — Ingestion and Parsing](phase_01_ingestion_parsing.md)

## Goal

A running, tested app shell with every boundary in place and no business logic yet.

## Pre-flight Check

> ⚠️ **Python 3.14 risk:** `pyproject.toml` requires `>=3.14`. Before anything else, check that `qdrant-client`, `dramatiq`, `asyncpg`/`psycopg`, `google-genai`, `pdfplumber` and `python-docx` all ship 3.14 wheels. If any don't, pin to **3.12/3.13** now. Changing Python versions later is disruptive.

- [x] Python version compatibility verified (2026-10-07: every core dependency resolves **binary-only** for Python 3.14 on `x86_64-pc-windows-msvc` and `x86_64-manylinux_2_28` → **keep 3.14**)

## Tasks

### Tooling
- [x] Add dependencies via `uv` (FastAPI, uvicorn, pydantic-settings, SQLAlchemy 2, Alembic, psycopg/asyncpg, redis, dramatiq, qdrant-client, structlog)
- [x] Configure ruff, mypy, pytest (+ pytest-asyncio)
- [ ] Pre-commit hooks

### Core
- [x] `core/config.py` — pydantic-settings, `.env` (`.env.example` still missing)
- [x] `core/logging.py` — structlog, JSON logs (`request_id` middleware not yet wired)
- [x] `core/db.py` — SQLAlchemy engine/session factory
- [x] `core/context.py` — `RequestContext` (tenant_id, user_id, request_id), resolves to default tenant
- [x] `core/errors.py` — error types + FastAPI exception handlers

### Infrastructure
- [ ] `docker-compose.yml` — Postgres 16, Redis, Qdrant
- [ ] Alembic initialised
- [ ] Base migration: `tenants`, `users` tables (ORM models exist but no migration files)
- [ ] Seed the **default tenant**

### Interfaces (ports) with stub adapters
- [x] `ObjectStorage` — port defined + `InMemoryObjectStorage` fake
- [x] `VectorStore` — port defined + `InMemoryVectorStore` fake
- [x] `KeywordIndex` — port defined + `InMemoryKeywordIndex` fake
- [x] `Embedder` — port defined + `HashEmbedder` fake
- [x] `LLMClient` — port defined + `EchoLLM` fake
- [x] `DocumentParser` — port defined + `PlainTextParser` fake

### API and workers
- [ ] FastAPI app factory, `/v1` router (CLI references `api.app:create_app` but the module doesn't exist yet)
- [ ] `GET /v1/health` — checks DB, Redis and Qdrant connectivity (health check infrastructure exists in `infra/health.py` but no HTTP endpoint)
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
