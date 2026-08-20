"""
tests/test_health.py
====================
Health check endpoint tests.

These tests use FastAPI's TestClient and mock the database connection
so no real Postgres instance is required.

Marks:
  - unit: fast, no external dependencies
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #

@pytest.fixture()
def client() -> TestClient:
    """Return a synchronous TestClient for the FastAPI app."""
    return TestClient(app, raise_server_exceptions=True)


# ------------------------------------------------------------------ #
# Tests
# ------------------------------------------------------------------ #

@pytest.mark.unit
def test_health_check_ok(client: TestClient) -> None:
    """
    Health check returns 200 with status 'ok' when database is reachable.
    """
    with patch(
        "app.main.check_database_connection",
        new_callable=AsyncMock,
        return_value=True,
    ):
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "0.1.0"
    assert body["dependencies"]["database"] == "ok"


@pytest.mark.unit
def test_health_check_degraded_when_db_unavailable(client: TestClient) -> None:
    """
    Health check returns 200 with status 'degraded' when database is unreachable.
    The service should still respond — it reports degradation rather than crashing.
    """
    with patch(
        "app.main.check_database_connection",
        new_callable=AsyncMock,
        return_value=False,
    ):
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["dependencies"]["database"] == "unavailable"


@pytest.mark.unit
def test_health_check_returns_process_time_header(client: TestClient) -> None:
    """Response includes X-Process-Time header from the middleware."""
    with patch(
        "app.main.check_database_connection",
        new_callable=AsyncMock,
        return_value=True,
    ):
        response = client.get("/api/v1/health")

    assert "x-process-time" in response.headers


@pytest.mark.unit
def test_health_check_json_content_type(client: TestClient) -> None:
    """Response Content-Type is application/json."""
    with patch(
        "app.main.check_database_connection",
        new_callable=AsyncMock,
        return_value=True,
    ):
        response = client.get("/api/v1/health")

    assert "application/json" in response.headers["content-type"]
