# backend/app/routes/ — Export Route Helpers

## Folder Purpose
Support code for the workflow **export** feature (producing distributable bundles). Despite the
generic name, this folder currently only concerns export; regular REST routing lives in
`app/api/`.

## What This Folder Contains / File-by-File Explanation
- `export.py` — export route logic.
- `export/services.py` — export bundle assembly services.
- `export/utils.py` — export helpers.
- `__init__.py` — package init.

## Important Files
`export/services.py`.

## Relationship With Other Folders
- The mounted router is `app/api/export.py` (included in `backend/main.py` under `/api/v1`);
  this folder provides its implementation details.
- Related CLI tooling: `backend/scripts/export_workflows.py` / `import_workflows.py`;
  deployable output consumed by `export-docker/` (import bundle).

## How This Folder Fits Into the AI Workflow
Packages workflows (and credential *structure* without secret values) so they can be moved to
another KAI-Flow instance and executed there.

## Developer Notes
- Keep bundle format changes in sync with `backend/scripts/workflow_bundle_utils.py` and the
  import side (`export-docker/import_bundle/`).

## Things to Be Careful About
- Exports must never contain decrypted credential values.
- Naming collision potential: `app/api/export.py` vs `app/routes/export.py` — check imports
  carefully when editing.

## Related Documentation Files
[../api/API.md](../api/API.md) · [../../scripts/SCRIPTS.md](../../scripts/SCRIPTS.md) ·
[../../../export-docker/EXPORT-DOCKER.md](../../../export-docker/EXPORT-DOCKER.md)
