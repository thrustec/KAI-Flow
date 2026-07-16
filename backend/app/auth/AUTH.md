# backend/app/auth/ — Authentication Dependencies

## Folder Purpose
FastAPI dependency functions that authenticate requests. Small folder, big blast radius: almost
every protected endpoint depends on it.

## What This Folder Contains / File-by-File Explanation
- `dependencies.py` — `get_current_user` (HTTP Bearer → `app/core/security.verify_token` →
  DB user lookup). Supports:
  - **Local JWT** (HS256, `SECRET_KEY` from `app/core/constants.py`)
  - **Keycloak tokens** (RS256): resolves email from `sub`/`email`/`preferred_username` claims and
    performs **JIT user provisioning** (creates the DB user on first login).
  Also defines an optional-auth variant (`security_optional`).
- `__init__.py` — package exports.

## Important Files
`dependencies.py` (the only module).

## Relationship With Other Folders
- Token logic lives in `app/core/security.py`; Keycloak config in `app/core/constants.py`
  (`KEYCLOAK_*`); user creation via `app/services/user_service.py`.
- `MASTER_API_KEY` (constants) can bypass authorization on execution endpoints; API keys are
  handled via `app/api/api_key.py` / `app/services/api_key_service.py`.
- Frontend counterpart: `client/app/stores/auth.ts` + `react-oidc-context` Keycloak wiring in
  `client/app/App.tsx`.

## How This Folder Fits Into the AI Workflow
Not workflow logic itself — it gates who may create/execute workflows and scopes data (user_id
flows into the engine as `user_context`).

## Developer Notes
- To protect a new endpoint: `user: User = Depends(get_current_user)`.

## Things to Be Careful About
- JIT provisioning creates users automatically for valid Keycloak tokens — consider implications
  before changing realm/client settings.
- Any change here affects every protected route; test both local-JWT and Keycloak paths
  (`KEYCLOAK_ENABLED=true/false`).

## Related Documentation Files
[../core/CORE.md](../core/CORE.md) · [../api/API.md](../api/API.md) ·
[../../../docs/configuration.md](../../../docs/configuration.md)
