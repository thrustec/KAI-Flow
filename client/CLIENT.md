# client/ — React Frontend

## Folder Purpose
The KAI-Flow web application: a React 19 single-page app (Vite) providing the visual workflow
canvas, dashboard, marketplace, credentials/variables management, execution history, and chat
testing UI.

## What This Folder Contains
- `app/` — all application code:
  - `main.tsx` — bootstrap; `App.tsx` — routes + Keycloak OIDC provider + auth sync; `app.css` —
    Tailwind 4 / DaisyUI styles.
  - `components/` → [app/components/COMPONENTS.md](app/components/COMPONENTS.md)
  - `routes/` (pages) → [app/routes/ROUTES.md](app/routes/ROUTES.md)
  - `services/` (API layer) → [app/services/SERVICES.md](app/services/SERVICES.md)
  - `stores/` (Zustand) → [app/stores/STORES.md](app/stores/STORES.md)
  - `lib/` (api-client, config, hooks) → [app/lib/LIB.md](app/lib/LIB.md)
  - `data/` — `prebuiltTemplates.tsx`, `tutorialWorkflows.ts`, `templates/` (empty dir) —
    prebuilt workflow templates + interactive tutorial definitions.
  - `types/` — shared TS types: `api.ts` (mirrors backend schemas: Workflow, WorkflowData,
    NodeMetadata, WebhookStreamEvent…), `credentials.ts`, `export.ts`, `external-workflows.ts`,
    `index.d.ts`.
  - `test/` — test setup/utilities for Vitest.
- `public/` — static assets incl. `config.js` (runtime `window.VITE_*` configuration read at
  load; also parsed by `vite.config.ts` for the dev proxy path).
- `index.html` — SPA entry.
- Config: `vite.config.ts` (base path default `/kai`, dev proxy `/api/kai` → backend, optional
  HTTPS using `../backend/cert/`), `tsconfig.json` (`~/` alias), `vitest.config.ts`,
  `jest.config.js` (a11y tests via jest-axe), `.eslintrc.js`, `lighthouse.config.js`.
- `Dockerfile` (multi-stage: deps → build → production, Node 22-alpine, serves on port 3000,
  build args bake `VITE_*` values in), `docker-entrypoint.sh`, `DOCKER_README.md`.
- `package.json` — React 19, React Router 7, `@xyflow/react` 12, Zustand 5, TanStack Query 5,
  axios, Tailwind 4 + DaisyUI 5, Monaco, Recharts, Keycloak (keycloak-js, react-oidc-context),
  `@kaifusion/widget`; extensive security `overrides` block.
- `README.md` (React Router template readme), `GEMINI.md` (earlier AI-assistant doc, uses the
  legacy "KAI-Fusion" name).

## Important Files
`app/App.tsx`, `app/components/canvas/FlowCanvas.tsx`, `app/lib/api-client.ts`,
`app/lib/config.ts`, `vite.config.ts`, `public/config.js`.

## File-by-File Explanation
See the per-subfolder docs linked above; root-level files are covered in the list.

## Relationship With Other Folders
- Talks to `backend/` exclusively through HTTP (`/api/v1/...`); type contracts mirror
  `backend/app/schemas/`.
- Embeds `@kaifusion/widget` (from `widget/`) via `KaiChatWidget.tsx`.

## How This Folder Fits Into the AI Workflow
The canvas builds the `flow_data` JSON (nodes + edges) that the backend engine executes; chat and
log panels stream execution results back over SSE.

## Developer Notes
- Commands (run in `client/`): `npm run dev` (Vite, proxies `/api/kai`), `build`, `typecheck`,
  `lint` (zero-warning policy), `test` (Vitest), `test:a11y` (jest-axe).
- Runtime config: values come from `window.VITE_*` (public/config.js) and/or Vite env — check
  `app/lib/config.ts` before adding new config.

## Things to Be Careful About
- `VITE_*` values are **baked at build time** in Docker (build args); runtime overrides go
  through `public/config.js` — two mechanisms, keep them consistent.
- Base path defaults to `/kai` in `vite.config.ts` (env `VITE_BASE_PATH`); deep links and OIDC
  redirect URIs depend on it.
- Dev proxy only rewrites `/api/kai` — direct `/api/v1` calls bypass the proxy.

## Related Documentation Files
[../CLAUDE.md](../CLAUDE.md) · [../docs/frontend.md](../docs/frontend.md) ·
[../docs/api.md](../docs/api.md) · [../widget/WIDGET.md](../widget/WIDGET.md)
