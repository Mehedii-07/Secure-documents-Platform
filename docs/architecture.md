# Architecture Decision Records & Component Diagram

## AI-Powered Secure Document & Compliance Platform

---

## High-Level Component Architecture

```mermaid
graph TB
    subgraph Client["Client Layer"]
        SPA["React SPA<br/>(Vite, TypeScript)"]
    end

    subgraph Gateway["Gateway Layer"]
        NGINX["Nginx<br/>(reverse proxy / SPA host)"]
    end

    subgraph API["API Layer — FastAPI"]
        ROUTES["Routes<br/>/api/v1/*"]
        DEPS["Dependencies<br/>(auth, RBAC, pagination)"]
        ROUTES --> DEPS
    end

    subgraph Services["Service Layer"]
        AUTH_SVC["AuthService"]
        DOC_SVC["DocumentService"]
        AI_SVC["AIService"]
        COMP_SVC["ComplianceService"]
        STORE_SVC["StorageService"]
    end

    subgraph AI["AI Layer (abstracted)"]
        AI_BASE["AIProvider (ABC)"]
        OPENAI["OpenAIProvider"]
        ANTHROPIC["AnthropicProvider (future)"]
        AI_BASE --> OPENAI
        AI_BASE --> ANTHROPIC
    end

    subgraph Workers["Background Workers"]
        CELERY["Celery Workers"]
        TASKS["Tasks:<br/>text-extract, embed, classify"]
    end

    subgraph Data["Data Layer"]
        PG["PostgreSQL 16<br/>+ pgvector"]
        REDIS["Redis<br/>(broker + result backend)"]
        STORAGE["Storage<br/>(local → S3)"]
    end

    SPA --> NGINX
    NGINX --> ROUTES
    ROUTES --> AUTH_SVC
    ROUTES --> DOC_SVC
    ROUTES --> AI_SVC
    ROUTES --> COMP_SVC
    AI_SVC --> AI_BASE
    DOC_SVC --> STORE_SVC
    AUTH_SVC --> PG
    DOC_SVC --> PG
    AI_SVC --> PG
    COMP_SVC --> PG
    STORE_SVC --> STORAGE
    ROUTES --> CELERY
    CELERY --> TASKS
    CELERY --> REDIS
    TASKS --> PG
    TASKS --> AI_BASE
```

---

## Data Flow: Document Upload → AI Processing

```mermaid
sequenceDiagram
    actor User
    participant API as FastAPI
    participant Store as StorageService
    participant Queue as Redis/Celery
    participant Worker as Celery Worker
    participant AI as AIProvider
    participant DB as PostgreSQL

    User->>API: POST /api/v1/documents (multipart)
    API->>API: Validate file type & size
    API->>API: Check DOCUMENT_UPLOAD permission
    API->>Store: store(file) → storage_key
    API->>DB: INSERT Document (status=PENDING)
    API->>Queue: enqueue process_document(doc_id)
    API-->>User: 202 Accepted {doc_id}

    Queue->>Worker: process_document(doc_id)
    Worker->>Store: retrieve(storage_key)
    Worker->>Worker: extract_text(file)
    Worker->>AI: classify(text)
    Worker->>AI: summarize(text)
    Worker->>AI: extract_metadata(text)
    Worker->>AI: detect_pii(text)
    Worker->>AI: embed(chunks[])
    Worker->>DB: UPDATE Document + INSERT Chunks + Embeddings
    Worker->>DB: INSERT AuditLog
```

---

## Data Flow: RAG Query (Authorization-first)

```mermaid
sequenceDiagram
    actor User
    participant API as FastAPI
    participant Auth as AuthService
    participant Vec as pgvector
    participant AI as AIProvider
    participant DB as PostgreSQL

    User->>API: POST /api/v1/ai/query {question}
    API->>Auth: verify_token()
    Auth-->>API: user + roles
    API->>DB: get_authorized_document_ids(user_id)
    API->>Vec: similarity_search(query_embedding, doc_ids_filter)
    Vec-->>API: top_k chunks (only authorized)
    API->>AI: chat_completion(question, chunks_as_context)
    AI-->>API: answer + token_usage
    API->>DB: INSERT AIQuery (user_id, question, answer, sources)
    API-->>User: {answer, sources[{doc_id, title, chunk_excerpt}]}
```

---

## ADR-001 — Technology Choices

**Date**: 2026-08-20  
**Status**: Accepted

### Context
We need a production-ready AI document platform that is maintainable, testable, and demonstrable in a portfolio/interview context.

### Decisions

| Concern | Decision | Rationale |
|---|---|---|
| Backend language | Python 3.11 | Rich AI/ML ecosystem; FastAPI is production-proven |
| API framework | FastAPI | Async-native, OpenAPI auto-docs, Pydantic v2 integration |
| ORM | SQLAlchemy 2 (async) | Industry standard, full Alembic support |
| Database | PostgreSQL 16 | Rock-solid; pgvector extension for embeddings in same DB |
| Vector search | pgvector | Avoids external vector DB dependency; single DB to operate |
| Frontend | React 18 + Vite + TypeScript | Specified in requirements; fastest dev-server startup |
| Auth | JWT + refresh tokens | Stateless, scalable; bcrypt for password hashing |
| Background tasks | Celery + Redis | De-facto Python standard; supports retries, monitoring |
| AI abstraction | `AIProvider` ABC | Prevents vendor lock-in; OpenAI as first concrete impl |
| Storage abstraction | `StorageService` ABC | Local for dev, S3-compatible for prod; no code changes |
| Container | Docker + Docker Compose | Reproducible local environment; CI-friendly |

### Rejected Alternatives

| Alternative | Reason Rejected |
|---|---|
| Django | More opinionated; FastAPI better for API-first async backends |
| Separate vector DB (Pinecone, Weaviate) | Operational complexity; pgvector is sufficient at this scale |
| GraphQL | REST is simpler, better understood, sufficient for this use case |
| Next.js | React + Vite is lighter; SSR not needed for this SPA-style app |

---

## ADR-002 — AI Security: Authorization-First RAG

**Date**: 2026-08-20  
**Status**: Accepted

### Decision
The RAG pipeline **must** filter vector search results to only include chunks belonging to documents the requesting user is authorized to view.

Authorization happens **before** the vector search query, not after. The similarity search receives an explicit `doc_ids` filter.

### Rationale
Post-retrieval filtering is error-prone. If a bug allows an unauthorized chunk into the LLM context, sensitive information could leak into the AI's answer even if the chunk is later discarded. Filtering at the query level is the safe default.

### Implementation
```sql
-- Vector search with authorization filter (pgvector)
SELECT chunk_id, content, embedding <=> $query_embedding AS distance
FROM document_chunks
WHERE document_id = ANY($authorized_doc_ids)
ORDER BY distance
LIMIT $top_k;
```

---

## ADR-003 — No Secrets in Code

**Date**: 2026-08-20  
**Status**: Accepted

All secrets (database passwords, JWT keys, API keys) are loaded from environment variables via `pydantic-settings`.  
The `.env.example` file contains placeholder values and is committed.  
The `.env` file is in `.gitignore` and is never committed.
