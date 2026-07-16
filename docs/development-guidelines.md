# Development Guidelines

How to make changes to KAI-Flow safely. Complements [../CONTRIBUTING.md](../CONTRIBUTING.md)
(upstream contribution process + node-type philosophy) and the mandatory
**Documentation Reference Rules** in [../CLAUDE.md](../CLAUDE.md).

## Before any change
1. Read [../CLAUDE.md](../CLAUDE.md).
2. Read the folder-level `.md` of each folder you'll touch (see
   [project-structure.md](project-structure.md) for the map).
3. Read the relevant doc here (api / database / ai-workflow / configuration / deployment).
4. If your change conflicts with the documented architecture, raise it before coding.
5. Update the affected docs in the same change set.

## Recipes

### Add a workflow node (most common contribution)
1. New file in `backend/app/nodes/<category>/`; subclass `ProviderNode` / `ProcessorNode` /
   `TerminatorNode` / `MemoryNode`.
2. Define `metadata` (`NodeMetadata` with `NodeProperty` inputs/outputs) — this auto-generates
   the frontend form.
3. Implement `execute()`; keep outputs JSON-serializable.
4. Restart backend; verify the node appears on the canvas and runs.
5. If AI Builder should generate it: check `backend/app/services/ai_builder/schema_compiler.py`
   assumptions and `backend/tests/`.
6. Update [NODES.md](../backend/app/nodes/NODES.md).
Details: [NODES.md](../backend/app/nodes/NODES.md) · [../CONTRIBUTING.md](../CONTRIBUTING.md).

### Add an API endpoint
Router in `backend/app/api/` → service in `backend/app/services/` → schemas in
`backend/app/schemas/` → `include_router` in `backend/main.py` → mirror types in
`client/app/types/api.ts` + service in `client/app/services/` → update
[API.md](../backend/app/api/API.md) and [api.md](api.md).

### Change the database
Model → `models/__init__.py` → `expected_tables` in `migrations/database_setup.py` → run it →
update [MODELS.md](../backend/app/models/MODELS.md) + [database.md](database.md).
Remember: no Alembic — destructive changes need a manual plan.

### Frontend feature
Respect the layering: page → component → store → service → api-client. New node field types go
in `client/app/components/node/fields/`. Update the relevant client folder docs.

## Testing & quality gates
- Backend: `cd backend && python -m pytest tests/` (currently AI-Builder-only — add tests for
  what you touch).
- Frontend: `npm run typecheck && npm run lint && npm run test` in `client/` (lint has a
  zero-warnings policy).
- Manual verification for canvas/engine changes: build a small workflow, execute it, watch node
  statuses and the log panel.

## Git/PR process (from CONTRIBUTING.md + repo history)
- Open an issue first; fork/branch (`feat/...`, `bug_fix/...` naming appears in history); PRs
  target `main` (default working branch here is `dev`); include screenshots/GIFs for UI changes;
  add/adjust tests where applicable.

## Security rules
- Never log or export decrypted credentials; anything credential-related goes through
  `app/core/encryption.py` / `credential_provider.py`.
- Treat `CodeNode` (executes user Python) and webhook/Kafka input paths as security-sensitive.
- Don't commit `.env`, certs, or real keys.

## Pitfall quick-list
- Root Dockerfile CMD is stale (compose overrides it).
- Timers router is intentionally mounted twice.
- Two config sources on the frontend (build-time vs `public/config.js`).
- Node `name` values are stored in saved workflows — renaming breaks them.
- `CREDENTIAL_MASTER_KEY` required at boot; DB must be reachable or startup raises.

## Related
Every folder-level `.md` (map in [project-structure.md](project-structure.md)) ·
[../CLAUDE.md](../CLAUDE.md)
