# Configuration

One root `.env` file configures backend, frontend and Docker compose. Template:
[.env.example](../.env.example). Backend consumption:
[backend/app/core/constants.py](../backend/app/core/constants.py) (values may be
Fernet-encrypted — see `backend/app/core/env_encryption.py` + helper `backend/encrypt_env.py`).
Frontend consumption: `VITE_*` vars at build time and/or `client/public/config.js`
(`window.VITE_*`) at runtime, arbitrated by
[client/app/lib/config.ts](../client/app/lib/LIB.md).

## Backend variables
| Variable | Default (.env.example) | Meaning |
|---|---|---|
| `SECRET_KEY` | placeholder | JWT signing key (HS256) — change in production |
| `CREDENTIAL_MASTER_KEY` | placeholder | **Required.** Fernet key for credential encryption; backend exits without it. Generate: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `MASTER_API_KEY` | placeholder | Bypass key for execution endpoints |
| `ENVIRONMENT` / `BACKEND_DEBUG` / `LOG_LEVEL` | development / true / DEBUG | Runtime mode & logging |
| `BACKEND_PORT` | 23056 | Uvicorn port (local) / host port (compose) |
| `ROOT_PATH` | `/api/kai` | FastAPI root_path (must match frontend proxy) |
| `DATABASE_URL` | `postgresql://kai:kai@host.docker.internal:5432/kai` | Sync URL (use `127.0.0.1` for local dev) |
| `ASYNC_DATABASE_URL` | `postgresql+asyncpg://kai:kai@127.0.0.1:5432/kai` | Async URL |
| `POSTGRES_DB/USERNAME/PASSWORD`, `DATABASE_SSL`, `DISABLE_DATABASE`, `CREATE_DATABASE` | kai/kai/kai, false, false, true | DB bootstrap |
| `SSL_CERTFILE` / `SSL_KEYFILE` | `cert/cert.pem` / `cert/key.pem` | Optional HTTPS (falls back to HTTP if missing) |
| `LANGCHAIN_TRACING_V2/ENDPOINT/API_KEY/PROJECT` | false/… | Optional LangSmith tracing |
| `ENABLE_WORKFLOW_TRACING`, `TRACE_AGENT_REASONING`, `TRACE_MEMORY_OPERATIONS` | true | Internal tracing toggles |
| `ALLOWED_ORIGINS` | `*` | CORS (note: `main.py` currently hardcodes `*`) |
| `KEYCLOAK_ENABLED/URL/REALM/CLIENT_ID/VERIFY_SSL` | true/localhost:8080/… | Optional SSO |
| `ENTERPRISE` | false | Enterprise feature flag (passed to frontend as `VITE_ENTERPRISE`) |

Optional (commented in .env.example): `DB_POOL_*`, `ALGORITHM`, token expiry settings,
rate-limit/file-upload settings, `KAI_FLOW_LOG_*` enhanced-logging knobs, third-party keys
(`OPENAI_API_KEY`, `COHERE_API_KEY`, `TAVILY_API_KEY`, `GOOGLE_API_KEY`, AWS keys),
`AF_USE_STUB_ENGINE` (debug engine).
Most LLM/tool keys are normally entered per-node or stored as encrypted **Credentials** in the
app rather than env vars.

## Frontend variables
`VITE_BASE_PATH` (default `/` in .env.example; vite.config.ts falls back to `/kai`),
`VITE_API_BASE_URL` (default `http://localhost:23056`), `VITE_API_VERSION` (`/api/v1`),
`VITE_NODE_ENV`, `VITE_ENABLE_LOGGING`, `VITE_KEYCLOAK_URL/REALM/CLIENT_ID`.
⚠️ In Docker these are **baked at build time** (build args in
[client/Dockerfile](../client/Dockerfile) / compose); at runtime `public/config.js` can override.

## Other config files
- [docker-compose.yml](../docker-compose.yml) — wires env into services (see
  [deployment.md](deployment.md)).
- [client/vite.config.ts](../client/vite.config.ts) — dev proxy `/api/kai` → `VITE_API_BASE_URL`
  (auto-downgrades https→http locally when no certs); reads `public/config.js`.
- `client/tsconfig.json` (`~/` alias), `.eslintrc.js`, `vitest.config.ts`, `jest.config.js`,
  `lighthouse.config.js`.
- `export-docker/.env.example` — separate template for the distributable stack.

## Known inconsistencies (verify before relying)
- `VITE_API_BASE_URL`: `.env.example` says `:23056`, README troubleshooting says `:8000`,
  vite fallback is `:8000`. The backend's real dev port is `BACKEND_PORT` (23056 default).
- `.env.example` has `VITE_BASE_PATH=/` while vite.config.ts defaults to `/kai`.

## Related
[deployment.md](deployment.md) · [backend.md](backend.md) · [frontend.md](frontend.md) ·
[../CLAUDE.md](../CLAUDE.md)
