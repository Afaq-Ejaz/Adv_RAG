# Phase 0 — Foundation and Skeleton

**Status:** 🟨 In progress
**Depends on:** —
**Next:** [Phase 1](phase_01_ingestion_parsing.md)

## Goal

Running app shell with all boundaries in place, no business logic.

## Tasks

### Tooling
- [x] Dependencies via `uv` (FastAPI, SQLAlchemy 2, Alembic, Dramatiq, Qdrant, structlog, etc.)
- [x] Configure ruff, mypy, pytest
- [ ] Pre-commit hooks

### Core
- [x] `core/config.py` — pydantic-settings, `.env`
- [x] `core/logging.py` — structlog JSON logs
- [x] `core/db.py` — SQLAlchemy engine/session factory
- [x] `core/context.py` — `RequestContext` (tenant_id, user_id, request_id)
- [x] `core/errors.py` — error types + exception handlers

### Infrastructure
- [ ] `docker-compose.yml` — Postgres, Redis, Qdrant
- [ ] Alembic initialised with base migration (`tenants`, `users`)
- [ ] Seed default tenant

### Interfaces (ports + fakes)
- [x] `ObjectStorage`, `VectorStore`, `KeywordIndex`, `Embedder`, `LLMClient`, `DocumentParser`
- [x] In-memory fakes for all ports

### API and workers
- [ ] FastAPI app factory, `/v1` router
- [ ] `GET /v1/health`
- [ ] Dramatiq broker (Redis) + `ping` actor

### CI
- [ ] GitHub Actions: lint → type-check → tests

## Exit Criteria

- [ ] `docker compose up` brings up all services
- [ ] `/v1/health` returns healthy
- [ ] `uv run pytest` is green
