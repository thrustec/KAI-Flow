# Deployment

## 1. Dev stack — root [docker-compose.yml](../docker-compose.yml)
```bash
cp .env.example .env   # edit values
docker compose up -d
```
| Service | Image/Build | Ports | Notes |
|---|---|---|---|
| `db` | pgvector/pgvector:pg15 | 5432:5432 | volume `kai_db_data`; must be the pgvector-enabled image, not plain `postgres:15`, or `CREATE EXTENSION vector` fails |
| `kai-flow-backend` | root `Dockerfile` | `${BACKEND_PORT:-23056}`:8000 | command: `python migrations/database_setup.py && uvicorn main:app` |
| `kai-flow-frontend` | `client/Dockerfile` (target `production`) | 23058:3000 | `VITE_*` passed as build args |

URLs: frontend http://localhost:23058 · Swagger http://localhost:23056/docs

⚠️ The root `Dockerfile`'s own CMD (`uvicorn app.main:app`) is stale — compose overrides it; do
not run the bare backend image without overriding the command.

## 2. Local (no Docker except Postgres)
See [../CLAUDE.md](../CLAUDE.md) "Installation"/"Running" or [../README.md](../README.md):
venv + `pip install -r backend/requirements.txt` → run Postgres → `database_setup.py` →
`python backend/main.py` → `cd client && npm run dev`. Optional HTTPS: self-signed certs in
`backend/cert/` (both backend and Vite pick them up automatically).

## 3. Distributable stack — [export-docker/](../export-docker/EXPORT-DOCKER.md)
Ship a built assistant to another environment:
1. Export workflows (`python -m scripts.export_workflows …` or the export API/UI).
2. Put the bundle in `export-docker/import_bundle/`.
3. `cd export-docker && docker compose up --build` — imports bundles at startup.
Credentials travel structure-only (no secrets) and must be re-entered on the target.

## 4. Widget distribution
- npm: `@kaifusion/widget` (library build, `widget/vite.config.ts`).
- Script tag: `npm run build:standalone` → served by backend at `/widget/widget.js`
  (mount logic in [backend/main.py](../backend/main.py); env override `KAI_WIDGET_DIR`).

## 5. CI/CD — `.github/workflows/`
| Workflow | Purpose |
|---|---|
| `ci.yml` | Push/PR to main/develop: backend tests (Postgres 15 + Redis 7 services) + frontend jobs |
| `backend-ci.yml` / `frontend-ci.yml` | Component pipelines |
| `pr-checks.yml` | PR validation |
| `deploy.yml` / `staging.yml` | Deployment pipelines |

Note: CI provisions Redis, but no Redis usage is visible in backend code — This part is not
clearly defined in the project.

## Production hardening checklist (from code inspection)
- Replace placeholder `SECRET_KEY`, `CREDENTIAL_MASTER_KEY`, `MASTER_API_KEY`.
- Restrict CORS (`main.py` hardcodes `allow_origins=["*"]`).
- Set real `ALLOWED_ORIGINS`, disable `BACKEND_DEBUG`, consider `DATABASE_SSL=true`.
- Keycloak: `KEYCLOAK_VERIFY_SSL=true` with a real realm.

## Related
[configuration.md](configuration.md) · [../USER_GUIDE.md](../USER_GUIDE.md) (detailed ops guide:
hardware/network requirements, image loading, health verification) ·
[../client/DOCKER_README.md](../client/DOCKER_README.md)
