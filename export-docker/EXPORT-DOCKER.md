# export-docker/ — Distributable Docker Bundle

## Folder Purpose
A self-contained Docker Compose stack for shipping KAI-Flow (plus exported workflows) to another
environment — e.g. delivering a built assistant to a customer. Distinct from the repo-root
`docker-compose.yml`, which is the development stack.

## What This Folder Contains / File-by-File Explanation
- `docker-compose.yml` — three services on a `kaifusion-network`:
  - `postgres` (postgres:15-alpine, healthchecked),
  - `backend` (built from `Dockerfile.backend`, port 23056→8000; runs
    `python -m migrations.database_setup` then Uvicorn; mounts `./import_bundle` into the
    container and imports workflow bundles at startup),
  - frontend (built from `Dockerfile.frontend`).
- `Dockerfile.backend` / `Dockerfile.frontend` — image builds using the repo as build context
  (`context: ..`).
- `.env.example` — environment template for this stack.
- `import_bundle/` — drop exported workflow bundles here (see its `README.md`); consumed at
  backend startup.

## Important Files
`docker-compose.yml` (orchestrates everything), `import_bundle/README.md`.

## Relationship With Other Folders
- Builds from `backend/` and `client/`; bundles are produced by `backend/scripts/`
  (`export_workflows.py`) / the export API (`backend/app/api/export.py`).

## How This Folder Fits Into the AI Workflow
The "deploy your assistant elsewhere" path: export workflows on the design instance → place the
bundle in `import_bundle/` → `docker compose up --build` on the target machine → workflows are
imported and runnable (credentials must be re-entered, since exports contain no secret values).

## Developer Notes
- Usage: `cd export-docker && docker compose up --build`.
- Default credentials in the compose file (`kaifusion`/`kaifusion_secret`, placeholder
  SECRET_KEY/CREDENTIAL_MASTER_KEY) are for testing — change for real deployments.

## Things to Be Careful About
- Container/user naming here uses the legacy "kaifusion" branding — expected, don't "fix" it
  casually (volumes/networks depend on the names).
- Keep this compose in sync with backend env requirements (e.g. it must always pass
  `CREDENTIAL_MASTER_KEY`, or the backend exits at startup).

## Related Documentation Files
[../CLAUDE.md](../CLAUDE.md) · [../docs/deployment.md](../docs/deployment.md) ·
[../backend/scripts/SCRIPTS.md](../backend/scripts/SCRIPTS.md) ·
[../USER_GUIDE.md](../USER_GUIDE.md)
