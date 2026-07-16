# backend/ — FastAPI Backend

## Folder Purpose
The Python 3.11 backend of KAI-Flow: a FastAPI application that stores workflows, compiles them
into LangGraph state machines, executes them (sync or SSE streaming), and exposes the full REST
API used by the frontend, the widget, and external callers.

## What This Folder Contains
- `main.py` — **entry point**. Creates the FastAPI app (title "Agent-Flow V2"), mounts `/widget`
  static assets, registers CORS + logging middleware, includes every API router under
  `/{API_START}/{API_VERSION}` (= `/api/v1`), defines `/health`, `/info`, `/` endpoints, and runs
  Uvicorn (HTTPS if `SSL_KEYFILE`/`SSL_CERTFILE` exist). The `lifespan` handler discovers nodes,
  initializes the engine, sets up tracing, checks DB health, and starts/stops the Kafka
  reconciliation loop.
- `app/` — the application package (see subfolder docs below).
- `migrations/` — `database_setup.py` schema creation script → [migrations/MIGRATIONS.md](migrations/MIGRATIONS.md)
- `scripts/` — workflow export/import CLI tools → [scripts/SCRIPTS.md](scripts/SCRIPTS.md)
- `tests/` — pytest tests → [tests/TESTS.md](tests/TESTS.md)
- `requirements.txt` — pinned dependencies (FastAPI, SQLAlchemy 2, LangChain/LangGraph 1.x,
  pgvector, APScheduler, confluent-kafka, document processing, etc.)
- `encrypt_env.py` — helper to encrypt `.env` values (works with `app/core/env_encryption.py`).
- `create_webhook_tables.py` — one-off helper that creates webhook tables.
- `webhook-http-integration-guide.md` — maintainer-written guide for webhook/HTTP integration.
- `docker-compose.yml` — a backend-local compose file (the canonical dev stack is the repo-root
  `docker-compose.yml`).
- `README.md` — extensive upstream backend documentation (architecture, node system, API).
- `cert/` — expected location for self-signed SSL certs (`cert.pem`, `key.pem`); not committed.

## Important Files
`main.py`, `app/core/engine.py`, `app/core/graph_builder/__init__.py`, `app/nodes/base.py`,
`app/core/node_registry.py`, `app/core/constants.py`, `migrations/database_setup.py`.

## File-by-File Explanation (app/ package)
| Subfolder | Role | Doc |
|---|---|---|
| `app/api/` | REST routers (one file per resource) | [app/api/API.md](app/api/API.md) |
| `app/auth/` | JWT/Keycloak auth dependencies | [app/auth/AUTH.md](app/auth/AUTH.md) |
| `app/core/` | Engine, graph builder, DB, config, security, logging | [app/core/CORE.md](app/core/CORE.md) |
| `app/middleware/` | Request/DB/security logging middleware | [app/middleware/MIDDLEWARE.md](app/middleware/MIDDLEWARE.md) |
| `app/models/` | SQLAlchemy ORM models | [app/models/MODELS.md](app/models/MODELS.md) |
| `app/nodes/` | Workflow node classes (the plugin system) | [app/nodes/NODES.md](app/nodes/NODES.md) |
| `app/routes/` | Export bundle route helpers | [app/routes/ROUTES.md](app/routes/ROUTES.md) |
| `app/schemas/` | Pydantic request/response schemas | [app/schemas/SCHEMAS.md](app/schemas/SCHEMAS.md) |
| `app/services/` | Business logic incl. AI Builder & memory | [app/services/SERVICES.md](app/services/SERVICES.md) |

## Relationship With Other Folders
- Serves the API consumed by `client/` and `widget/` (widget assets are also served at `/widget`).
- Built into a Docker image by the root `Dockerfile` and `export-docker/Dockerfile.backend`.
- Reads configuration from the repo-root `.env`.

## How This Folder Fits Into the AI Workflow
This folder **is** the AI workflow engine: flow JSON in → validation → LangGraph compilation →
execution with LangChain components → results/streaming out. See [../docs/ai-workflow.md](../docs/ai-workflow.md).

## Developer Notes
- Run locally with `python backend/main.py` (Uvicorn reload enabled).
- The DB schema must exist first: `python backend/migrations/database_setup.py`.
- Startup **fails** without `CREDENTIAL_MASTER_KEY` and a healthy database connection.
- API prefix convention comes from `app/core/constants.py`: `API_START="api"`, `API_VERSION="v1"`.

## Things to Be Careful About
- The root `Dockerfile` CMD (`uvicorn app.main:app`) does not match the real module (`main:app`);
  docker-compose overrides it — don't rely on the bare image.
- `ROOT_PATH` (e.g. `/api/kai`) is applied as FastAPI `root_path`; the Vite dev proxy rewrites
  `/api/kai` — changing either side breaks the frontend proxy.
- CORS is `allow_origins=["*"]` in `main.py` — tighten before production exposure.
- Timers router is intentionally registered twice (versioned + unversioned paths).

## Related Documentation Files
[../CLAUDE.md](../CLAUDE.md) · [../docs/backend.md](../docs/backend.md) ·
[../docs/api.md](../docs/api.md) · [../docs/ai-workflow.md](../docs/ai-workflow.md) ·
[../docs/database.md](../docs/database.md) · upstream [README.md](README.md)
