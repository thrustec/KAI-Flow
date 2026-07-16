# Backend Summary

FastAPI application (Python 3.11) in [backend/](../backend/BACKEND.md). Entry point:
[backend/main.py](../backend/main.py).

## Layered architecture & request flow

```
HTTP request
  → middleware (CORS, DetailedLogging, DatabaseQueryLogging, SecurityLogging)
  → app/api/<router>.py        (validation via app/schemas/, auth via app/auth/)
  → app/services/<service>.py  (business logic, async DB sessions)
  → app/models/ (SQLAlchemy)   or   app/core/engine.py (workflow execution)
  → response (JSON or SSE stream)
```

- **API layer** — 22 routers under `/api/v1` → [API.md](../backend/app/api/API.md)
- **Auth** — JWT (HS256) + Keycloak (RS256, JIT provisioning), API keys, `MASTER_API_KEY`
  → [AUTH.md](../backend/app/auth/AUTH.md)
- **Core** — engine, GraphBuilder, node registry, DB, config, security, logging/tracing
  → [CORE.md](../backend/app/core/CORE.md)
- **Nodes** — ~31 auto-discovered node classes in 14 categories
  → [NODES.md](../backend/app/nodes/NODES.md)
- **Services** — one service per domain + AI Builder + memory subsystem
  → [SERVICES.md](../backend/app/services/SERVICES.md)
- **Models/Schemas** — [MODELS.md](../backend/app/models/MODELS.md) /
  [SCHEMAS.md](../backend/app/schemas/SCHEMAS.md)

## Startup sequence (`main.py` lifespan)
1. Enhanced logging config → 2. `node_registry.discover_nodes()` → 3. `get_engine()` →
4. `setup_tracing()` → 5. DB health check (**raises on failure**) → 6. start Kafka
reconciliation loop. Shutdown stops the loop and all Kafka listeners.

## Background/async machinery
- SSE streaming for executions and logs.
- APScheduler-based scheduled jobs; timer trigger endpoints.
- Kafka listeners (per KafkaTriggerNode) reconciled periodically.
- Execution queue and active-task tracking in `app/core/`.

## Operational endpoints
`/health` (component statuses incl. DB stats), `/info`, `/` — plus Swagger at `/docs`,
ReDoc at `/redoc`. Legacy aliases: `/api/health`, `/api/v1/info`.

## Conventions
- Async everywhere (endpoints, sessions, node execution).
- Routers thin, services fat; schemas for all request/response bodies.
- Env config only via `app/core/constants.py` (supports encrypted values).

## Related
[ai-workflow.md](ai-workflow.md) · [api.md](api.md) · [database.md](database.md) ·
[configuration.md](configuration.md) · upstream [backend/README.md](../backend/README.md)
