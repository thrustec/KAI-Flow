# backend/migrations/ — Database Setup

## Folder Purpose
Database schema creation and verification. There is **no Alembic migration tree** here (Alembic
is in requirements but unused as of 2026-07); the schema is managed imperatively by one script.

## What This Folder Contains / File-by-File Explanation
- `database_setup.py` — the `DatabaseSetup` class:
  - loads `.env` (supports encrypted values via `app/core/env_encryption.py`),
  - optionally creates the database itself (`CREATE_DATABASE=true`),
  - creates all tables from the SQLAlchemy models (`app/models/`),
  - maintains an `expected_tables` list (~29 tables: users, workflows, workflow_executions,
    chat_message, memories, api_keys, scheduled_jobs, webhook_endpoints, vector_collections,
    documents, external_workflows, …),
  - logs to `database_setup.log` (a copy may appear at repo root when run from there).

## Important Files
`database_setup.py` (the only file).

## Relationship With Other Folders
- Reads models from `app/models/`; run by `docker-compose.yml` before Uvicorn starts
  (`python migrations/database_setup.py`) and by developers during local setup.

## How This Folder Fits Into the AI Workflow
Provisions the persistence layer for workflows, executions, chat, memory, vectors — without it
the backend refuses to start (DB health check in `main.py` lifespan raises).

## Developer Notes
- Local run: `python backend/migrations/database_setup.py` (or `python -m migrations.database_setup`
  from `backend/`).
- New model? Add it to `app/models/__init__.py` **and** to `expected_tables` here.

## Things to Be Careful About
- The script is additive/verifying — it is not a versioned migration system; destructive schema
  changes need manual SQL or a move to Alembic.
- Requires the pgvector extension for vector tables (PostgreSQL 15 + pgvector).

## Related Documentation Files
[../BACKEND.md](../BACKEND.md) · [../app/models/MODELS.md](../app/models/MODELS.md) ·
[../../docs/database.md](../../docs/database.md)
