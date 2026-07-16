# REST API Surface

Base: `http://<host>:23056` (dev default). All versioned routes live under `/api/v1`
(`API_START`/`API_VERSION` in [backend/app/core/constants.py](../backend/app/core/constants.py)).
Interactive reference: **Swagger UI at `/docs`**, ReDoc at `/redoc` — always authoritative for
exact request/response shapes. Router-by-router ownership:
[backend/app/api/API.md](../backend/app/api/API.md).

## Authentication
- `Authorization: Bearer <JWT>` — local (HS256) or Keycloak (RS256, JIT user provisioning).
- API keys (managed via `/api/v1/api-keys`) and `MASTER_API_KEY` env for programmatic/execution
  access.

## Endpoint groups (prefix → purpose)
| Prefix | Purpose |
|---|---|
| `/api/v1/auth` | Sign-up, sign-in, token refresh |
| `/api/v1/workflows` | CRUD, `/validate`, `/public/`, `/search/`, `/{id}/duplicate`, visibility, `/templates/…`, `/dashboard/stats/`, **`POST /execute`** (ad-hoc run, SSE), `/queue/status`, `/{id}/execute-timer-node`, `/error-trigger/{id}/stream` |
| `/api/v1/executions` | List/get/delete/cancel executions, `/export/csv` |
| `/api/v1/nodes` | Node catalog (canvas metadata) |
| `/api/v1/nodes/registry` | Node registry management |
| `/api/v1/node-configurations` | Saved node config presets |
| `/api/v1/credentials` | Encrypted credentials CRUD + usage info |
| `/api/v1/api-keys` | API key management |
| `/api/v1/chat` | Chat CRUD, `POST /{chatflow_id}/interact`, `/active-session/id` |
| `/api/v1/ai-builder` | Natural-language workflow generation |
| `/api/v1/variables` | Variables CRUD |
| `/api/v1/documents` | RAG document collections/uploads |
| `/api/v1/vectors` | Vector collections/documents (pgvector) |
| `/api/v1/jobs/scheduled` | Scheduled job management |
| `/api/timers` + `/api/v1/timers` | Timer triggers (deliberately dual-mounted) |
| `/api/v1/webhooks`, `/api/v1/webhooks/trigger` | Webhook endpoint/trigger management |
| dynamic webhook routes | Test & production webhook receivers (built-in prefixes, defined in `webhook_trigger.py`) |
| Kafka trigger routes | Listener management (built-in prefix, `kafka_trigger.py`) |
| HTTP client routes | Support for HttpClientNode (built-in prefix) |
| `/api/v1` (export) | Workflow export bundles |
| `/api/v1` (external-workflows) | Cross-instance workflow sharing |
| `/api/v1/logs` | Log streaming for the UI terminal |

## Meta endpoints
`GET /` · `GET /health` (+ legacy `/api/health`) · `GET /info` (+ legacy `/api/v1/info`).
Widget static assets at `/widget/*`.

## Streaming (SSE)
Execution, log, and error-trigger endpoints return `text/event-stream`. The frontend parses
typed events (status/result/error) in `client/app/services/executionService.ts` and
`client/app/lib/useSSE.ts` — keep event `type` fields backward compatible.

## Related
[backend.md](backend.md) · [ai-workflow.md](ai-workflow.md) ·
frontend consumers: [client/app/services/SERVICES.md](../client/app/services/SERVICES.md)
