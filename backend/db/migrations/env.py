"""Alembic environment file.

Generated programmatically for Aperture project.
"""
from __future__ import with_statement

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Add project root to sys.path so backend modules are importable
sys.path.append(str(Path(__file__).resolve().parents[3]))

from backend.db.models import Base  # noqa: E402
from backend.core.config import settings  # noqa: E402

# Alembic Config object, provides access to the .ini file values.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Metadata for 'autogenerate'
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = f"sqlite:///./{settings.SQLITE_PATH}"
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        {
            "sqlalchemy.url": f"sqlite:///./{settings.SQLITE_PATH}",
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
