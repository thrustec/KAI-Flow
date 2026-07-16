# client/app/lib/ — Utilities, HTTP Client & Hooks

## Folder Purpose
Cross-cutting utilities: the axios client, runtime configuration, and custom hooks used by the
canvas and log terminal.

## What This Folder Contains / File-by-File Explanation
- `api-client.ts` — configured axios instance (base URL from config, auth header injection,
  error handling). **All HTTP goes through this.**
- `config.ts` — resolves runtime configuration (`window.VITE_*` injected by
  `client/public/config.js`, falling back to Vite env vars): API base URL/version, base path,
  Keycloak settings, logging flags.
- `useSSE.ts` — Server-Sent-Events hook for streamed execution events.
- `useLogStream.ts` — log streaming hook for the `LogPanel` terminal.
- `useWorkflowHistory.ts` — canvas undo/redo history (+ `isEditableKeyboardTarget` guard for
  keyboard shortcuts).
- `clipboard.ts`, `dateFormatter.ts`, `iconUtils.ts` — small helpers.

## Important Files
`api-client.ts`, `config.ts`.

## Relationship With Other Folders
Used by `app/services/` (api-client), `app/components/canvas/` (hooks) and `App.tsx` (config).

## How This Folder Fits Into the AI Workflow
`useSSE`/`useLogStream` deliver real-time engine execution feedback to the UI; `api-client`
carries every workflow/chat/execution request.

## Developer Notes
- New config value? Add it to `public/config.js` **and** `config.ts` (and to Docker build args in
  `client/Dockerfile` + compose files if needed at build time).

## Things to Be Careful About
- Two config sources (runtime `window.VITE_*` vs build-time `import.meta.env`) — `config.ts` is
  the single arbiter; don't read `import.meta.env` elsewhere.
- SSE reconnect/parsing logic must match backend event framing.

## Related Documentation Files
[../../CLIENT.md](../../CLIENT.md) · [../services/SERVICES.md](../services/SERVICES.md) ·
[../../../docs/configuration.md](../../../docs/configuration.md)
