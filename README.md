# AI-Powered Secure Document & Compliance Platform

[![CI](https://github.com/YOUR_ORG/compliance-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_ORG/compliance-platform/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade, AI-powered document management and compliance platform featuring RAG-based document chat, PII detection, semantic search, and automated compliance scoring.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Environment Configuration](#environment-configuration)
- [Development](#development)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)

---

## Features

- 🔐 **Authentication & RBAC** — JWT + refresh tokens, role-based access control, optional MFA
- 📄 **Document Management** — upload, version, categorize, tag, and archive documents
- 🤖 **AI Document Intelligence** — classification, summarization, metadata extraction, PII detection
- 🔍 **RAG Chat** — ask questions about your documents; answers cite source documents
- 📊 **Compliance Dashboard** — track requirements, scores, alerts, and expired documents
- 🛡️ **Security** — document-level authorization, audit logs, sensitive-data detection
- 🔄 **Background Processing** — Celery + Redis for non-blocking document processing

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite |
| Backend | Python 3.11, FastAPI, Pydantic v2 |
| ORM / Migrations | SQLAlchemy 2, Alembic |
| Database | PostgreSQL 16 + pgvector |
| Cache / Queue | Redis, Celery |
| AI Abstraction | OpenAI (swappable via `AIProvider`) |
| Storage | Local (dev) → S3-compatible (prod) |
| Auth | JWT (python-jose), bcrypt |
| DevOps | Docker, Docker Compose, GitHub Actions |

---

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the full component diagram and ADRs.

```
┌──────────────┐     HTTPS      ┌─────────────────────────────┐
│  React SPA   │ ──────────────▶│  Nginx (reverse proxy)      │
└──────────────┘                └──────────┬──────────────────┘
                                           │
                              ┌────────────▼────────────────┐
                              │   FastAPI Backend (uvicorn)  │
                              │  /api/v1/...                 │
                              └──┬───────────┬──────────────┘
                                 │           │
                    ┌────────────▼──┐   ┌────▼─────────────┐
                    │  PostgreSQL   │   │  Redis / Celery   │
                    │  + pgvector   │   │  (async workers)  │
                    └───────────────┘   └──────────────────┘
```

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/) v2 (bundled with Docker Desktop)
- Git

### 1. Clone

```bash
git clone https://github.com/YOUR_ORG/compliance-platform.git
cd compliance-platform
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env — fill in POSTGRES_PASSWORD, JWT_SECRET_KEY, OPENAI_API_KEY, etc.
```

### 3. Start

```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/api/v1/docs |
| API Docs (ReDoc) | http://localhost:8000/api/v1/redoc |

---

## Environment Configuration

See [`.env.example`](.env.example) for all available variables with descriptions.  
**Never commit `.env` to version control.**

Key variables:

| Variable | Description |
|---|---|
| `POSTGRES_PASSWORD` | Database password — use a strong random value |
| `JWT_SECRET_KEY` | JWT signing key — generate with `python -c "import secrets; print(secrets.token_hex(64))"` |
| `AI_PROVIDER` | `openai` \| `anthropic` \| `azure_openai` \| `ollama` |
| `OPENAI_API_KEY` | Required when `AI_PROVIDER=openai` |
| `STORAGE_BACKEND` | `local` (dev) or `s3` (prod) |

---

## Development

### Backend only

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements/dev.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend only

```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

```bash
cd backend
alembic upgrade head          # Apply all migrations
alembic revision --autogenerate -m "description"  # Generate new migration
alembic downgrade -1          # Rollback one step
```

---

## Testing

### Backend

```bash
cd backend
pytest tests/ -v --tb=short
```

### Frontend

```bash
cd frontend
npm run test
```

---

## Project Structure

```
compliance-platform/
├── backend/
│   ├── app/
│   │   ├── api/           # HTTP layer (routes, dependencies)
│   │   ├── core/          # Config, security, database
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── repositories/  # Database access
│   │   ├── workers/       # Celery tasks
│   │   ├── ai/            # AI provider abstraction
│   │   └── main.py
│   ├── alembic/           # Database migrations
│   ├── tests/
│   ├── requirements/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/           # Axios client, service functions
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Route-level pages
│   │   ├── hooks/         # Custom React hooks
│   │   ├── store/         # State management
│   │   └── types/         # TypeScript interfaces
│   ├── Dockerfile
│   └── nginx.conf
├── docs/
│   └── architecture.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker-compose.yml
├── docker-compose.override.yml
├── .env.example
└── README.md
```

---

## Roadmap

Issues are implemented incrementally. See the master development plan for the full sequence.

| Issue | Status |
|---|---|
| #1 Project Setup | ✅ Done |
| #2 Database Setup | ⏳ Next |
| #3 Backend Architecture | ⏳ Planned |
| #4 Frontend Architecture | ⏳ Planned |
| #5 Authentication | ⏳ Planned |
| … | … |

---

## License

MIT
