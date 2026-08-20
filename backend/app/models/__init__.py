"""
app/models/__init__.py
======================
Export all SQLAlchemy models here so Alembic can import them from a single location.
"""
from __future__ import annotations

from app.models.user import User

__all__ = ["User"]
