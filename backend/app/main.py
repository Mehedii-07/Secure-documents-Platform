"""
app/main.py
===========
FastAPI application entry point.

Responsibilities:
- Create and configure the FastAPI app instance
- Register middleware (CORS, etc.)
- Register API routers
- Define application lifespan (startup / shutdown)
- Expose the health check endpoint
"""
from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import check_database_connection

logger = logging.getLogger(__name__)
settings = get_settings()


# ------------------------------------------------------------------ #
# Application lifespan (replaces deprecated @app.on_event)
# ------------------------------------------------------------------ #
@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    """
    Code before yield → startup.
    Code after yield → shutdown.
    """
    logger.info(
        "Starting %s v%s [env=%s]", settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV
    )

    # Verify database connectivity at startup (non-fatal — allows health check to report status)
    db_ok = await check_database_connection()
    if db_ok:
        logger.info("Database connection: OK")
    else:
        logger.warning("Database connection: FAILED — proceeding anyway (check .env)")

    yield

    logger.info("Shutting down %s", settings.APP_NAME)


# ------------------------------------------------------------------ #
# FastAPI app instance
# ------------------------------------------------------------------ #
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-Powered Secure Document & Compliance Platform API. "
        "Provides document management, AI analysis, semantic search, and compliance tracking."
    ),
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
    # Only expose Swagger UI in non-production environments
    # In production, set DEBUG=false to disable docs
)


# ------------------------------------------------------------------ #
# Middleware
# ------------------------------------------------------------------ #
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Any) -> Any:
    """Add X-Process-Time header to every response for performance monitoring."""
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{duration:.4f}s"
    return response


# ------------------------------------------------------------------ #
# Health check endpoint
# ------------------------------------------------------------------ #
@app.get(
    f"{settings.API_V1_PREFIX}/health",
    tags=["Health"],
    summary="Health check",
    description=(
        "Returns the current health status of the API and its dependencies. "
        "Used by Docker health checks, load balancers, and monitoring tools."
    ),
)
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.

    Returns:
        200 with status "ok" if the service is healthy.
        200 with status "degraded" if some dependencies are unhealthy
        (the service still responds but may have limited functionality).
    """
    db_healthy = await check_database_connection()

    status = "ok" if db_healthy else "degraded"

    return {
        "status": status,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "dependencies": {
            "database": "ok" if db_healthy else "unavailable",
        },
    }


# ------------------------------------------------------------------ #
# API v1 routers (registered as they are implemented in future issues)
# ------------------------------------------------------------------ #
# from app.api.v1.router import api_v1_router
# app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
#
# Routers are added issue by issue:
# Issue #5  → auth router
# Issue #10 → documents router
# Issue #22 → ai/query router
# Issue #23 → compliance router


# ------------------------------------------------------------------ #
# Global exception handlers
# ------------------------------------------------------------------ #
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Convert unhandled ValueErrors to 400 responses."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "type": "validation_error"},
    )


@app.exception_handler(PermissionError)
async def permission_error_handler(request: Request, exc: PermissionError) -> JSONResponse:
    """Convert unhandled PermissionErrors to 403 responses."""
    return JSONResponse(
        status_code=403,
        content={"detail": "Access denied.", "type": "permission_error"},
    )
