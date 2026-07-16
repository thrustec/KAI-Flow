# backend/app/models/ — SQLAlchemy ORM Models

## Folder Purpose
Async SQLAlchemy 2 ORM models for every database table. `backend/migrations/database_setup.py`
creates the schema from these models (there is no Alembic migration tree in the repo).

## What This Folder Contains / File-by-File Explanation
| File | Models | Purpose |
|---|---|---|
| `base.py` | `Base` | Declarative base |
| `user.py` | `User` | Accounts (local + Keycloak-provisioned) |
| `user_credential.py` | `UserCredential` | Encrypted third-party credentials (Fernet via core encryption) |
| `workflow.py` | `Workflow`, `WorkflowTemplate` | Workflows (`flow_data` JSON: nodes+edges), templates/marketplace |
| `execution.py` | `WorkflowExecution`, `ExecutionCheckpoint` | Execution history + checkpoints |
| `organization.py` | `Role`, `Organization`, `OrganizationUser` | Org/role structure |
| `auth.py` | `LoginMethod`, `LoginActivity` | Login providers + audit |
| `chat.py` | `ChatMessage` | Chat sessions/messages for workflow testing |
| `variable.py` | `Variable` | User/workflow variables |
| `memory.py` | `Memory` | Persistent conversation memory (`memories` table) |
| `node_configuration.py` | `NodeConfiguration` | Saved node configuration presets |
| `node_registry.py` | `NodeRegistry` | DB-backed node registry entries |
| `webhook.py` | `WebhookEndpoint`, `WebhookEvent` | Webhook config + received events |
| `api_key.py` | `APIKey` | Programmatic access keys |
| `scheduled_job.py` | `ScheduledJob`, `JobExecution` | Cron jobs + run history |
| `vector_collection.py` / `vector_document.py` | `VectorCollection`, `VectorDocument` | pgvector embedding storage |
| `document.py` | `DocumentCollection`, `Document`, `DocumentChunk`, `DocumentAccessLog`, `DocumentVersion` | RAG document management |
| `external_workflow.py` | `ExternalWorkflow` | Workflows shared from/to other instances |
| `__init__.py` | — | Imports/exports **all** models (required for schema creation) |

## Important Files
`workflow.py` and `execution.py` (core domain), `__init__.py` (registration).

## Relationship With Other Folders
- Used by `app/services/` (all DB access goes through services) and validated/serialized by
  `app/schemas/`.
- Table list mirrored in `backend/migrations/database_setup.py::expected_tables`.

## How This Folder Fits Into the AI Workflow
`Workflow.flow_data` stores the canvas graph the engine executes; `WorkflowExecution` records
each run; `Memory`/`ChatMessage` persist conversational state; vector/document models back RAG.

## Developer Notes
- Adding a model: create the file, add it to `__init__.py` **and** to `expected_tables` in
  `migrations/database_setup.py`, then re-run that script.
- Async sessions come from `app/core/database.py::get_db_session`.

## Things to Be Careful About
- Forgetting the `__init__.py` import means the table silently never gets created.
- pgvector columns require the `vector` extension (handled by database_setup).
- Some table names are singular (`variable`, `chat_message`), some plural (`workflows`) — check
  `expected_tables` rather than guessing.

## Related Documentation Files
[../../BACKEND.md](../../BACKEND.md) · [../services/SERVICES.md](../services/SERVICES.md) ·
[../schemas/SCHEMAS.md](../schemas/SCHEMAS.md) ·
[../../migrations/MIGRATIONS.md](../../migrations/MIGRATIONS.md) ·
[../../../docs/database.md](../../../docs/database.md)
