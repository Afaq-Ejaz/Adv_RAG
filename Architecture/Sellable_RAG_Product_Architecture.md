# Sellable RAG — Product Architecture

## Architecture

```text
                    CLIENTS
                       │
                 API / AUTH
                       │
          ┌────────────┴────────────┐
          │                         │
     QUERY PLANE              KNOWLEDGE PLANE
          │                         │
   Query Understanding          Ingestion
          ↓                         ↓
   Permission Filter             Parsing
          ↓                         ↓
   Hybrid Retrieval             Chunking
   (Vector + Keyword)            Metadata
          ↓                         ↓
      Reranking                Embeddings
          ↓                         ↓
   Context Builder              Indexing
          ↓                         │
       LLM ◄───────────────────────┘
          ↓
   Citation / Grounding
          ↓
       Answer
```

## Cross-Cutting Systems

```text
Multi-tenancy
Versioning
Evaluation
Observability
Security
Cost tracking
```

## Core Infrastructure

```text
PostgreSQL     → users, tenants, documents, metadata
Object Storage → original documents
Search Engine  → keyword + vector search
Redis/Queue    → caching + async ingestion
Workers        → document processing
```

## Scalability Principle

Start as a **modular monolith**, while keeping clear internal boundaries:

```text
ingestion/
retrieval/
ranking/
generation/
auth/
tenancy/
evaluation/
observability/
```

Later, heavy components can be independently extracted into services.

## Product Vision

> **A scalable, multi-tenant enterprise knowledge infrastructure — with RAG as its intelligence layer.**

PostEx is the **first vertical/use case**, not the entire product.
