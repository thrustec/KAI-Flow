# backend/app/schemas/ — Pydantic Request/Response Schemas

## Folder Purpose
Pydantic v2 models that define the API contract: request validation and response serialization
for the routers in `app/api/`. (Not to be confused with `app/api/schemas.py`, which holds local
helpers for API modules.)

## What This Folder Contains / File-by-File Explanation
| File | Schemas for |
|---|---|
| `auth.py` | Sign-up/sign-in payloads, tokens (`UserSignUpData`, …) |
| `user.py` | User responses/updates |
| `workflow.py` | `WorkflowResponse`, create/update requests, template schemas |
| `execution.py` | `WorkflowExecutionResponse`, execution filters |
| `chat.py` | `ChatMessageResponse`, interact payloads |
| `user_credential.py` | Credential create/read (secrets never echoed back) |
| `api_key.py` | API key create/response |
| `variable.py` | Variable CRUD |
| `document.py` | Document/collection/upload schemas |
| `node_configuration.py` | Node config presets |
| `organization.py` | Organization/role schemas |
| `webhook.py` | Webhook endpoint/event schemas |

## Important Files
`workflow.py` and `execution.py` — they shape what the frontend types in
`client/app/types/api.ts` mirror.

## Relationship With Other Folders
- Used by `app/api/` routers (`response_model=`) and `app/services/`.
- Field names must stay in sync with frontend TypeScript types (`client/app/types/`).

## How This Folder Fits Into the AI Workflow
Defines the wire format of `flow_data` (nodes/edges), execution inputs and streamed results —
the JSON contract between canvas and engine.

## Developer Notes
- Pydantic v2 style (`model_config`, `Field`); prefer explicit response models on endpoints.

## Things to Be Careful About
- Changing a schema is an API contract change — update `client/app/types/api.ts` and affected
  client services in the same change.

## Related Documentation Files
[../api/API.md](../api/API.md) · [../models/MODELS.md](../models/MODELS.md) ·
[../../../docs/api.md](../../../docs/api.md)
