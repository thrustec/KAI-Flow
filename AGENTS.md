# AGENTS.md — KAI-Flow

This file gives Codex (and other AI assistants) the context needed to work correctly on this
repository. Read it before making any change. See **Documentation Reference Rules** at the bottom —
they are mandatory for all future work.

---

## Project Overview

**KAI-Flow** is an open-source (Apache 2.0) visual platform for building AI-powered assistants and
workflow automations, developed by Kafein (repo: `kafein-product-space/KAI-Flow`; the active remote
in this clone is `kafein-technology`). Users design workflows on a drag-and-drop canvas by
connecting nodes (LLMs, agents, tools, memory, vector stores, triggers…), test them in real time
via chat, and deploy them — including as an embeddable chat widget for third-party sites.

It is conceptually similar to tools like Flowise or n8n, built on **LangChain / LangGraph**.

> Naming note: the codebase contains legacy names. The FastAPI app title is "Agent-Flow V2",
> the widget npm package is `@kaifusion/widget`, and some docs say "KAI-Fusion". They all refer
> to this same project, whose current name is **KAI-Flow**.

## Project Purpose

- Let non-programmers and developers build AI assistants/automations visually instead of writing
  LangChain/LangGraph code by hand.
- Provide a full lifecycle: design (canvas) → configure (node forms, credentials, variables) →
  test (chat, streaming logs) → run (API, webhooks, timers, Kafka) → embed/export (widget,
  external workflows, Docker export bundles).
- Typical scenarios: Q&A assistants over documents (RAG), web-search agents, scheduled jobs,
  webhook-driven integrations, HTTP API orchestration, LLM red-teaming/security testing.

## AI Workflow Architecture

The heart of the system (all paths relative to repo root):

1. **Workflow definition**: the frontend canvas ([client/app/components/canvas/FlowCanvas.tsx](client/app/components/canvas/FlowCanvas.tsx))
   produces `flow_data` JSON: `{ nodes: [...], edges: [...] }` (XYFlow/React Flow format), stored in
   the `workflows` table.
2. **Node system** ([backend/app/nodes/](backend/app/nodes/NODES.md)): every node is a Python class
   extending `BaseNode` (in `backend/app/nodes/base.py`) with typed `metadata` (inputs/outputs,
   UI form fields). Four node types (enum `NodeType`):
   - `PROVIDER` — factory: creates LangChain objects (e.g. `OpenAINode`, `TavilySearchNode`)
   - `PROCESSOR` — orchestrator: combines inputs (e.g. `ReactAgentNode`, `ConditionNode`)
   - `TERMINATOR` — transformer/finalizer (e.g. `EndNode`, `WebhookTriggerNode`)
   - `MEMORY` — conversation state (e.g. `BufferMemoryNode`)
3. **Node discovery** (`backend/app/core/node_registry.py`): `node_registry.discover_nodes()` scans
   `app/nodes/` at startup and registers all concrete `BaseNode` subclasses. Adding a node file is
   enough to register it — no manual wiring.
4. **Engine** (`backend/app/core/engine.py`): `get_engine()` returns the singleton
   `LangGraphWorkflowEngine` (or `StubWorkflowEngine` when `AF_USE_STUB_ENGINE=true`). API:
   `validate(flow_data)` → `build(flow_data)` → `await execute(inputs, stream=...)`.
5. **GraphBuilder** (`backend/app/core/graph_builder/`): compiles `flow_data` into a LangGraph
   `StateGraph` with `MemorySaver` checkpointing. Delegates to `ConnectionMapper`, `NodeExecutor`,
   `ControlFlowManager`, `ValidationEngine`.
6. **State** (`backend/app/core/state.py`): `FlowState` (Pydantic) flows through the graph; reducer
   functions (`merge_node_outputs`, `merge_executed_nodes`, `merge_errors`) support parallel
   branches.
7. **Execution entry points**: REST (`/api/v1/workflows/execute`, SSE streaming), chat, webhooks
   (test + production routers), timers/scheduled jobs (APScheduler + croniter), Kafka triggers
   (a reconciliation loop is started in `backend/main.py` lifespan).
8. **AI Builder** (`backend/app/services/ai_builder/`): generates/edits workflows from natural
   language via OpenAI-compatible LLMs — two-phase prompting (skeleton → parameterization) +
   diff engine, validators, hydrator, auto-layout.
9. **RAG**: document loaders / web scraper → `ChunkSplitterNode` → `OpenAIEmbeddingsProvider` →
   `VectorStoreOrchestrator` (PostgreSQL + pgvector) → `RetrieverProvider` (+ `CohereRerankerNode`)
   → agent.

Full detail: [docs/ai-workflow.md](docs/ai-workflow.md).

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI 0.136, Uvicorn, SQLAlchemy 2 (async, asyncpg), Pydantic v2 |
| AI/LLM | LangChain 1.x, LangGraph 1.x, LangSmith (optional tracing), OpenAI SDK, Cohere, Tavily |
| Database | PostgreSQL 15 + pgvector (embeddings), ~29 tables (see `backend/migrations/database_setup.py`) |
| Auth | JWT (python-jose, HS256) + optional Keycloak (RS256, JIT user provisioning), API keys, `MASTER_API_KEY` |
| Scheduling | APScheduler, croniter |
| Messaging | Kafka (confluent-kafka) triggers/producer |
| Frontend | React 19, React Router 7 (SPA routes), Vite, TypeScript 5.8, Zustand, TanStack Query, XYFlow (`@xyflow/react` 12), Tailwind CSS 4 + DaisyUI 5, Monaco editor, Recharts |
| Widget | `widget/` — `@kaifusion/widget` React lib + standalone `widget.js` build (Vite lib mode) |
| Container | Docker + docker-compose (root = dev stack, `export-docker/` = distributable stack) |
| CI | GitHub Actions (`.github/workflows/`: ci.yml, backend-ci.yml, frontend-ci.yml, pr-checks.yml, deploy.yml, staging.yml) |
| Docs (docs sites) | Some deployment/publishing steps reference MkDocs, but no MkDocs config exists in this repo |

Details and "why": [docs/tech-stack.md](docs/tech-stack.md).

## Installation

Prerequisites: Docker (for Postgres at minimum), Python 3.11, Node.js ≥ 18.15.

```bash
# 1. Environment
cp .env.example .env        # then edit values (see Environment Variables)

# 2a. Full Docker stack (simplest)
docker compose up -d
# Frontend: http://localhost:23058  ·  Backend Swagger: http://localhost:23056/docs

# 2b. Local development
# For local dev, replace host.docker.internal with 127.0.0.1 in DATABASE_URL in .env
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
docker run --name kai -e POSTGRES_DB=kai -e POSTGRES_USER=kai -e POSTGRES_PASSWORD=kai -p 5432:5432 -d pgvector/pgvector:pg15
python backend/migrations/database_setup.py    # creates DB schema
```

## Running the Project

```bash
# Backend (from repo root, venv active) — serves on BACKEND_PORT (default 23056)
python backend/main.py

# Frontend (second terminal)
cd client && npm install && npm run dev    # Vite dev server, proxies /api/kai → backend

# Widget development
cd widget && npm install && npm run dev
```

## Environment Variables

Defined in root `.env` (template: [.env.example](.env.example)); consumed by
`backend/app/core/constants.py` (values may be Fernet-encrypted via
`backend/app/core/env_encryption.py`; `backend/encrypt_env.py` is a helper for that).

Required / important:
- `SECRET_KEY` — JWT signing key
- `CREDENTIAL_MASTER_KEY` — Fernet key for encrypting stored user credentials. **The backend
  refuses to start without it** (`constants.py` raises).
- `MASTER_API_KEY` — bypass key for workflow execution endpoints
- `DATABASE_URL`, `ASYNC_DATABASE_URL`, `POSTGRES_*`, `CREATE_DATABASE`
- `BACKEND_PORT` (default 23056), `ROOT_PATH` (e.g. `/api/kai`), `SSL_CERTFILE`/`SSL_KEYFILE` (optional HTTPS)
- `KEYCLOAK_ENABLED` + `KEYCLOAK_URL/REALM/CLIENT_ID` (optional SSO), `ENTERPRISE`
- `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT` (optional LangSmith tracing)
- `VITE_API_BASE_URL`, `VITE_API_VERSION`, `VITE_BASE_PATH`, `VITE_KEYCLOAK_*` — frontend build/runtime
- Optional third-party keys: `OPENAI_API_KEY`, `COHERE_API_KEY`, `TAVILY_API_KEY`, … (most model/tool
  keys are usually entered per-node or stored as encrypted Credentials in the app instead)

Full reference: [docs/configuration.md](docs/configuration.md).

## Main Features

| Feature | Where |
|---|---|
| Visual workflow canvas (drag-drop, undo/redo, autosave, sticky notes) | `client/app/components/canvas/`, `client/app/routes/canvas.tsx` |
| Node system (~31 node classes: LLM, agent, tools, RAG, triggers, processing, security/red-team) | `backend/app/nodes/`, UI forms in `client/app/components/node/` |
| LangGraph execution engine with streaming (SSE) | `backend/app/core/engine.py`, `graph_builder/`, `backend/app/api/workflows.py`, `executions.py` |
| Chat testing + chat history | `backend/app/api/chat.py`, `client/app/components/canvas/ChatComponent.tsx` |
| AI Builder (generate workflows from natural language) | `backend/app/services/ai_builder/`, `client/app/services/aiBuilderService.ts` |
| Credentials vault (encrypted, deletion protected by usage tracking) | `backend/app/services/credential_service.py`, `client/app/components/credentials/` |
| Variables, API keys, organizations/roles | `backend/app/api/variables.py`, `api_key.py`, `backend/app/models/organization.py` |
| Webhook triggers (test/prod), timers, scheduled jobs, Kafka triggers, error triggers | `backend/app/nodes/triggers/`, `backend/app/api/webhooks.py`, `scheduled_jobs.py`, `timers.py` |
| Documents & vector storage (RAG) | `backend/app/api/documents.py`, `vectors.py`, `backend/app/models/document.py`, `vector_*.py` |
| Embeddable chat widget | `widget/`, served by backend at `/widget`, export modal `client/app/components/modals/WidgetExportModal.tsx` |
| External workflows (import/embed workflows from other instances) | `backend/app/api/external_workflows.py`, `client/app/components/external/` |
| Export/import bundles (workflows + Docker) | `backend/scripts/`, `backend/app/routes/export/`, `export-docker/` |
| Templates & marketplace, dashboard stats, execution history, log terminal | `client/app/routes/marketplace.tsx`, `home.tsx`, `executions.tsx`, `client/app/components/canvas/LogPanel.tsx` |

## Folder Structure

```
KAI-Flow/
├─ backend/            FastAPI backend — see backend/BACKEND.md
│  ├─ main.py          entry point (FastAPI app, routers, lifespan)
│  ├─ app/
│  │  ├─ api/          REST endpoint routers        → backend/app/api/API.md
│  │  ├─ auth/         auth dependencies (JWT/Keycloak) → backend/app/auth/AUTH.md
│  │  ├─ core/         engine, graph builder, config, DB, security → backend/app/core/CORE.md
│  │  ├─ middleware/   logging/security middleware  → backend/app/middleware/MIDDLEWARE.md
│  │  ├─ models/       SQLAlchemy models            → backend/app/models/MODELS.md
│  │  ├─ nodes/        workflow node classes        → backend/app/nodes/NODES.md
│  │  ├─ routes/       export route helpers         → backend/app/routes/ROUTES.md
│  │  ├─ schemas/      Pydantic request/response    → backend/app/schemas/SCHEMAS.md
│  │  └─ services/     business logic + AI Builder  → backend/app/services/SERVICES.md
│  ├─ migrations/      database_setup.py            → backend/migrations/MIGRATIONS.md
│  ├─ scripts/         workflow export/import CLI   → backend/scripts/SCRIPTS.md
│  └─ tests/           pytest tests (AI Builder)    → backend/tests/TESTS.md
├─ client/             React frontend — see client/CLIENT.md
│  └─ app/
│     ├─ components/   canvas, node UI, modals, …   → client/app/components/COMPONENTS.md
│     ├─ routes/       pages (SPA)                  → client/app/routes/ROUTES.md
│     ├─ services/     API layer (axios)            → client/app/services/SERVICES.md
│     ├─ stores/       Zustand stores               → client/app/stores/STORES.md
│     ├─ lib/          api-client, config, hooks    → client/app/lib/LIB.md
│     ├─ data/         prebuilt/tutorial templates
│     └─ types/        shared TS types
├─ widget/             embeddable chat widget       → widget/WIDGET.md
├─ export-docker/      distributable Docker bundle  → export-docker/EXPORT-DOCKER.md
├─ docs/               central documentation        → docs/README.md
├─ .github/workflows/  CI/CD pipelines
├─ docker-compose.yml  dev stack (db + backend + frontend)
└─ Dockerfile          backend image
```

## Important Files

- [backend/main.py](backend/main.py) — backend entry point: app creation, all router includes, lifespan (node discovery, engine init, DB health, Kafka loop), `/health`, `/info`.
- [backend/app/core/engine.py](backend/app/core/engine.py) — `get_engine()`, `LangGraphWorkflowEngine`.
- [backend/app/core/graph_builder/__init__.py](backend/app/core/graph_builder/__init__.py) — `GraphBuilder` orchestration.
- [backend/app/nodes/base.py](backend/app/nodes/base.py) — `BaseNode`, `NodeType`, `NodeMetadata`, `NodeProperty` (the contract every node follows).
- [backend/app/core/node_registry.py](backend/app/core/node_registry.py) — automatic node discovery.
- [backend/app/core/constants.py](backend/app/core/constants.py) — all env-derived config.
- [backend/migrations/database_setup.py](backend/migrations/database_setup.py) — schema creation (run before first start).
- [client/app/App.tsx](client/app/App.tsx) — SPA routes + Keycloak OIDC wiring.
- [client/app/components/canvas/FlowCanvas.tsx](client/app/components/canvas/FlowCanvas.tsx) — the canvas (largest, most central UI component).
- [client/app/lib/api-client.ts](client/app/lib/api-client.ts) + [client/app/lib/config.ts](client/app/lib/config.ts) — HTTP layer & runtime config.
- [docker-compose.yml](docker-compose.yml) / [Dockerfile](Dockerfile) / [client/Dockerfile](client/Dockerfile) — containerization.
- [.env.example](.env.example) — canonical env template.

## Development Guidelines

- **Adding a node**: create a class in the right `backend/app/nodes/<category>/` folder extending
  `ProviderNode` / `ProcessorNode` / `TerminatorNode` / `MemoryNode` (from `app/nodes/base.py`),
  define `metadata` (inputs/outputs/UI fields) and implement `execute`. Discovery is automatic.
  The generic frontend form (`client/app/components/node/GenericNodeForm.tsx` + `fields/`) renders
  the UI from node metadata, so most nodes need no frontend change. See
  [CONTRIBUTING.md](CONTRIBUTING.md) for the maintainers' node-type guide.
- **Adding an API endpoint**: router in `backend/app/api/`, business logic in
  `backend/app/services/`, Pydantic schemas in `backend/app/schemas/`, include the router in
  `backend/main.py` with the `/{API_START}/{API_VERSION}` prefix convention.
- **Frontend data flow**: component → Zustand store (`client/app/stores/`) → service
  (`client/app/services/`) → `lib/api-client.ts` → backend. Keep that layering.
- **Database changes**: models in `backend/app/models/` + register in `models/__init__.py`; the
  table list in `backend/migrations/database_setup.py` (`expected_tables`) must be updated.
  Alembic is installed but no alembic migration tree exists in the repo — schema management goes
  through `database_setup.py`.
- **Branches**: default working branch is `dev`; PRs target `main` (see recent merge history).
- Don't commit `.env` (it exists locally with real values), certificates, or build artifacts.

## Coding Conventions

- **Python**: type-hinted, async-first (async SQLAlchemy sessions, `async def` endpoints), Pydantic
  v2 models, service-layer pattern. Modules carry long descriptive docstrings. Logging via the
  enhanced logging helpers in `app/core/enhanced_logging.py`.
- **TypeScript/React**: functional components + hooks; Zustand for client state;
  TanStack Query available for server state; Tailwind 4 + DaisyUI classes; `~/` path alias to
  `client/app` (vite-tsconfig-paths); ESLint with `--max-warnings 0`.
- Some comments appear in Turkish (e.g. Dockerfiles) — the team is Turkish; write new code
  comments in English to match the majority of the codebase.
- No Python formatter/linter config (black/ruff) is committed — follow the existing style.
  This part is not clearly defined in the project.

## Common Commands

```bash
# Backend
python backend/main.py                          # run dev backend (reload enabled)
python backend/migrations/database_setup.py     # create/verify DB schema
cd backend && python -m pytest tests/           # backend tests (pytest + pytest-asyncio)
cd backend && python -m scripts.export_workflows --ids "<uuid>" --output ./export_bundle
cd backend && python -m scripts.import_workflows ...   # see script docstrings

# Frontend (in client/)
npm run dev / build / typecheck / lint / test   # Vitest for unit tests

# Widget (in widget/)
npm run build              # library build (@kaifusion/widget)
npm run build:standalone   # standalone widget.js for <script> embedding

# Docker
docker compose up -d                         # root: dev stack
cd export-docker && docker compose up --build  # distributable stack (auto-imports ./import_bundle)
```

## Known Issues or Missing Parts

- **Root `Dockerfile` CMD is stale**: it runs `uvicorn app.main:app`, but the module is `main:app`
  (file `backend/main.py`). `docker-compose.yml` overrides the command, so compose works; running
  the image directly would fail.
- **Naming inconsistencies**: "Agent-Flow V2" (FastAPI title, health/info endpoints), "KAI-Fusion"
  (client/GEMINI.md, export-docker container names), `@kaifusion/widget` (npm) vs README's
  mention of `@kaiflow/widget`.
- **README's project-structure diagram** lists `docs/ # Documentation (MkDocs)`; no MkDocs setup
  exists. The `docs/` directory in this repo (created 2026-07) is plain markdown documentation.
- **VITE_API_BASE_URL defaults differ**: root `.env.example` uses `http://localhost:23056`, the
  README troubleshooting section says `http://localhost:8000`, and `client/vite.config.ts` falls
  back to `http://localhost:8000`. Verify which port your backend actually uses (default 23056).
- **Test coverage is thin**: `backend/tests/` only covers AI Builder modules; client has Vitest
  config and a `test/` folder, plus a `jest.config.js` for a11y tests.
- CI (`.github/workflows/ci.yml`) provisions a Redis service, but no Redis usage is visible in the
  backend code. This part is not clearly defined in the project.
- `backend/create_webhook_tables.py` and `backend/webhook-http-integration-guide.md` are one-off
  helper artifacts at backend root; consult before touching webhook persistence.
- `client/.vite/` is an untracked build cache (safe to ignore/delete; consider gitignoring).

## Future Improvements

(Suggestions, not commitments)
- Adopt Alembic migrations instead of imperative `database_setup.py`.
- Fix the root Dockerfile CMD; align naming (KAI-Flow everywhere).
- Broaden automated tests (engine/graph_builder, API integration, frontend stores).
- Restrict CORS (currently `allow_origins=["*"]` in `backend/main.py`) for production.
- Consolidate the duplicated timers router registration and legacy route aliases.

## Documentation Reference Rules (MANDATORY)

Before making **any** future code change in this repository, Codex must:

1. **Read this `AGENTS.md`** first.
2. **Read the folder-level `.md` file** of every folder being modified (e.g.
   `backend/app/nodes/NODES.md` before touching a node, `client/app/stores/STORES.md` before
   touching a store). Each folder doc lists purpose, file-by-file explanations, and pitfalls.
3. **Read the relevant `docs/` file(s)**: [docs/README.md](docs/README.md) is the index —
   e.g. `docs/ai-workflow.md` for engine/node changes, `docs/api.md` for endpoints,
   `docs/database.md` for models, `docs/configuration.md` for env/config,
   `docs/deployment.md` for Docker/CI.
4. **Check for conflicts** between the requested change and the documented architecture. If the
   change conflicts, surface the conflict to the user before implementing.
5. **Update documentation with the code**: any change to code must be reflected in the affected
   folder-level `.md` and the related `docs/` file(s) in the same change set. Keep all `.md` files
   consistent with each other.

Cross-reference map: folder docs link to related folder docs and to `docs/`; `docs/` files link
back to folder docs. Existing upstream docs ([README.md](README.md), [USER_GUIDE.md](USER_GUIDE.md),
[CONTRIBUTING.md](CONTRIBUTING.md), [backend/README.md](backend/README.md),
[widget/README.md](widget/README.md)) remain authoritative for install/user-facing instructions.
