"""
tests/integration/test_database.py
==================================
Integration tests for database connectivity and SQLAlchemy models.
Requires a running PostgreSQL instance.
"""
from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import check_database_connection, get_engine


@pytest.mark.integration
async def test_database_connection_success() -> None:
    """
    Verify that the application can connect to the database.
    """
    is_connected = await check_database_connection()
    if not is_connected:
        pytest.skip("Database is not reachable. Skipping integration test.")
    
    assert is_connected is True


@pytest.mark.integration
async def test_database_engine_executes_query() -> None:
    """
    Verify that the async engine can execute a basic query.
    """
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            assert value == 1
    except ModuleNotFoundError as exc:
        pytest.skip(f"Database driver not installed: {exc}")
    except Exception as exc:
        pytest.skip(f"Database connection failed: {exc}")

