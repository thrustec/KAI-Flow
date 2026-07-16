# backend/app/middleware/ — HTTP Middleware

## Folder Purpose
Custom Starlette/FastAPI middleware for observability and security logging, registered in
`backend/main.py`.

## What This Folder Contains / File-by-File Explanation
- `logging_middleware.py` — implements the three middleware classes exported by `__init__.py`:
  - `DetailedLoggingMiddleware` — request/response logging (body logging togglable, size-capped;
    `/health`, `/docs`, `/openapi.json`, `/redoc` excluded).
  - `DatabaseQueryLoggingMiddleware` — DB query logging per request.
  - `SecurityLoggingMiddleware` — suspicious-request detection and security-header logging.
- `__init__.py` — exports the middleware classes.

## Important Files
`logging_middleware.py` (the only module).

## Relationship With Other Folders
- Registered in `backend/main.py`; uses logging helpers from `app/core/`
  (`enhanced_logging.py`, `logging_config.py`).

## How This Folder Fits Into the AI Workflow
Not workflow logic — it provides request-level observability around all API calls, including
workflow execution requests.

## Developer Notes
- Body logging is off by default (`log_request_body=False` in `main.py`); enable temporarily for
  debugging only.

## Things to Be Careful About
- Middleware wraps streaming (SSE) responses too — be careful not to buffer/consume streams when
  modifying it.

## Related Documentation Files
[../../BACKEND.md](../../BACKEND.md) · [../core/CORE.md](../core/CORE.md)
