"""
alembic/env.py
==============
Alembic migration environment.

- Uses synchronous psycopg2 connection (required by Alembic)
- Reads DATABASE_URL from pydantic-settings (never hardcoded)
- Imports all models so Alembic can detect schema changes via --autogenerate
"""
from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure the backend/ directory is on sys.path so `app` can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# ------------------------------------------------------------------ #
# Import application settings and Base metadata
# ------------------------------------------------------------------ #
from app.core.config import get_settings  # noqa: E402
from app.core.database import Base  # noqa: E402

# Import ALL models here so Alembic's autogenerate can detect them.
# Add new model imports as you create them in future issues:
#
# from app.models.user import User                   # Issue #2
# from app.models.document import Document           # Issue #10
# from app.models.compliance import ComplianceCheck  # Issue #24

settings = get_settings()

# ------------------------------------------------------------------ #
# Alembic Config object (provides access to alembic.ini values)
# ------------------------------------------------------------------ #
config = context.config

# Set the database URL dynamically from Settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNC)

# Configure Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = Base.metadata


# ------------------------------------------------------------------ #
# Offline mode — generates SQL script without connecting to DB
# ------------------------------------------------------------------ #
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generate SQL to stdout)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,           # Detect column type changes
        compare_server_default=True, # Detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()


# ------------------------------------------------------------------ #
# Online mode — connects to DB and runs migrations
# ------------------------------------------------------------------ #
def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connect to DB and apply)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Don't pool connections during migrations
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
