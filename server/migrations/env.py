"""Alembic environment for the shared migration workflow (Module M).

Module M owns the migration execution process; it does NOT own business entities.
Feature modules own their SQLModel entities and register their model modules in
`metadata_registry.FEATURE_MODEL_MODULES` so Alembic can discover them without
Module M importing business code.

The database URL comes from the same settings the app uses (DATABASE_URL), or a
`-x db_url=...` override. Migrations run outside the Worker (locally or in CI),
directly against Neon — never through Hyperdrive.
"""

from __future__ import annotations

import pathlib
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Make both the app source and this migrations directory importable.
_HERE = pathlib.Path(__file__).resolve().parent
for _path in (_HERE.parent / "src", _HERE):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from metadata_registry import load_metadata  # noqa: E402
from settings import ConfigError, load_settings  # noqa: E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# All registered SQLModel metadata (empty of business tables until feature modules land).
target_metadata = load_metadata()

# Tables that are NOT part of the shared migration history.
# infra_probe is a dev/test harness table and must never be migrated.
EXCLUDED_TABLES = frozenset({"infra_probe"})


def include_object(object_, name, type_, reflected, compare_to):
    if type_ == "table" and name in EXCLUDED_TABLES:
        return False
    return True


def _database_url() -> str:
    override = context.get_x_argument(as_dictionary=True).get("db_url")
    if override:
        return override
    try:
        url = load_settings().database_url
    except ConfigError as exc:
        raise SystemExit(f"migration configuration error: {exc}") from exc
    if not url:
        raise SystemExit(
            "DATABASE_URL is required to run migrations (or pass -x db_url=...). "
            "Migrations target Neon directly and are never run inside the Worker."
        )
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _database_url()
    connectable = engine_from_config(
        configuration, prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
