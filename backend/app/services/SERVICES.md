# backend/app/services/ — Business Logic Layer

## Folder Purpose
Service classes sitting between the API routers (`app/api/`) and the ORM models
(`app/models/`). All non-trivial business logic and DB access lives here.

## What This Folder Contains / File-by-File Explanation
| File | Responsibility |
|---|---|
| `base.py` | Shared service base class/helpers |
| `dependencies.py` | FastAPI DI providers (`get_db_session`, `get_user_service_dep`, …) |
| `workflow_service.py` | Workflow CRUD, templates, visibility, stats |
| `workflow_executor.py` | Bridges API → engine: builds and runs workflows, handles execution records/streaming |
| `execution_service.py` | Execution history management |
| `chat_service.py` | Chat sessions/messages, interact flow |
| `user_service.py` | Users (lookup, creation incl. Keycloak JIT provisioning) |
| `credential_service.py` | Encrypted credential CRUD + workflow-usage tracking (blocks unsafe deletion) |
| `api_key_service.py` | API keys |
| `variable_service.py` | Variables |
| `document_service.py` | RAG document collections/uploads/chunks |
| `node_configuration_service.py` | Node config presets |
| `node_registry_service.py` | DB-backed node registry |
| `scheduled_job_service.py` | Scheduled jobs (APScheduler integration) |
| `webhook_service.py` | Webhook endpoints/events |
| `error_handler_service.py` | Error-trigger workflow handling |
| `minio_service.py` | MinIO/S3-compatible object storage client (boto3) |
| `memory.py` + `memory/` (`repo.py`, `store.py`, `service.py`) | Persistent conversation memory (DB-backed store/repo/service split) |

### `ai_builder/` — natural-language workflow generation
| File | Role |
|---|---|
| `orchestrator.py` | `AIBuilderOrchestrator.generate_workflow()`: calls an OpenAI-compatible LLM (AsyncOpenAI) in two phases — skeleton → parameterization; supports `build` and edit modes with chat history |
| `prompt_templates/` | `skeleton_system.py`, `parameterization_system.py` prompt builders |
| `schema_compiler.py` | Compiles the node catalog / connection rules / parameter schemas into prompt context |
| `diff_engine.py` | Computes changesets when editing an existing workflow |
| `validator.py` | `validate_structure` / `validate_topology` of generated graphs |
| `hydrator.py` | Fills defaults into generated nodes |
| `layout_engine.py` | Auto-layout (node positions) for generated graphs |
| `types.py`, `handle_types.py` | `WorkflowSnapshot`, `WorkflowNode`, `WorkflowEdge`, handle typing |

## Important Files
`workflow_executor.py` (execution pipeline), `ai_builder/orchestrator.py`,
`credential_service.py`, `dependencies.py`.

## Relationship With Other Folders
- Called by `app/api/`; uses `app/models/` + `app/core/database.py`. The primary ad-hoc execution
  path calls `app/core/workflow_enhancer.py`, which creates a fresh `DynamicWorkflowEngine` and
  delegates to `GraphBuilder`; the separate `app/core/engine.py` interface is still initialized
  at startup. AI Builder consumes node metadata from the registry.
- `backend/tests/` currently tests only the `ai_builder` modules.

## How This Folder Fits Into the AI Workflow
`workflow_executor.py` is the glue from REST/chat/webhook requests to the LangGraph engine.
`ai_builder/` is itself an AI feature: an LLM generates the workflow graph that the engine then
runs.

## Developer Notes
- Keep routers thin — put logic here. Services receive an `AsyncSession` via DI.
- AI Builder default model is `gpt-4o` with configurable `base_url` (any OpenAI-compatible API).

## Things to Be Careful About
- Credential deletion is intentionally guarded by workflow-usage checks — don't bypass.
- `minio_service.py` exists but object-storage configuration is not part of `.env.example`;
  This part is not clearly defined in the project.
- AI Builder output must pass `validator.py`; changing node metadata/handles can silently break
  generation — update `schema_compiler.py` expectations and the tests in `backend/tests/`.

## Related Documentation Files
[../api/API.md](../api/API.md) · [../models/MODELS.md](../models/MODELS.md) ·
[../core/CORE.md](../core/CORE.md) · [../../tests/TESTS.md](../../tests/TESTS.md) ·
[../../../docs/ai-workflow.md](../../../docs/ai-workflow.md)
