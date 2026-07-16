# client/app/stores/ — Zustand State Stores

## Folder Purpose
Global client state (Zustand 5). Each store owns a domain: it holds data + loading/error state
and exposes async actions that call `app/services/`.

## What This Folder Contains / File-by-File Explanation
| File | State domain |
|---|---|
| `workflows.ts` | Workflows, templates, categories, dashboard stats, `currentWorkflow`, unsaved-changes flag (uses `subscribeWithSelector`) |
| `nodes.ts` | Node catalog (metadata for the sidebar/canvas) |
| `executions.ts` | Execution history/status |
| `chat.ts` | Chat sessions/messages for canvas testing |
| `auth.ts` | Auth tokens/user (localStorage `auth_access_token`/`auth_refresh_token`; syncs with Keycloak via `AuthSynchronizer` in `App.tsx`) |
| `userCredential.ts` | Credentials |
| `apiKey.ts` | API keys |
| `variables.ts` | Variables |
| `organization.ts` | Organizations/roles |
| `pinnedItems.ts` | Pinned dashboard items |
| `smartSuggestions.ts` | Node-suggestion settings/state |
| `theme.ts` | Light/dark theme |
| `tutorialProgress.ts` | Tutorial progress |

## Important Files
`workflows.ts`, `auth.ts`, `nodes.ts`.

## Relationship With Other Folders
Consumed by `app/components/` and `app/routes/`; call `app/services/`; typed by `app/types/`.

## How This Folder Fits Into the AI Workflow
`workflows.ts` holds the workflow being edited (and its dirty state); `nodes.ts` supplies node
metadata that the canvas renders; `executions.ts`/`chat.ts` reflect engine runs.

## Developer Notes
- Pattern: state fields + async actions with `isLoading`/`error`; keep API calls in services.
- TanStack Query is also available (used for server-state caching) — prefer it for pure
  fetch-cache scenarios, Zustand for shared mutable UI state.

## Things to Be Careful About
- `auth.ts` writes tokens to localStorage and coordinates with Keycloak session state — changes
  affect both auth modes (local + OIDC).
- `hasUnsavedChanges` in `workflows.ts` drives the unsaved-changes modal and autosave; keep it
  accurate when adding canvas mutations.

## Related Documentation Files
[../../CLIENT.md](../../CLIENT.md) · [../services/SERVICES.md](../services/SERVICES.md) ·
[../components/COMPONENTS.md](../components/COMPONENTS.md)
