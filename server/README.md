# Backend — Module M: Infrastructure, Deployment & Database Operations

Python / FastAPI backend for the GDG VIT Chennai Flutter Workshop platform,
deployed on Cloudflare Python Workers with Hyperdrive to Neon PostgreSQL.

Runtime path:

```
Cloudflare Python Worker -> FastAPI -> sync SQLModel/SQLAlchemy -> psycopg
    -> Cloudflare Hyperdrive -> Neon PostgreSQL
```

Module M owns **infrastructure only**: deployment configuration, Hyperdrive,
environment/secrets configuration, the shared migration workflow, CI/CD, staging,
recovery, and operational documentation. It owns **no business entities** and no
participant API.

> **Deployment prerequisite:** the current Worker bundle is ~34.24 MiB uncompressed
> / ~7.66 MiB gzip, which exceeds the Workers **Free** compressed limit (3 MiB) and
> therefore **requires the Workers Paid plan** (10 MiB compressed). Free-plan
> compatibility is not claimed. See [docs/deployment.md](docs/deployment.md).

## Documentation index

| Topic | Document |
| --- | --- |
| Local development | [docs/local-development.md](docs/local-development.md) |
| Environment variables | [docs/environment-reference.md](docs/environment-reference.md) |
| Database connection architecture (incl. Neon + concurrency decision) | [docs/database-architecture.md](docs/database-architecture.md) |
| Migration workflow (+ how modules contribute) | [docs/migrations.md](docs/migrations.md) |
| Deployment (Cloudflare + Hyperdrive + ordering) | [docs/deployment.md](docs/deployment.md) |
| Recovery, rollback, backups (RPO/RTO) | [docs/recovery.md](docs/recovery.md) |
| Secret rotation | [docs/secret-rotation.md](docs/secret-rotation.md) |
| Troubleshooting runbook | [docs/runbook.md](docs/runbook.md) |
| Competition-day checklist | [docs/competition-runbook.md](docs/competition-runbook.md) |

## Where Module M ends and Foundation (Module A) begins

- **Foundation / Module A owns**: FastAPI bootstrap, module registration, shared
  configuration abstraction, `get_db()` / session abstraction, health/readiness API.
- **Module M owns**: engine/session factory, target resolution, readiness probe
  hook, deployment config, migrations, CI/CD.

`src/app.py` in this repository is a **temporary infrastructure-verification seam**
(FastAPI + `/health` + `/ready` + probe endpoints). It is not the production
bootstrap and must be removed once Foundation lands. Module M core modules are
`src/settings.py`, `src/db.py`, `src/health.py`, `src/worker.py`, and `migrations/`.

## Layout

```
server/
  src/            settings.py db.py health.py infra_probe.py app.py worker.py
  migrations/     env.py metadata_registry.py versions/
  tests/          unit + integration + migration tests
  scripts/        dev_setup.py migrate.sh deploy.sh verify_deployment.sh loadtest.py
  docs/           operational documentation (see index above)
  wrangler.jsonc  dev/staging/production Worker + Hyperdrive config
  alembic.ini     migration config (URL supplied via env.py)
```
