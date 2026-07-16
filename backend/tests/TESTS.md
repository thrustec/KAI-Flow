# backend/tests/ — Backend Tests

## Folder Purpose
Pytest test suite for the backend. Coverage is currently narrow: only the AI Builder service
modules are tested.

## What This Folder Contains / File-by-File Explanation
- `test_validator.py` — tests `app/services/ai_builder/validator.py`
  (`validate_structure`: missing ids/types, edge integrity, etc.).
- `test_diff_engine.py` — tests `app/services/ai_builder/diff_engine.py` (changeset computation
  for workflow edit mode).
- `test_handle_types.py` — tests `app/services/ai_builder/handle_types.py` (connection handle
  typing rules).

## Important Files
All three are peers.

## Relationship With Other Folders
- Tests target `app/services/ai_builder/` only. Engine (`app/core/`), API and nodes have **no**
  tests here.
- CI (`.github/workflows/ci.yml`, `backend-ci.yml`) runs backend tests with a Postgres service.

## How This Folder Fits Into the AI Workflow
Guards the AI-generated-workflow feature: structural validity of generated graphs and edit diffs.

## Developer Notes
- Run: `cd backend && python -m pytest tests/` (pytest + pytest-asyncio are pinned in
  `requirements.txt`).
- These tests are pure-unit (no DB needed).

## Things to Be Careful About
- Changing node metadata/handles can break `test_handle_types.py` and AI Builder generation —
  update tests together with `app/services/ai_builder/schema_compiler.py`.
- When adding engine or API tests, keep them DB-independent or document required services.

## Related Documentation Files
[../BACKEND.md](../BACKEND.md) · [../app/services/SERVICES.md](../app/services/SERVICES.md) ·
[../../docs/development-guidelines.md](../../docs/development-guidelines.md)
