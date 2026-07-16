# Database

PostgreSQL 15 with the **pgvector** extension. Async access via SQLAlchemy 2 + asyncpg
([backend/app/core/database.py](../backend/app/core/database.py)); pool settings via `DB_POOL_*`
env vars.

## Schema management
No Alembic tree (Alembic is installed but unused). The schema is created/verified by
[backend/migrations/database_setup.py](../backend/migrations/MIGRATIONS.md):
```bash
python backend/migrations/database_setup.py   # requires .env; CREATE_DATABASE=true creates the DB too
```
Docker compose runs it automatically before starting Uvicorn.

## Table groups (~29 tables; source of truth: `expected_tables` in database_setup.py and
[backend/app/models/](../backend/app/models/MODELS.md))

| Group | Tables |
|---|---|
| Identity & org | `users`, `user_credentials`, `roles`, `organization`, `organization_user`, `login_method`, `login_activity` |
| Workflows | `workflows` (holds `flow_data` JSON), `workflow_templates` |
| Execution | `workflow_executions`, `execution_checkpoints` |
| Conversation | `chat_message`, `memories` |
| Node system | `node_registry`, `node_configurations` |
| Access | `api_keys` |
| Scheduling | `scheduled_jobs`, `job_executions` |
| Webhooks | `webhook_endpoints`, `webhook_events` |
| Vectors (RAG) | `vector_collections`, `vector_documents` |
| Documents (RAG) | `document_collections`, `documents`, `document_chunks`, `document_access_logs`, `document_versions` |
| Sharing | `external_workflows` |

## Security notes
- `user_credentials` values are Fernet-encrypted with `CREDENTIAL_MASTER_KEY` — losing that key
  makes stored credentials unrecoverable.
- `DATABASE_URL`/credentials in `.env` may themselves be encrypted
  (`backend/app/core/env_encryption.py` + `backend/encrypt_env.py`).

## Change checklist
1. Model file in `backend/app/models/` → 2. import in `models/__init__.py` →
3. add to `expected_tables` in `migrations/database_setup.py` → 4. re-run the script →
5. update [MODELS.md](../backend/app/models/MODELS.md) + this file.

## Related
[backend.md](backend.md) · [configuration.md](configuration.md) ·
[ai-workflow.md](ai-workflow.md) (which tables the engine touches)
