# backend/app/api/ — REST API Routers

## Folder Purpose
One FastAPI `APIRouter` per resource. Routers are included by `backend/main.py` under the prefix
`/{API_START}/{API_VERSION}` (= `/api/v1`), except a few routers that carry built-in prefixes
(webhooks test/production, Kafka, HTTP client, timers unversioned alias).

## What This Folder Contains / File-by-File Explanation
| File | Mounted at (via main.py) | Responsibility |
|---|---|---|
| `auth.py` | `/api/v1/auth` | Sign-up/sign-in, JWT issuance/refresh (local auth; Keycloak tokens verified in `app/auth/`) |
| `workflows.py` | `/api/v1/workflows` | Workflow CRUD, validate, duplicate, visibility, public listing/search, templates (`/templates/`), dashboard stats, **ad-hoc execution** `POST /execute` (SSE streaming), execution queue status, timer-node manual execution, error-trigger stream |
| `executions.py` | `/api/v1/executions` | Execution history: list/get/delete/cancel, CSV export |
| `nodes.py` | `/api/v1/nodes` | Node catalog for the canvas (metadata from the node registry) |
| `node_registry.py` | `/api/v1/nodes/registry` | Node registry management endpoints (DB-backed `node_registry` table) |
| `node_configurations.py` | `/api/v1/node-configurations` | Saved per-node configuration presets |
| `credentials.py` | `/api/v1/credentials` | Encrypted user credentials CRUD (+ workflow-usage protection) |
| `api_key.py` | `/api/v1/api-keys` | API key management for programmatic execution |
| `chat.py` | `/api/v1/chat` | Chat sessions/messages, `POST /{chatflow_id}/interact`, active session |
| `ai_builder.py` | `/api/v1/ai-builder` | Natural-language workflow generation (delegates to `app/services/ai_builder/`) |
| `variables.py` | `/api/v1/variables` | User/workflow variables CRUD |
| `documents.py` | `/api/v1/documents` | Document collections/upload for RAG |
| `vectors.py` | `/api/v1/vectors` | Vector collections/documents (pgvector) |
| `scheduled_jobs.py` | `/api/v1/jobs/scheduled` | Cron/scheduled job management (APScheduler) |
| `timers.py` | `/api/timers` **and** `/api/v1/timers` | Timer trigger endpoints (registered twice on purpose to match frontend calls) |
| `webhooks.py` | `/api/v1/webhooks`, `/api/v1/webhooks/trigger` | Webhook endpoint config + trigger management |
| `http_client.py` | built-in prefix | HTTP client node support endpoints |
| `export.py` | `/api/v1` | Workflow export endpoints (bundles; uses `app/routes/export/`) |
| `external_workflows.py` | `/api/v1` | Register/serve "external workflows" (share/embed flows across instances) |
| `logs.py` | `/api/v1/logs` | Log streaming for the frontend log terminal |
| `workflow_integration.py` | not included in `main.py` | Integration helpers; This part is not clearly defined in the project. |
| `schemas.py` | n/a | Local schema helpers for API modules (distinct from `app/schemas/`) |

Also mounted in `main.py` but defined elsewhere: webhook test/production routers and dynamic
webhook router (`app/nodes/triggers/webhook_trigger.py`, `app/nodes/triggers/__init__.py`),
Kafka trigger router (`app/nodes/triggers/kafka_trigger.py`).

## Important Files
`workflows.py` (largest surface, includes execution + SSE), `chat.py`, `webhooks.py`, `auth.py`.

## Relationship With Other Folders
- Depends on `app/services/` for business logic, `app/schemas/` for request/response models,
  `app/auth/dependencies.py` for `get_current_user`, `app/core/` for engine/DB.
- Consumed by `client/app/services/*.ts` and `widget/`.

## How This Folder Fits Into the AI Workflow
`workflows.py::execute_adhoc_workflow` and the chat/webhook/timer/Kafka endpoints are the entry
points that hand `flow_data` to the engine (`app/core/engine.py`) and stream results back.

## Developer Notes
- New endpoint = new router file here + `include_router` in `backend/main.py` + service +
  schema. Follow the existing prefix/tags pattern.
- Auth: most routers depend on `get_current_user`; execution endpoints can also accept
  `MASTER_API_KEY` or API keys.

## Things to Be Careful About
- Streaming endpoints return SSE (`text/event-stream`) — the frontend (`lib/useSSE.ts`,
  `executionService.ts`) parses specific event shapes; keep event `type` fields stable.
- Legacy aliases exist (`/api/health`, `/api/v1/info`, unversioned timers) — don't remove them
  without checking frontend/tests.

## Related Documentation Files
[../../BACKEND.md](../../BACKEND.md) · [../services/SERVICES.md](../services/SERVICES.md) ·
[../schemas/SCHEMAS.md](../schemas/SCHEMAS.md) · [../auth/AUTH.md](../auth/AUTH.md) ·
[../../../docs/api.md](../../../docs/api.md)
