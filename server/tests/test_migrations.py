"""Migration workflow tests (shared Alembic history).

Gated on a real Postgres URL. In CI the same commands run against a Neon branch.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parents[1]
ALEMBIC = str(Path(sys.executable).parent / "alembic")


def _alembic(*args: str, database_url: str | None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if database_url is None:
        env.pop("DATABASE_URL", None)
        env.pop("SPIKE_DATABASE_URL", None)
    else:
        env["DATABASE_URL"] = database_url
    return subprocess.run(
        [ALEMBIC, *args], cwd=SERVER_DIR, env=env, capture_output=True, text=True
    )


@pytest.fixture()
def clean_db(postgres_url: str):
    _alembic("downgrade", "base", database_url=postgres_url)
    yield postgres_url
    _alembic("downgrade", "base", database_url=postgres_url)


def test_upgrade_and_current(clean_db):
    up = _alembic("upgrade", "head", database_url=clean_db)
    assert up.returncode == 0, up.stderr
    current = _alembic("current", database_url=clean_db)
    assert "0001_baseline" in current.stdout
    assert "(head)" in current.stdout


def test_history_lists_baseline(clean_db):
    result = _alembic("history", database_url=clean_db)
    assert result.returncode == 0
    assert "0001_baseline" in result.stdout


def test_check_reports_no_drift(clean_db):
    _alembic("upgrade", "head", database_url=clean_db)
    result = _alembic("check", database_url=clean_db)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "No new upgrade operations detected" in (result.stdout + result.stderr)


def test_downgrade_clears_version(clean_db):
    _alembic("upgrade", "head", database_url=clean_db)
    down = _alembic("downgrade", "base", database_url=clean_db)
    assert down.returncode == 0, down.stderr
    current = _alembic("current", database_url=clean_db)
    assert "0001_baseline" not in current.stdout


def test_missing_configuration_fails_clearly():
    result = _alembic("upgrade", "head", database_url=None)
    assert result.returncode != 0
    assert "DATABASE_URL" in (result.stdout + result.stderr)


def test_registry_has_no_feature_modules_yet():
    migrations_dir = SERVER_DIR / "migrations"
    sys.path.insert(0, str(migrations_dir))
    try:
        import metadata_registry

        assert metadata_registry.FEATURE_MODEL_MODULES == ()
    finally:
        sys.path.remove(str(migrations_dir))
