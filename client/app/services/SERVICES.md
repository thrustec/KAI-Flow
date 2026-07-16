# client/app/services/ — Frontend API Layer

## Folder Purpose
Typed functions that call the backend REST API (axios via `app/lib/api-client.ts`). Stores call
services; components call stores.

## What This Folder Contains / File-by-File Explanation
| File | Backend counterpart |
|---|---|
| `workflows.ts` + `workflowService.ts` | `/api/v1/workflows` (CRUD, templates, stats, visibility) |
| `executionService.ts` | `/api/v1/executions` + streaming execution (`executeWorkflowStream`, SSE parsing) |
| `chatService.ts` | `/api/v1/chat` |
| `nodes.ts` | `/api/v1/nodes` (node catalog/metadata) |
| `authService.ts` | `/api/v1/auth` (sign-in/up, tokens) |
| `userCredentialService.ts` | `/api/v1/credentials` |
| `apiKeyService.ts` | `/api/v1/api-keys` |
| `variableService.ts` | `/api/v1/variables` |
| `aiBuilderService.ts` | `/api/v1/ai-builder` (NL workflow generation) |
| `exportService.ts` | `/api/v1` export endpoints |
| `externalWorkflowService.ts` | `/api/v1` external workflows |
| `organizationService.ts` | organizations/roles |
| `smartSuggestions.ts` | client-side smart node suggestions (paired with its store) |

## Important Files
`executionService.ts` (streaming logic), `workflows.ts`.

## Relationship With Other Folders
- Uses `app/lib/api-client.ts` (base URL/interceptors) and types from `app/types/api.ts`;
  consumed by `app/stores/`.
- Contracts mirror `backend/app/schemas/` — change both sides together.

## How This Folder Fits Into the AI Workflow
Carries the workflow graph to the backend and streams execution events (node status, outputs,
errors) back to the canvas/chat.

## Developer Notes
- Add new endpoints here (not inline in components/stores); keep response typing in
  `app/types/api.ts`.

## Things to Be Careful About
- There are two workflow service files (`workflows.ts`, `workflowService.ts`) — check which one a
  store imports before extending (stores currently import `~/services/workflows`).
- SSE parsing expects specific `type` fields in events; coordinate with
  `backend/app/api/workflows.py` / `executions.py`.

## Related Documentation Files
[../../CLIENT.md](../../CLIENT.md) · [../stores/STORES.md](../stores/STORES.md) ·
[../lib/LIB.md](../lib/LIB.md) · [../../../backend/app/api/API.md](../../../backend/app/api/API.md)
