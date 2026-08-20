# ============================================================
# create_github_issues.ps1
# Creates all planned GitHub Issues for the Compliance Platform
#
# Usage:
#   $env:GITHUB_TOKEN = "ghp_yourtoken"
#   .\scripts\create_github_issues.ps1
# ============================================================

param(
    [string]$Token = $env:GITHUB_TOKEN,
    [string]$Repo = "Mehedii-07/Secure-documents-Platform"
)

if (-not $Token) {
    Write-Error "Set GITHUB_TOKEN env var first: `$env:GITHUB_TOKEN = 'ghp_yourtoken'"
    exit 1
}

$Headers = @{
    Authorization = "Bearer $Token"
    Accept        = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

$BaseUrl = "https://api.github.com/repos/$Repo/issues"

$Issues = @(
    @{
        title  = "[Issue #1] Project Setup"
        body   = "## Goal`nBootstrap the monorepo skeleton.`n`n## Branch`n``feature/project-setup```n`n## Tasks`n- [x] Git init on main`n- [x] .gitignore, .env.example, README`n- [x] docker-compose.yml + override`n- [x] Backend: FastAPI shell, config, database, AI abstraction`n- [x] Frontend: React + Vite + TS scaffold`n- [x] Alembic skeleton`n- [x] CI workflow (GitHub Actions)`n- [x] Health check endpoint + 4 unit tests`n`n## Status`n✅ **Completed**"
        labels = @("setup", "completed")
    },
    @{
        title  = "[Issue #2] Database Setup"
        body   = "## Goal`nSet up the database foundation with Alembic migrations and core model infrastructure.`n`n## Branch`n``feature/database-setup```n`n## Tasks`n- [ ] Enable pgvector, uuid-ossp extensions (confirmed via init-db.sql)`n- [ ] Create TimestampMixin (created_at, updated_at)`n- [ ] Create UUIDMixin`n- [ ] First Alembic migration (baseline)`n- [ ] Verify `alembic upgrade head` runs cleanly`n- [ ] Integration test: DB connection + migration`n`n## Depends On`n#1 Project Setup"
        labels = @("database", "backend")
    },
    @{
        title  = "[Issue #3] Backend Architecture"
        body   = "## Goal`nEstablish the full layered backend architecture (routes, services, repositories, schemas).`n`n## Branch`n``feature/backend-architecture```n`n## Tasks`n- [ ] Create `app/api/` structure with router registration`n- [ ] Create `app/api/dependencies/` (auth, pagination, db)`n- [ ] Create `app/schemas/base.py` (common response schemas)`n- [ ] Create `app/services/base.py`  `n- [ ] Create `app/repositories/base.py`  `n- [ ] Register v1 router in main.py`n- [ ] Standardize error response format`n- [ ] Add pagination helper`n`n## Depends On`n#2 Database Setup"
        labels = @("backend", "architecture")
    },
    @{
        title  = "[Issue #4] Frontend Architecture"
        body   = "## Goal`nEstablish the full React frontend architecture with routing, layout, and component library.`n`n## Branch`n``feature/frontend-architecture```n`n## Tasks`n- [ ] React Router setup with route config`n- [ ] Layout component (sidebar, topbar, content area)`n- [ ] Design system components: Button, Input, Card, Badge, Spinner`n- [ ] API service layer structure`n- [ ] Auth context / store scaffold`n- [ ] Toast notification system`n- [ ] Error boundary`n- [ ] Loading skeleton components`n`n## Depends On`n#3 Backend Architecture"
        labels = @("frontend", "architecture")
    },
    @{
        title  = "[Issue #5] Authentication"
        body   = "## Goal`nImplement full JWT authentication: register, login, logout, refresh tokens, password hashing.`n`n## Branch`n``feature/auth-login-registration```n`n## API Endpoints`n- `POST /api/v1/auth/register`  `n- `POST /api/v1/auth/login`  `n- `POST /api/v1/auth/logout`  `n- `POST /api/v1/auth/refresh`  `n- `POST /api/v1/auth/change-password`  `n`n## Tasks`n- [ ] User model + migration`n- [ ] Password hashing (bcrypt)`n- [ ] JWT access + refresh token generation`n- [ ] Token blacklist (Redis)`n- [ ] Auth dependency for protected routes`n- [ ] Rate limiting on login`n- [ ] Frontend: Login page, Register page`n- [ ] Frontend: Token storage + refresh logic`n- [ ] Tests: register, login, wrong password, expired token`n`n## Depends On`n#4 Frontend Architecture"
        labels = @("auth", "security", "backend", "frontend")
    },
    @{
        title  = "[Issue #6] User Profile"
        body   = "## Goal`nUser profile view and update functionality.`n`n## Branch`n``feature/user-profile```n`n## API Endpoints`n- `GET /api/v1/users/me`  `n- `PATCH /api/v1/users/me`  `n- `GET /api/v1/users/{id}` (admin only)`n`n## Tasks`n- [ ] Profile schema (name, email, avatar_url, etc.)`n- [ ] Profile update endpoint`n- [ ] Frontend: Profile page`n- [ ] Avatar upload (to storage)`n- [ ] Tests`n`n## Depends On`n#5 Authentication"
        labels = @("backend", "frontend")
    },
    @{
        title  = "[Issue #7] Roles (RBAC)"
        body   = "## Goal`nImplement Role-Based Access Control with predefined roles.`n`n## Branch`n``feature/rbac-roles```n`n## Roles`n- ADMIN`n- COMPLIANCE_MANAGER`n- HR_MANAGER`n- EMPLOYEE`n`n## Tasks`n- [ ] Role model + migration`n- [ ] Assign role to user on registration (default: EMPLOYEE)`n- [ ] Role-check dependency`n- [ ] Admin: list/assign roles`n- [ ] Tests: role enforcement`n`n## Depends On`n#6 User Profile"
        labels = @("auth", "security", "backend")
    },
    @{
        title  = "[Issue #8] Permissions"
        body   = "## Goal`nGranular permission system layered on top of roles.`n`n## Branch`n``feature/permissions```n`n## Permissions`n`DOCUMENT_VIEW`, `DOCUMENT_UPLOAD`, `DOCUMENT_DOWNLOAD`, `DOCUMENT_EDIT`, `DOCUMENT_DELETE`, `DOCUMENT_SHARE`, `AI_QUERY`, `COMPLIANCE_MANAGE`, `USER_MANAGE``n`n## Tasks`n- [ ] Permission model + migration`n- [ ] Role-Permission mapping table`n- [ ] Permission-check dependency`n- [ ] Admin UI: manage role permissions`n- [ ] Tests`n`n## Depends On`n#7 Roles"
        labels = @("auth", "security", "backend")
    },
    @{
        title  = "[Issue #9] Multi-Factor Authentication (MFA)"
        body   = "## Goal`nOptional TOTP-based MFA for user accounts.`n`n## Branch`n``feature/mfa```n`n## API Endpoints`n- `POST /api/v1/auth/mfa/enable`  `n- `POST /api/v1/auth/mfa/verify`  `n- `POST /api/v1/auth/mfa/disable`  `n`n## Tasks`n- [ ] TOTP secret generation (pyotp)`n- [ ] QR code generation`n- [ ] MFA verification on login`n- [ ] Backup codes`n- [ ] Frontend: MFA setup page`n- [ ] Tests`n`n## Depends On`n#8 Permissions"
        labels = @("auth", "security")
    },
    @{
        title  = "[Issue #10] Document Upload"
        body   = "## Goal`nSecure document upload with file validation and background processing trigger.`n`n## Branch`n``feature/document-upload```n`n## API Endpoints`n- `POST /api/v1/documents` (multipart/form-data)`n`n## Tasks`n- [ ] Document model + migration`n- [ ] File type validation (PDF, DOCX, TXT, PNG, JPG)`n- [ ] File size validation (max from config)`n- [ ] Safe server-side file identifier generation`n- [ ] Store file via StorageService`n- [ ] Enqueue background processing task`n- [ ] Return 202 Accepted with document ID`n- [ ] Frontend: Upload page with drag-and-drop`n- [ ] Tests: upload, invalid type, oversized`n`n## Depends On`n#8 Permissions"
        labels = @("documents", "backend", "frontend")
    },
    @{
        title  = "[Issue #11] Storage Service"
        body   = "## Goal`nAbstracted storage service: local for dev, S3-compatible for prod.`n`n## Branch`n``feature/storage-service```n`n## Tasks`n- [ ] `StorageService` abstract base class`n- [ ] `LocalStorageProvider` implementation`n- [ ] `S3StorageProvider` implementation (boto3)`n- [ ] Factory: resolve from `STORAGE_BACKEND` setting`n- [ ] Prevent path traversal attacks`n- [ ] Secure signed-URL generation for downloads`n- [ ] Tests: store, retrieve, delete, path traversal attempt`n`n## Depends On`n#10 Document Upload"
        labels = @("backend", "security", "infrastructure")
    },
    @{
        title  = "[Issue #12] Document CRUD"
        body   = "## Goal`nFull CRUD for documents with authorization enforcement.`n`n## Branch`n``feature/document-crud```n`n## API Endpoints`n- `GET /api/v1/documents` (paginated, filterable)`n- `GET /api/v1/documents/{id}`  `n- `PATCH /api/v1/documents/{id}`  `n- `DELETE /api/v1/documents/{id}`  `n- `GET /api/v1/documents/{id}/download`  `n`n## Tasks`n- [ ] List with pagination, filtering, sorting`n- [ ] Document-level authorization check`n- [ ] Secure download (signed URL or streaming)`n- [ ] Soft delete / archive`n- [ ] Audit log on every action`n- [ ] Frontend: Documents list page, document detail page`n- [ ] Tests`n`n## Depends On`n#11 Storage Service"
        labels = @("documents", "backend", "frontend")
    },
    @{
        title  = "[Issue #13] Categories & Tags"
        body   = "## Goal`nOrganize documents with categories and tags.`n`n## Branch`n``feature/categories-tags```n`n## Tasks`n- [ ] Category model + migration`n- [ ] Tag model + migration`n- [ ] Assign categories/tags on upload and via PATCH`n- [ ] Filter documents by category/tag`n- [ ] Admin: manage categories`n- [ ] Frontend: category/tag UI`n- [ ] Tests`n`n## Depends On`n#12 Document CRUD"
        labels = @("documents", "backend", "frontend")
    },
    @{
        title  = "[Issue #14] Document Versioning"
        body   = "## Goal`nTrack document versions — upload new version, view history, restore.`n`n## Branch`n``feature/document-versioning```n`n## Tasks`n- [ ] DocumentVersion model + migration`n- [ ] Upload new version endpoint`n- [ ] Version history endpoint`n- [ ] Download specific version`n- [ ] Frontend: version history UI`n- [ ] Tests`n`n## Depends On`n#12 Document CRUD"
        labels = @("documents", "backend")
    },
    @{
        title  = "[Issue #15] Text Extraction"
        body   = "## Goal`nExtract plain text from uploaded documents as the first background processing step.`n`n## Branch`n``feature/text-extraction```n`n## Tasks`n- [ ] PDF text extraction (pypdf / pdfplumber)`n- [ ] DOCX extraction (python-docx)`n- [ ] TXT passthrough`n- [ ] Image OCR (pytesseract) — basic support`n- [ ] Store extracted text in Document model`n- [ ] Update document status: PENDING → EXTRACTING → EXTRACTED`n- [ ] Celery task: `extract_text`  `n- [ ] Tests`n`n## Depends On`n#10 Document Upload"
        labels = @("ai", "backend", "celery")
    },
    @{
        title  = "[Issue #16] AI Document Classification"
        body   = "## Goal`nClassify documents into categories using the AI provider abstraction.`n`n## Branch`n``feature/ai-document-classification```n`n## Tasks`n- [ ] Celery task: `classify_document`  `n- [ ] Call `AIProvider.classify_document(text, categories)`  `n- [ ] Store classification result on Document`n- [ ] Update document status`n- [ ] Frontend: show classification badge`n- [ ] Tests (mock AIProvider)`n`n## Depends On`n#15 Text Extraction"
        labels = @("ai", "backend")
    },
    @{
        title  = "[Issue #17] AI Document Summarization"
        body   = "## Goal`nGenerate AI summaries for uploaded documents.`n`n## Branch`n``feature/ai-document-summary```n`n## API Endpoints`n- `POST /api/v1/documents/{id}/summarize`  `n- `GET /api/v1/documents/{id}/summary`  `n`n## Tasks`n- [ ] Celery task: `summarize_document`  `n- [ ] Prompt engineering for summarization`n- [ ] Store summary on Document`n- [ ] Frontend: summary panel on document detail`n- [ ] Tests (mock AIProvider)`n`n## Depends On`n#16 AI Classification"
        labels = @("ai", "backend", "frontend")
    },
    @{
        title  = "[Issue #18] Metadata Extraction"
        body   = "## Goal`nExtract structured metadata from documents (title, author, dates, key entities).`n`n## Branch`n``feature/metadata-extraction```n`n## Tasks`n- [ ] Celery task: `extract_metadata`  `n- [ ] Prompt: extract title, author, creation date, expiry date, key topics`n- [ ] Validate structured AI response before storing`n- [ ] Store metadata (JSONB field or dedicated model)`n- [ ] Important-date / expiry-date detection`n- [ ] Frontend: metadata display panel`n- [ ] Tests`n`n## Depends On`n#17 AI Summarization"
        labels = @("ai", "backend")
    },
    @{
        title  = "[Issue #19] PII Detection"
        body   = "## Goal`nDetect personally identifiable information (PII) in document text.`n`n## Branch`n``feature/pii-detection```n`n## Tasks`n- [ ] Celery task: `detect_pii`  `n- [ ] Prompt: detect names, emails, phone numbers, SSNs, financial data, addresses`n- [ ] Store PII detection result (types found, risk level)`n- [ ] Do NOT store raw PII content — only presence and type`n- [ ] Flag high-risk documents`n- [ ] Alert compliance manager on high-risk PII`n- [ ] Frontend: PII badge + warning`n- [ ] Tests`n`n## Depends On`n#18 Metadata Extraction"
        labels = @("ai", "security", "compliance")
    },
    @{
        title  = "[Issue #20] Embeddings"
        body   = "## Goal`nChunk documents and generate vector embeddings stored in pgvector.`n`n## Branch`n``feature/embeddings```n`n## Tasks`n- [ ] DocumentChunk model + migration (with vector column)`n- [ ] Text chunking strategy (sliding window, overlap)`n- [ ] Batch embedding via `AIProvider.embed_batch()`  `n- [ ] Store embeddings in pgvector`n- [ ] Celery task: `embed_document`  `n- [ ] IVFFlat / HNSW index on embedding column`n- [ ] Tests`n`n## Depends On`n#15 Text Extraction"
        labels = @("ai", "database", "backend")
    },
    @{
        title  = "[Issue #21] Semantic Search"
        body   = "## Goal`nVector similarity search over authorized document chunks.`n`n## Branch`n``feature/semantic-search```n`n## API Endpoints`n- `GET /api/v1/search?q=...`  `n`n## Tasks`n- [ ] Embed query via AIProvider`n- [ ] Filter by authorized document IDs (SECURITY: before vector search)`n- [ ] pgvector similarity search with `<=>` operator`n- [ ] Return ranked results with document metadata`n- [ ] Frontend: Search page with results`n- [ ] Tests (mock embedding)`n`n## Security Note`nAuthorization filter MUST be applied before vector search — never after.`n`n## Depends On`n#20 Embeddings"
        labels = @("ai", "search", "security")
    },
    @{
        title  = "[Issue #22] RAG Document Chat"
        body   = "## Goal`nRAG-based AI chat over authorized documents with source citations.`n`n## Branch`n``feature/rag-document-chat```n`n## API Endpoints`n- `POST /api/v1/ai/query`  `n- `GET /api/v1/ai/queries` (history)`n`n## Pipeline`n```\nUser → Auth → Authorization → Authorized Doc IDs\n→ Query Embedding → Vector Search (filtered)\n→ Context Construction → LLM → Answer + Sources\n```\n`n## Tasks`n- [ ] AIQuery model + migration`n- [ ] Authorized chunk retrieval only`n- [ ] Context window management (token budget)`n- [ ] Source citations in response`n- [ ] Store query + answer + sources`n- [ ] Frontend: AI Chat page`n- [ ] Tests (mock LLM + embeddings)`n`n## Security Note`nNever allow unauthorized document chunks into LLM context.`n`n## Depends On`n#21 Semantic Search"
        labels = @("ai", "security", "backend", "frontend")
    },
    @{
        title  = "[Issue #23] Compliance Requirements"
        body   = "## Goal`nDefine and manage compliance requirements (rules that documents must satisfy).`n`n## Branch`n``feature/compliance-requirements```n`n## API Endpoints`n- `POST /api/v1/compliance/requirements`  `n- `GET /api/v1/compliance/requirements`  `n- `PATCH /api/v1/compliance/requirements/{id}`  `n- `DELETE /api/v1/compliance/requirements/{id}`  `n`n## Tasks`n- [ ] ComplianceRequirement model + migration`n- [ ] Rule fields: document category, required, expiry rules, approval status needed`n- [ ] CRUD endpoints (COMPLIANCE_MANAGER role required)`n- [ ] Frontend: Compliance requirements management page`n- [ ] Tests`n`n## Depends On`n#8 Permissions"
        labels = @("compliance", "backend", "frontend")
    },
    @{
        title  = "[Issue #24] Compliance Checking"
        body   = "## Goal`nAutomatically evaluate compliance requirements against existing documents.`n`n## Branch`n``feature/compliance-checking```n`n## Tasks`n- [ ] ComplianceCheck model + migration`n- [ ] Celery task: `run_compliance_check`  `n- [ ] Check: does required document exist? Is it current? Is it expired?`n- [ ] Result: COMPLIANT / NEEDS_REVIEW / NON_COMPLIANT`n- [ ] Store result + timestamp`n- [ ] Trigger check on document upload/update`n- [ ] Tests`n`n## Depends On`n#23 Compliance Requirements"
        labels = @("compliance", "backend", "celery")
    },
    @{
        title  = "[Issue #25] Compliance Score"
        body   = "## Goal`nCalculate and expose an overall compliance score.`n`n## Branch`n``feature/compliance-score```n`n## API Endpoints`n- `GET /api/v1/compliance/score`  `n- `GET /api/v1/compliance/score/breakdown`  `n`n## Tasks`n- [ ] Score calculation: (compliant checks / total checks) * 100`n- [ ] Breakdown by category`n- [ ] Historical score tracking`n- [ ] Frontend: Compliance dashboard with score gauge`n- [ ] Tests`n`n## Depends On`n#24 Compliance Checking"
        labels = @("compliance", "frontend")
    },
    @{
        title  = "[Issue #26] Compliance Alerts"
        body   = "## Goal`nAutomated alerts for compliance violations, expiring documents, and missing requirements.`n`n## Branch`n``feature/compliance-alerts```n`n## Tasks`n- [ ] ComplianceAlert model + migration`n- [ ] Alert types: MISSING_DOCUMENT, EXPIRING_SOON, EXPIRED, NON_COMPLIANT`n- [ ] Celery beat task: daily compliance scan`n- [ ] Notification delivery (in-app + email)`n- [ ] Mark alerts as read/resolved`n- [ ] Frontend: Alerts page with filters`n- [ ] Tests`n`n## Depends On`n#25 Compliance Score"
        labels = @("compliance", "backend", "frontend")
    },
    @{
        title  = "[Issue #27] Document-Level Security"
        body   = "## Goal`nPer-document access control — restrict which users/roles can view each document.`n`n## Branch`n``feature/document-level-security```n`n## Tasks`n- [ ] DocumentPermission model + migration`n- [ ] Share document with specific user or role`n- [ ] Revoke document access`n- [ ] Authorization check in all document endpoints`n- [ ] RAG pipeline: filter chunks by user doc permissions`n- [ ] Frontend: Document sharing UI`n- [ ] Tests: unauthorized access attempt`n`n## Depends On`n#12 Document CRUD"
        labels = @("security", "documents")
    },
    @{
        title  = "[Issue #28] Audit Logs"
        body   = "## Goal`nImmutable audit trail of all security-sensitive actions.`n`n## Branch`n``feature/audit-logs```n`n## Tasks`n- [ ] AuditLog model + migration`n- [ ] Log: user, action, resource, timestamp, IP address`n- [ ] Actions: login, logout, upload, download, delete, permission-change, AI query`n- [ ] Never log passwords, tokens, or document content`n- [ ] Admin: audit log viewer with filtering`n- [ ] Frontend: Audit logs page`n- [ ] Tests`n`n## Security Note`nAudit logs must be append-only. No update or delete operations.`n`n## Depends On`n#7 Roles"
        labels = @("security", "backend", "frontend")
    },
    @{
        title  = "[Issue #29] Security Monitoring"
        body   = "## Goal`nDetect and respond to suspicious activity: brute force, unusual access, failed logins.`n`n## Branch`n``feature/security-monitoring```n`n## Tasks`n- [ ] Failed login counter per user (Redis)`n- [ ] Account lockout after N failed attempts`n- [ ] Suspicious access detection (unusual hour, unusual IP)`n- [ ] Security alert model + migration`n- [ ] Admin: security dashboard`n- [ ] Rate limiting middleware (slowapi)`n- [ ] Tests`n`n## Depends On`n#28 Audit Logs"
        labels = @("security", "backend")
    },
    @{
        title  = "[Issue #30] Testing Suite"
        body   = "## Goal`nComprehensive test coverage across all backend modules.`n`n## Branch`n``feature/testing```n`n## Tasks`n- [ ] Integration tests with real PostgreSQL (pytest + testcontainers or Docker)`n- [ ] Auth flow tests (register → login → protected endpoint)`n- [ ] Document upload + processing pipeline tests`n- [ ] RAG pipeline tests (mock AI, real DB)`n- [ ] Compliance check tests`n- [ ] Security tests: unauthorized access, path traversal, rate limits`n- [ ] Coverage report (target: 80%+)`n- [ ] Frontend: Vitest component tests`n`n## Depends On`nAll previous issues"
        labels = @("testing")
    },
    @{
        title  = "[Issue #31] Docker & Local Development"
        body   = "## Goal`nFully working `docker-compose up --build` experience for local development.`n`n## Branch`n``feature/docker```n`n## Tasks`n- [ ] Verify all services start with health checks passing`n- [ ] Add Celery Flower to docker-compose (monitoring UI)`n- [ ] Add Nginx as reverse proxy in production compose`n- [ ] Create `docker-compose.prod.yml`  `n- [ ] Volume mounts for dev hot-reload`n- [ ] Seed script for initial admin user`n- [ ] README: complete local setup walkthrough`n- [ ] Test: `docker-compose up` from clean state`n`n## Depends On`nAll previous issues"
        labels = @("devops", "infrastructure")
    },
    @{
        title  = "[Issue #32] CI/CD Pipeline"
        body   = "## Goal`nFull GitHub Actions CI/CD: lint, test, build, and optional deploy.`n`n## Branch`n``feature/ci-cd```n`n## Tasks`n- [ ] CI: backend lint (ruff) + type check (mypy)`n- [ ] CI: backend tests with PostgreSQL service`n- [ ] CI: frontend lint (ESLint) + build (Vite)`n- [ ] CD: build and push Docker images to registry`n- [ ] CD: optional deploy step (Railway / Render / self-hosted)`n- [ ] Branch protection rules on main`n- [ ] Required status checks before merge`n`n## Depends On`n#30 Testing, #31 Docker"
        labels = @("devops", "ci-cd")
    },
    @{
        title  = "[Issue #33] Monitoring & Observability"
        body   = "## Goal`nAdd structured logging, metrics, and health monitoring.`n`n## Branch`n``feature/monitoring```n`n## Tasks`n- [ ] Structured JSON logging (structlog)`n- [ ] Request ID middleware`n- [ ] Prometheus metrics endpoint`n- [ ] Celery task monitoring (Flower)`n- [ ] Health check endpoint enhancements (Redis, Celery status)`n- [ ] Error tracking (Sentry integration — optional)`n- [ ] Frontend: basic admin system status page`n`n## Depends On`n#31 Docker, #32 CI/CD"
        labels = @("devops", "infrastructure")
    }
)

$Labels = @("setup","completed","database","backend","architecture","frontend","auth","security","documents","ai","celery","search","compliance","testing","devops","infrastructure","ci-cd")

# Create labels first
Write-Host "Creating labels..."
foreach ($label in $Labels) {
    $colors = @{
        "setup"="0075ca"; "completed"="0e8a16"; "database"="e4e669";
        "backend"="d93f0b"; "architecture"="1d76db"; "frontend"="bfdadc";
        "auth"="b60205"; "security"="e11d48"; "documents"="0075ca";
        "ai"="7057ff"; "celery"="fef2c0"; "search"="c5def5";
        "compliance"="f9d0c4"; "testing"="c2e0c6"; "devops"="bfd4f2";
        "infrastructure"="d4c5f9"; "ci-cd"="ffd33d"
    }
    $color = $colors[$label]
    $body = @{ name=$label; color=$color; description="" } | ConvertTo-Json
    try {
        Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/labels" `
            -Method POST -Headers $Headers -Body $body -ContentType "application/json" | Out-Null
        Write-Host "  Label created: $label"
    } catch {
        Write-Host "  Label exists or error: $label"
    }
}

# Create issues
Write-Host "`nCreating issues..."
$created = 0
foreach ($issue in $Issues) {
    $body = @{
        title  = $issue.title
        body   = $issue.body
        labels = $issue.labels
    } | ConvertTo-Json -Depth 5

    try {
        $result = Invoke-RestMethod -Uri $BaseUrl `
            -Method POST -Headers $Headers -Body $body -ContentType "application/json"
        Write-Host "  ✅ Created: #$($result.number) $($issue.title)"
        $created++
        Start-Sleep -Milliseconds 500  # avoid rate limiting
    } catch {
        Write-Host "  ❌ Failed: $($issue.title) — $($_.Exception.Message)"
    }
}

Write-Host "`nDone! Created $created / $($Issues.Count) issues."
Write-Host "View at: https://github.com/$Repo/issues"
