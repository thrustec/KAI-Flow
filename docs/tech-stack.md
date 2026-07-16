# Tech Stack

Verified against `backend/requirements.txt`, `client/package.json`, `widget/package.json`,
Docker files and CI workflows (2026-07).

## Backend (Python 3.11)
| Technology | Version | Why it's used |
|---|---|---|
| FastAPI + Uvicorn | 0.136 / 0.36 | Async REST API, OpenAPI docs at `/docs`, SSE streaming |
| SQLAlchemy 2 + asyncpg (+ psycopg2/3) | 2.0.44 | Async ORM over PostgreSQL |
| Pydantic v2 (+ pydantic-settings) | 2.13 | Schema validation, node metadata typing, FlowState |
| LangChain (+ core/community/openai/tavily/cohere/postgres/text-splitters) | 1.x | LLM, tool, retriever, memory abstractions that nodes wrap |
| LangGraph (+ checkpoint/prebuilt/sdk) | 1.1 | The workflow execution engine: StateGraph compilation, checkpointing |
| LangSmith | 0.7 | Optional tracing/debugging of agent runs |
| OpenAI SDK / tiktoken | 2.33 | LLM + embeddings providers; AI Builder generation |
| Cohere / rank-bm25 | 5.21 | Reranking for RAG |
| pgvector | 0.3.6 | Embedding storage & similarity search in Postgres |
| python-jose, passlib[bcrypt], PyJWT, cryptography | — | JWT auth (HS256 + Keycloak RS256), password hashing, Fernet credential/env encryption |
| APScheduler + croniter + pytz/tzlocal | 3.11 | Scheduled/cron workflow triggers |
| confluent-kafka | 2.14 | Kafka trigger listeners + producer node |
| httpx / aiohttp / requests | — | HTTP client node & integrations |
| pypdf, pdfplumber, python-docx, markitdown, beautifulsoup4, lxml | — | Document loaders / web scraping for RAG |
| boto3, google-api-python-client | — | AWS S3/MinIO (`minio_service.py`) and Google API integrations |
| deepteam, json-repair | — | LLM red-team security nodes; robust JSON parsing |
| psutil | — | System monitoring |
| pytest + pytest-asyncio | 9 / 1.3 | Backend tests |

## Frontend (`client/`, TypeScript 5.8)
| Technology | Version | Why |
|---|---|---|
| React | 19 | UI |
| React Router | 7 | SPA routing (manual `<Routes>` in `App.tsx`) |
| Vite (+ vite-tsconfig-paths) | 8 | Build/dev server, `/api/kai` dev proxy, `~/` alias |
| @xyflow/react | 12 | The drag-and-drop workflow canvas |
| Zustand | 5 | Global client state (one store per domain) |
| @tanstack/react-query | 5 | Server-state caching |
| axios | 1.15 | HTTP (`app/lib/api-client.ts`) |
| Tailwind CSS 4 + DaisyUI 5 + @tailwindcss/typography | — | Styling (monochromatic blue theme, see commit d64ea89) |
| @monaco-editor/react | 4.7 | Code/JSON editor node fields |
| react-markdown + remark/rehype (gfm, math, katex, highlight, raw) | — | Chat message rendering |
| keycloak-js, oidc-client-ts, react-oidc-context | — | Keycloak SSO |
| recharts | 3 | Dashboard charts |
| lucide-react, motion, notistack | — | Icons, animation, toasts |
| Vitest (+ Testing Library, jsdom) & Jest + jest-axe | — | Unit tests & accessibility tests |
| ESLint (typescript-eslint) | — | Linting, `--max-warnings 0` |

## Widget (`widget/`)
`@kaifusion/widget` 1.1.0 — React 18/19 peer, Vite library build (ES+CJS+d.ts via
vite-plugin-dts) plus a standalone script-tag bundle (`vite.config.standalone.ts`). Uses
react-markdown/KaTeX/syntax-highlighter for rich chat rendering.

## Data layer
PostgreSQL 15 (`pgvector/pgvector:pg15` image in compose — required for the `vector` extension;
plain `postgres:15` does not include it) + pgvector extension. ~29 tables. Schema managed by
`backend/migrations/database_setup.py` (Alembic installed but unused — no migration tree).

## Infrastructure
- **Docker**: root `Dockerfile` (backend, python:3.11), `client/Dockerfile` (node:22-alpine
  multi-stage), root `docker-compose.yml` (db+backend+frontend dev stack),
  `export-docker/` (distributable stack with workflow bundle auto-import).
- **CI/CD**: GitHub Actions — `ci.yml` (tests w/ Postgres+Redis services), `backend-ci.yml`,
  `frontend-ci.yml`, `pr-checks.yml`, `deploy.yml`, `staging.yml`.
- **Auth infra**: optional Keycloak server (`KEYCLOAK_*` env).
- **Optional external services**: LangSmith, OpenAI-compatible APIs, Tavily, Cohere, Kafka,
  AWS S3/MinIO, Google APIs.

## Related docs
[backend.md](backend.md) · [frontend.md](frontend.md) · [database.md](database.md) ·
[deployment.md](deployment.md)
