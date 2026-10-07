"""Minimal FastAPI app — the Foundation / Module A integration seam.

Foundation owns the real bootstrap, the /health and /ready routers, and get_db().
This app exists so the Module M database infrastructure is runnable and verifiable
end to end until Foundation lands. It must not import `workers` so it also runs
under plain uvicorn.

What Module M provides to Foundation:
- db.resolve_target / db.engine_for / db.session_scope  -> connection lifecycle
- health.readiness / health.check_database               -> readiness hook
"""

from __future__ import annotations

from dataclasses import replace

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from db import engine_for, get_binding, resolve_target, session_scope
from health import check_database
from infra_probe import InfraProbe
from settings import Settings, load_settings

# Loaded once per isolate. Defaults are valid even when no env vars are present.
_settings: Settings = load_settings()

app = FastAPI(title="Flutter Wars — Module M infrastructure", version="0.2.0")


def _request_settings(request: Request) -> Settings:
    app_env = get_binding(request.scope.get("env"), "APP_ENV")
    if app_env and str(app_env) != _settings.app_env:
        return replace(_settings, app_env=str(app_env).strip().lower())
    return _settings


@app.get("/health")
async def health() -> dict[str, object]:
    """Process is alive. Must not touch the database."""
    return {"status": "ok", "env": _settings.app_env}


@app.get("/ready")
async def ready(request: Request):
    """Readiness: can we use required dependencies? Delegates to Module M's hook."""
    status = check_database(request.scope.get("env"), _request_settings(request))
    payload: dict[str, object] = {
        "status": "ready" if status.ok else "not_ready",
        "dependencies": [status.to_dict()],
    }
    if not status.ok:
        return JSONResponse(status_code=503, content=payload)
    return payload


@app.get("/db/roundtrip")
async def db_roundtrip(request: Request, label: str = "probe") -> dict[str, object]:
    """Dev/infra only: exercise transaction + INSERT/SELECT via SQLModel.

    No DDL here: the harness table is created by `scripts/dev_setup.py` or the
    test fixtures. Real schema is owned by Alembic migrations.
    """
    settings = _request_settings(request)
    target = resolve_target(request.scope.get("env"), settings)
    with engine_for(target, settings) as engine:
        with session_scope(engine) as session:
            row = InfraProbe(label=label)
            session.add(row)
            session.commit()
            session.refresh(row)
            total = len(session.exec(select(InfraProbe)).all())
            return {"id": row.id, "label": row.label, "rows": total, "source": target.source}


@app.get("/sqlmodel-selftest")
async def sqlmodel_selftest() -> dict[str, object]:
    """Prove sync SQLModel works in-runtime via in-memory SQLite (no network)."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    try:
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            session.add(InfraProbe(label="selftest"))
            session.commit()
            rows = session.exec(select(InfraProbe)).all()
            return {"sqlmodel": "ok", "rows": len(rows), "label": rows[0].label}
    finally:
        engine.dispose()
