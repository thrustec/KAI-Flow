# client/app/routes/ — Pages (SPA Routes)

## Folder Purpose
One file per page. Routes are declared manually in `client/app/App.tsx` with React Router 7
(`<Routes>/<Route>`), most behind `AuthGuard`.

## What This Folder Contains / File-by-File Explanation
| File | Page |
|---|---|
| `home.tsx` | Dashboard (stats, charts, recent activity) |
| `signin.tsx` / `register.tsx` | Local auth pages (Keycloak login is a separate button) |
| `workflows.tsx` | Workflow list/management |
| `canvas.tsx` | The workflow editor page (hosts `FlowCanvas`) |
| `executions.tsx` | Execution history |
| `credentials.tsx` | Credential vault UI |
| `variables.tsx` | Variables management |
| `marketplace.tsx` | Templates / public workflows |
| `pinned.tsx` | Pinned items |
| `settings.tsx` | User settings |

## Important Files
`canvas.tsx` (the core product surface), `App.tsx` (route table — lives one level up).

## Relationship With Other Folders
Pages compose `app/components/`, read state from `app/stores/`, and never call HTTP directly.

## How This Folder Fits Into the AI Workflow
`canvas.tsx` is where workflows are designed and test-executed; `executions.tsx` shows engine
run history; `marketplace.tsx` distributes workflow templates.

## Developer Notes
- Adding a page: create the file here, register the `<Route>` in `App.tsx`, guard it with
  `AuthGuard`/`PublicOnlyGuard` as appropriate.

## Things to Be Careful About
- The app is served under a base path (default `/kai`) — use router-relative links, not absolute
  URLs.

## Related Documentation Files
[../../CLIENT.md](../../CLIENT.md) · [../components/COMPONENTS.md](../components/COMPONENTS.md) ·
[../stores/STORES.md](../stores/STORES.md)
