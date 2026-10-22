# The Mastery Map — What to Know Cold

> This file is your checklist, not a tutorial. Every item here is something you should be able to explain, implement, or debug from memory. Items are derived directly from what this project uses, plus what separates the top 5% from the average.

---

## A. Fundamentals of the Stack (What This Project Runs On)

### 1. Python — Deep, Not Surface

- Asyncio event loop, coroutines, `await`, `async for`, `async with`
- `asyncio.gather` vs `asyncio.TaskGroup` — concurrency control
- Generators & async generators (how streaming responses actually work)
- Context variables (`contextvars`) — how `RequestContext` propagates
- The descriptor protocol (`__get__`, `__set__`, `__delete__`)
- Metaclasses — when and why (Pydantic uses them)
- `__init_subclass__` — lighter alternative to metaclasses
- Protocols (`typing.Protocol`) — structural subtyping (your entire ports layer)
- Type narrowing: `TypeGuard`, `TypeVar`, `ParamSpec`, `Concatenate`
- Memory model: reference counting + cyclic GC, `__slots__`, weak references
- Import system: `importlib`, lazy imports, circular import resolution
- The GIL (and why it matters less than people think for I/O-bound RAG)
- `dataclasses` vs `attrs` vs `Pydantic` — when to use which and why

### 2. FastAPI & Web Fundamentals

- ASGI lifecycle: startup/shutdown, middleware chain, dependency injection
- Dependency injection tree — `Depends()`, scopes, overrides for testing
- Request/response cycle: validation → handler → serialization
- Background tasks vs task queues (when to use which)
- Middleware: CORS, authentication, request ID injection, timing
- SSE (Server-Sent Events) — how `/v1/query/stream` works
- HTTP status codes — know the semantics, not just 200/400/500
- API versioning strategies: URL path vs header vs content negotiation
- Rate limiting algorithms: token bucket, sliding window, leaky bucket
- OpenAPI spec generation — how FastAPI auto-docs work

### 3. SQLAlchemy 2 & PostgreSQL

- **SQLAlchemy Core vs ORM:** when to use which
- Session lifecycle: `begin()`, `flush()`, `commit()`, `expire_on_commit`
- Unit of Work pattern — what SQLAlchemy actually does under the hood
- Connection pooling: `pool_size`, `max_overflow`, `pool_pre_ping`
- Eager vs lazy loading: `joinedload`, `selectinload`, `subqueryload`, N+1 problem
- **PostgreSQL internals:**
  - MVCC (Multi-Version Concurrency Control)
  - Transaction isolation levels: READ COMMITTED vs SERIALIZABLE
  - Index types: B-tree, GIN, GiST, BRIN — when to use each
  - `tsvector`, `tsquery`, GIN indexes — full-text search mechanics
  - Row-Level Security (RLS) policies — your tenant isolation mechanism
  - `EXPLAIN ANALYZE` — reading query plans
  - Partitioning: range, list, hash
  - Advisory locks
  - JSONB: operators, indexing, when to use vs normalized columns

### 4. Alembic — Database Migrations

- Autogenerate vs manual migrations
- Expand-migrate-contract pattern
- Online schema changes (no downtime)
- Branching and merging migration heads
- Data migrations vs schema migrations

### 5. Qdrant — Vector Database

- HNSW algorithm: how approximate nearest neighbor search works
- Distance metrics: cosine, dot product, euclidean — when to use which
- Collections, points, payloads, filters
- Payload indexing — how tenant_id filtering stays fast
- Quantization: scalar, product, binary — trade-offs
- Sharding and replication
- Snapshots and backup/restore
- Batch operations and idempotent upserts

### 6. Redis

- Data structures: strings, hashes, sorted sets, streams, HyperLogLog
- Pub/Sub vs Streams — when to use which
- Lua scripting for atomic operations
- Expiration policies: LRU, LFU, volatile-*
- Persistence: RDB snapshots vs AOF
- Connection pooling in Python
- Distributed locking (Redlock)

### 7. Dramatiq — Task Queue

- Actor model: actors, messages, brokers, middleware
- Retry policies: backoff, max_retries, dead-letter queues
- Rate limiting actors
- Priority queues
- Result backends
- Worker concurrency: threads vs processes
- Graceful shutdown and message acknowledgment

### 8. Docker & Docker Compose

- Image layering, caching, multi-stage builds
- Networking: bridge, host, overlay — service discovery by container name
- Volumes: bind mounts vs named volumes
- Health checks
- Resource limits: CPU, memory
- Docker Compose profiles and environment overrides
- Container logging and log drivers

### 9. Pydantic v2

- Model validators: `@field_validator`, `@model_validator`
- Serialization: `model_dump()`, `model_dump_json()`, aliases, exclude
- Discriminated unions
- Custom types with `__get_pydantic_core_schema__`
- `pydantic-settings`: env var loading, secrets, `.env` files
- Performance: why v2 is faster (Rust core)

---

## B. AI/ML/RAG Fundamentals (What Makes the Product Intelligent)

### 10. Embeddings — Deep Understanding

- What an embedding actually represents geometrically
- Transformer encoder architecture (at the level of: attention → FFN → pooling)
- Tokenization: BPE, SentencePiece, WordPiece
- Cosine similarity vs dot product — when they're equivalent and when not
- Embedding dimensions and the curse of dimensionality
- Matryoshka embeddings (variable-dimension)
- Asymmetric embeddings (separate query vs document models)
- Fine-tuning embeddings: contrastive loss, triplet loss, hard negatives
- Embedding drift when switching models — re-indexing strategy

### 11. Chunking Strategies

- Fixed-size vs recursive vs structure-aware vs semantic chunking
- Token counting vs character counting
- Overlap: why it exists, optimal ratios
- Late chunking (embed first, split after)
- Parent-child chunking (retrieve child, expand to parent for context)
- Chunk size vs retrieval accuracy trade-off

### 12. Retrieval

- Vector search: ANN (HNSW, IVF, ScaNN) — algorithmic complexity trade-offs
- Keyword search: TF-IDF, BM25, `tsvector`/`tsquery`
- Hybrid search: why neither alone is sufficient
- Reciprocal Rank Fusion (RRF) — the math and why it works
- Reranking: cross-encoder models, Vertex AI Ranking API
- Multi-stage retrieval: fast recall → precise reranking
- Metadata filtering: pre-filter vs post-filter performance impact
- Maximum Marginal Relevance (MMR) — diversity in results

### 13. Generation & Prompting

- How autoregressive LLMs generate (token-by-token, softmax, temperature, top-k, top-p)
- Context window management: token budgets, truncation strategies
- System prompt vs user prompt separation
- Few-shot prompting
- Chain-of-thought prompting
- Structured output (JSON mode, function calling)
- Streaming: how SSE token streaming works at the API level
- Grounding and citation: claim verification against source chunks
- Hallucination: why it happens, detection methods, mitigation
- Prompt injection: direct, indirect, jailbreaks — and defenses

### 14. Evaluation (RAG-Specific)

- Retrieval metrics: Recall@k, Precision@k, MRR, NDCG
- Generation metrics: faithfulness, answer relevance, citation correctness
- LLM-as-judge: how to use one LLM to evaluate another's output
- RAGAS framework concepts
- A/B testing for RAG pipelines
- Regression testing: baseline snapshots, drift detection

---

## C. Software Engineering Fundamentals (What Makes It Production-Grade)

### 15. Architecture Patterns

- Hexagonal / Ports & Adapters (your entire infra layer)
- Modular monolith → microservices migration path
- CQRS (Command Query Responsibility Segregation)
- Event sourcing (understand it even if you don't use it)
- Pipeline / Chain of Responsibility pattern (your `QueryPipeline`)
- Repository pattern
- Unit of Work
- Dependency injection (without a framework)

### 16. Testing

- Unit vs integration vs E2E — the test pyramid
- Fakes vs mocks vs stubs — when to use which (your project uses fakes — know why)
- Fixture design: factories, builders
- Property-based testing (Hypothesis)
- Snapshot testing for API responses
- Test isolation: database transactions, test containers

### 17. Observability

- The three pillars: logs, metrics, traces
- Structured logging (structlog — your project uses it)
- OpenTelemetry: spans, traces, context propagation, exporters
- Metrics: counters, gauges, histograms — RED method (Rate, Errors, Duration)
- Distributed tracing across async workers
- SLOs, SLIs, error budgets

### 18. Security

- Authentication vs authorization — the difference matters
- JWT: header, payload, signature, expiration, refresh tokens
- API key hashing (bcrypt/argon2 — never store plaintext)
- OWASP Top 10 for APIs
- SQL injection (parameterized queries — SQLAlchemy handles this, but know *why*)
- SSRF, IDOR, broken access control
- Secrets management (environment variables → Secret Manager)
- Content Security: MIME sniffing, file upload validation

### 19. DevOps & CI/CD

- Git: rebase vs merge, conventional commits, branch strategies
- GitHub Actions: workflows, jobs, steps, matrix builds, caching
- Container orchestration basics (Cloud Run, understand Kubernetes concepts)
- Infrastructure as Code: Terraform basics
- Blue-green / canary deployments
- Database migration in CI/CD pipelines

---

## D. Edge-Givers — What Separates You From Average

### 20. System Design Thinking

- Capacity estimation: QPS, storage, bandwidth, cost
- CAP theorem — and why it actually matters for your Qdrant + Postgres combo
- Consistency models: strong, eventual, causal
- Back-of-envelope calculations for latency budgets
- Multi-tenancy architectures: pool vs silo vs bridge
- Cost modeling: per-tenant, per-query, per-token

### 21. Advanced RAG Patterns (Beyond This Project)

- Agentic RAG: tool-use, multi-step retrieval, self-reflection loops
- Graph RAG: knowledge graphs + vector search
- Corrective RAG (CRAG): verify → decide → search again
- Self-RAG: LLM decides when to retrieve
- Multi-modal RAG: images, tables, charts as retrievable units
- Adaptive retrieval: route queries to different strategies based on type
- Query decomposition: break complex questions into sub-queries

### 22. LLM Engineering (Beyond Prompt Writing)

- Fine-tuning: LoRA, QLoRA, full fine-tuning — when each applies
- RLHF / DPO / ORPO — alignment techniques
- Distillation: large model → small model
- Inference optimization: KV cache, speculative decoding, batching
- Token economics: cost optimization without quality loss
- Model routing: cheap model for easy queries, expensive for hard ones
- Guardrails: input/output classifiers, PII detection

### 23. Data Engineering Instincts

- Idempotency in every pipeline (your plan already enforces this — know *why*)
- Exactly-once vs at-least-once processing semantics
- Backpressure and flow control
- Schema evolution and backward compatibility
- Data lineage: which source produced which chunk produced which answer
- Deduplication strategies: content hashing, MinHash, SimHash

### 24. Communication & Influence

- Writing RFCs / design documents
- Explaining technical decisions to non-technical stakeholders
- Code review — giving and receiving
- Estimating work: breaking down unknowns, time-boxing research

---

## E. Things You Didn't Mention But Must Know

### 25. Networking Fundamentals (You're Building a Distributed System)

- TCP/IP, DNS resolution, TLS handshake
- HTTP/2 and gRPC — why some services use one over the other
- Load balancing: L4 vs L7, sticky sessions
- Connection pooling at the application level (your DB, Redis, Qdrant connections)
- Timeouts: connect, read, write — and why you need all three
- Circuit breaker pattern (Qdrant goes down — your API shouldn't crash)

### 26. Concurrency & Parallelism (Critical for RAG Performance)

- Thread vs process vs coroutine — and when your RAG pipeline uses each
- Race conditions in shared state (tenant config updates mid-query)
- Semaphores for limiting concurrent LLM/embedding API calls
- Connection pool exhaustion under load
- Backpressure: what happens when ingestion overwhelms embedding API rate limits

### 27. Caching (You'll Need It — The Plan Never Mentions It)

- Cache invalidation strategies: TTL, event-driven, versioned keys
- What to cache in RAG: embeddings of repeated queries, LLM responses for identical contexts
- Cache layers: in-process (LRU) → Redis → CDN
- Cache stampede prevention: locking, probabilistic early expiration

### 28. Cost Awareness (AI Products Live or Die by Unit Economics)

- Embedding API costs: batch vs single, caching to avoid re-embedding
- LLM API costs: prompt tokens vs completion tokens, context window optimization
- Vector DB costs: storage, QPS, collection count
- Cloud Run pricing: CPU allocation, min instances, cold starts
- Cloud SQL pricing: instance size, storage, connections

### 29. Post-AI World Positioning

- Understanding AI agents: tool use, planning, memory — building systems that agents consume
- API-first thinking: your RAG system becomes a tool that agents call
- Human-in-the-loop patterns: when the system should defer to a human
- Evaluation-driven development: this skill transfers to *any* AI system
- Infrastructure for AI: the people who build the plumbing outlast the hype
- Composability: building systems from interchangeable components (your ports & adapters approach is exactly this)
