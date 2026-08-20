# ============================================================
# Backend Dockerfile — multi-stage build
# ============================================================
# Stage 1: builder — install Python dependencies
# Stage 2: runtime — lean production image
# ============================================================

# ---- Stage 1: Builder ----
FROM python:3.11-slim AS builder

# Install system dependencies needed to compile C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy requirements first (Docker layer caching — only reinstalled on requirements change)
COPY requirements/base.txt requirements/base.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements/base.txt


# ---- Stage 2: Runtime ----
FROM python:3.11-slim AS runtime

LABEL maintainer="Platform Team"
LABEL description="AI-Powered Secure Document & Compliance Platform — Backend API"

# Install runtime system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home --shell /bin/false appuser

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=appuser:appgroup app/ ./app/
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup alembic.ini ./

# Create storage directory for local file uploads
RUN mkdir -p /app/storage/local && \
    chown -R appuser:appgroup /app/storage

# Switch to non-root user
USER appuser

# Expose API port
EXPOSE 8000

# Health check using the /api/v1/health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default command — production server
# Override in docker-compose.override.yml for dev with --reload
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "2", \
     "--log-level", "info"]
