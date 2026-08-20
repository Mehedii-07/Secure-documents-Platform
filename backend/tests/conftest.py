"""
tests/conftest.py
=================
Pytest fixtures and configuration shared across all tests.

Sets required environment variables before any app module is imported,
so pydantic-settings doesn't fail with 'Field required' errors.
These are test-safe dummy values — no real credentials.
"""
from __future__ import annotations

import os

# ------------------------------------------------------------------ #
# Set required env vars BEFORE any app import
# (pydantic-settings reads env at module load time)
# ------------------------------------------------------------------ #
os.environ.setdefault("POSTGRES_PASSWORD", "test_password_for_pytest")
os.environ.setdefault("JWT_SECRET_KEY", "test_jwt_secret_key_long_enough_for_validation_pytest")
os.environ.setdefault("OPENAI_API_KEY", "sk-test-placeholder")
os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("DEBUG", "false")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    """
    Session-scoped TestClient.
    One instance shared across the entire test session for performance.
    """
    return TestClient(app, raise_server_exceptions=True)
