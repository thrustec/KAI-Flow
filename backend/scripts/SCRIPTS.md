# backend/scripts/ — Workflow Export/Import CLI

## Folder Purpose
Command-line tools to move workflows between KAI-Flow instances as distributable YAML bundles.

## What This Folder Contains / File-by-File Explanation
- `export_workflows.py` — exports workflows to a YAML bundle. Preserves workflow/credential
  UUIDs; exports credential *structure* with empty values (no secrets).
  ```bash
  cd backend
  python -m scripts.export_workflows --ids "uuid1,uuid2" --output ./export_bundle
  python -m scripts.export_workflows --user-email "admin@example.com" --output ./export_bundle
  ```
- `import_workflows.py` — imports such a bundle into a target instance (see its docstring for
  flags).
- `workflow_bundle_utils.py` — shared bundle (de)serialization helpers.
- `__init__.py` — package init.

## Important Files
All three scripts are peers; `workflow_bundle_utils.py` defines the bundle format.

## Relationship With Other Folders
- Reads/writes via `app/models/` + `app/core/database.py`.
- The REST counterpart is `app/api/export.py` + `app/routes/export/`.
- `export-docker/` consumes bundles: its backend container mounts `./import_bundle` and imports
  it at startup.

## How This Folder Fits Into the AI Workflow
Enables packaging a designed workflow (graph + credential placeholders) for deployment on another
instance — the "ship your assistant" path.

## Developer Notes
- Run from `backend/` with the venv active and `.env` reachable (scripts connect to the DB).

## Things to Be Careful About
- Bundle format changes must stay compatible with `app/routes/export/` and the import path used
  by `export-docker/`.
- Never add secret values to exports.

## Related Documentation Files
[../BACKEND.md](../BACKEND.md) · [../app/routes/ROUTES.md](../app/routes/ROUTES.md) ·
[../../export-docker/EXPORT-DOCKER.md](../../export-docker/EXPORT-DOCKER.md)
