# Project Structure

Full folder map (build artifacts, caches, `node_modules`, `__pycache__` omitted). Each linked
`.md` is the authoritative doc for that folder.

```
KAI-Flow/
├─ CLAUDE.md                  ← AI-assistant working rules (read first)
├─ README.md · USER_GUIDE.md · CONTRIBUTING.md · CODE_OF_CONDUCT.md · LICENSE (Apache 2.0)
├─ .env / .env.example        ← single env file for backend + frontend + compose
├─ docker-compose.yml         ← dev stack: db + kai-flow-backend + kai-flow-frontend
├─ Dockerfile                 ← backend image (see Known Issues in CLAUDE.md re: CMD)
├─ database_setup.log         ← log output from migrations/database_setup.py runs
├─ banner.png · demo.gif · demo.png
│
├─ .github/workflows/         ← ci.yml, backend-ci.yml, frontend-ci.yml, pr-checks.yml,
│                                deploy.yml, staging.yml
│
├─ backend/                   → backend/BACKEND.md
│  ├─ main.py                 ← FastAPI entry point
│  ├─ requirements.txt · encrypt_env.py · create_webhook_tables.py
│  ├─ webhook-http-integration-guide.md · README.md · docker-compose.yml
│  ├─ app/
│  │  ├─ api/                 → backend/app/api/API.md          (22 routers)
│  │  ├─ auth/                → backend/app/auth/AUTH.md        (JWT/Keycloak deps)
│  │  ├─ core/                → backend/app/core/CORE.md        (engine, graph_builder/, tool/,
│  │  │                                                          config, DB, security, logging)
│  │  ├─ middleware/          → backend/app/middleware/MIDDLEWARE.md
│  │  ├─ models/              → backend/app/models/MODELS.md    (19 model files)
│  │  ├─ nodes/               → backend/app/nodes/NODES.md      (base.py + 14 category folders)
│  │  ├─ routes/              → backend/app/routes/ROUTES.md    (export helpers)
│  │  ├─ schemas/             → backend/app/schemas/SCHEMAS.md  (Pydantic contracts)
│  │  └─ services/            → backend/app/services/SERVICES.md (incl. ai_builder/, memory/)
│  ├─ migrations/             → backend/migrations/MIGRATIONS.md (database_setup.py)
│  ├─ scripts/                → backend/scripts/SCRIPTS.md      (export/import CLI)
│  └─ tests/                  → backend/tests/TESTS.md          (AI Builder unit tests)
│
├─ client/                    → client/CLIENT.md
│  ├─ index.html · vite.config.ts · tsconfig.json · vitest.config.ts · jest.config.js
│  ├─ package.json · Dockerfile · docker-entrypoint.sh · DOCKER_README.md · GEMINI.md
│  ├─ public/                 ← static assets + runtime config.js (window.VITE_*)
│  └─ app/
│     ├─ App.tsx · main.tsx · app.css
│     ├─ components/          → client/app/components/COMPONENTS.md (canvas/, node/, modals/,
│     │                          credentials/, common/, tutorial/, external/, dashboard/)
│     ├─ routes/              → client/app/routes/ROUTES.md     (11 pages)
│     ├─ services/            → client/app/services/SERVICES.md (API layer)
│     ├─ stores/              → client/app/stores/STORES.md     (13 Zustand stores)
│     ├─ lib/                 → client/app/lib/LIB.md           (api-client, config, hooks)
│     ├─ data/                ← prebuiltTemplates.tsx, tutorialWorkflows.ts, templates/
│     ├─ types/               ← api.ts, credentials.ts, export.ts, external-workflows.ts
│     └─ test/                ← Vitest setup/utilities
│
├─ widget/                    → widget/WIDGET.md
│  ├─ src/ (KaiChatWidget.tsx, embed.tsx, config.ts, index.ts, index.css)
│  ├─ vite.config.ts (npm lib) · vite.config.standalone.ts (script-tag bundle)
│  └─ package.json (@kaifusion/widget) · README.md
│
├─ export-docker/             → export-docker/EXPORT-DOCKER.md
│  ├─ docker-compose.yml · Dockerfile.backend · Dockerfile.frontend · .env.example
│  └─ import_bundle/          ← drop exported workflow bundles here (README.md inside)
│
└─ docs/                      → this directory (see docs/README.md)
```

Small folders documented inline in their parent's doc instead of separately (to avoid
near-empty files): `client/app/data/`, `client/app/types/`, `client/app/test/`,
`client/public/` (in [CLIENT.md](../client/CLIENT.md)); `backend/app/core/graph_builder/` and
`backend/app/core/tool/` (in [CORE.md](../backend/app/core/CORE.md));
`backend/app/services/ai_builder/` and `memory/` (in [SERVICES.md](../backend/app/services/SERVICES.md));
node category folders (in [NODES.md](../backend/app/nodes/NODES.md));
`export-docker/import_bundle/` (in [EXPORT-DOCKER.md](../export-docker/EXPORT-DOCKER.md)).
