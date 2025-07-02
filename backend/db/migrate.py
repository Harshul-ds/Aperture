"""Utility to apply Alembic migrations programmatically."""
from pathlib import Path
from alembic import command
from alembic.config import Config


def run_migrations() -> None:  # noqa: D401
    """Upgrade database to the latest head revision."""
    cfg_path = Path(__file__).resolve().parent.parent.parent / "alembic.ini"
    alembic_cfg = Config(str(cfg_path))
    command.upgrade(alembic_cfg, "head")
