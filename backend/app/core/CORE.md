# backend/app/core/ — Engine & Platform Core

## Folder Purpose
The platform core: workflow engine, LangGraph graph builder, node registry/discovery, database
layer, configuration, security/encryption, logging/tracing. Everything the rest of the backend
builds on.

## What This Folder Contains / File-by-File Explanation

### Workflow engine & execution
- `engine.py` — `BaseWorkflowEngine` ABC; `StubWorkflowEngine` (debug, `AF_USE_STUB_ENGINE=true`);
  `LangGraphWorkflowEngine` (default): `validate()` → `build()` → `execute()` (sync or async
  generator for streaming). `get_engine()` returns the cached singleton.
- `workflow_enhancer.py` + `dynamic_workflow_engine.py` — the primary ad-hoc/canvas execution
  path creates a fresh `DynamicWorkflowEngine` per request, then builds and executes through the
  same `GraphBuilder`. This avoids sharing a mutable compiled graph between those requests.
- `graph_builder/` — compiles flow JSON to a compiled LangGraph `StateGraph`:
  - `__init__.py` — `GraphBuilder` orchestrator (build_from_flow, execute, checkpointer selection)
  - `connection_mapper.py` — maps visual edges to node input/output connections
  - `node_executor.py` — wraps node `execute()` calls for LangGraph
  - `control_flow.py` — control-flow handling (conditions/branching)
  - `validation.py` — `ValidationEngine` structural checks
  - `types.py` — `NodeConnection`, `GraphNodeInstance`, `ControlFlowType`, `TERMINAL_NODE_TYPES`…
  - `exceptions.py` — `WorkflowError`, `NodeExecutionError`, `ConnectionError`, `ValidationError`
- `state.py` — `FlowState` (Pydantic) LangGraph state + merge reducers (`merge_node_outputs`,
  `merge_executed_nodes`, `merge_errors`) for parallel branches.
- `node_registry.py` — `NodeRegistry`: auto-discovers `BaseNode` subclasses under `app/nodes/`,
  `get_node(name)`, `get_nodes_by_category(...)`.
- `node_discovery.py`, `node_handlers.py`, `dynamic_node_analyzer.py`, `dynamic_type_detection.py`,
  `dynamic_workflow_engine.py`, `workflow_enhancer.py`, `auto_connector.py`,
  `compatibility_layer.py` — discovery/handler/type-inference helpers around the engine.
- `checkpointer.py` — LangGraph checkpoint support; `execution_queue.py` — execution queueing;
  `active_tasks.py` — tracking running tasks; `output_cache.py` — node output caching +
  `default_connection_extractor`; `connection_manager.py` / `connection_pool.py` — connection
  handling; `memory_manager.py` — memory management for conversation state.
- `tool/` — tool integration subsystem: `interfaces.py`, `detector.py` (detects tool-capable
  objects), `converter.py` (converts nodes/objects into LangChain tools), `manager.py`.

### Configuration & security
- `constants.py` — **all env-derived settings** (SECRET_KEY, DATABASE_URL, CREDENTIAL_MASTER_KEY
  (required!), MASTER_API_KEY, Keycloak, LangSmith, pool sizes, API_START/API_VERSION…).
- `config.py` — additional config helpers.
- `encryption.py` — credential encryption (Fernet); `env_encryption.py` — optional encrypted
  `.env` values (paired with `backend/encrypt_env.py`); `credential_provider.py` /
  `credential_fields.py` — resolving stored credentials into node parameters.
- `security.py` — JWT creation/verification (`verify_token` supports local HS256 + Keycloak RS256).

### Data & observability
- `database.py` — async SQLAlchemy engine/session (`get_db_session`), `check_database_health`,
  `get_database_stats`.
- `enhanced_logging.py` (`get_enhanced_logger`, `WorkflowPhase`), `logging_config.py`,
  `logging_settings.py`, `logging_utils.py` — structured/colored logging.
- `tracing.py` (`setup_tracing`, `trace_workflow`, `get_workflow_tracer`) + `enhanced_tracing.py`
  — workflow tracing incl. LangSmith integration.
- `error_handlers.py` (`register_exception_handlers`), `exceptions.py` — global error handling.
- `performance_monitor.py`, `json_utils.py` (LangChain-aware JSON serialization),
  `templating.py` (Jinja2 helpers), `kafka_utils.py`.

## Important Files
`engine.py`, `graph_builder/__init__.py`, `state.py`, `node_registry.py`, `constants.py`,
`database.py`, `security.py`.

## Relationship With Other Folders
- Executes node classes from `app/nodes/`; called by `app/api/` and `app/services/`
  (esp. `workflow_executor.py`); models come from `app/models/`.

## How This Folder Fits Into the AI Workflow
This folder implements the AI workflow runtime itself: flow JSON → validation → LangGraph
StateGraph (with MemorySaver checkpointing) → node execution with FlowState → merged outputs /
streamed events. See [../../../docs/ai-workflow.md](../../../docs/ai-workflow.md).

## Developer Notes
- The `get_engine()` interface is a singleton — config changes need a restart. Do not confuse it
  with the ad-hoc/canvas path, whose workflow enhancer creates a fresh dynamic engine per request.
- `validate()` in `engine.py` gives helpful errors (unknown node type suggestions, isolated-node
  warnings); extend it rather than adding ad-hoc checks elsewhere.
- Long "enterprise"-style module docstrings are the house style here; the code below them is the
  source of truth.

## Things to Be Careful About
- **`CREDENTIAL_MASTER_KEY` is mandatory** — `constants.py` raises at import time without it.
- `state.py` reducers exist to prevent `NoneType` iteration errors during parallel execution —
  keep them when touching FlowState.
- `env_encryption.py` means env values may be encrypted; never read `os.getenv` directly for
  secrets — go through `constants.py`.
- Changing `API_START`/`API_VERSION` breaks the frontend proxy and service URLs.

## Related Documentation Files
[../../BACKEND.md](../../BACKEND.md) · [../nodes/NODES.md](../nodes/NODES.md) ·
[../services/SERVICES.md](../services/SERVICES.md) ·
[../../../docs/ai-workflow.md](../../../docs/ai-workflow.md) ·
[../../../docs/configuration.md](../../../docs/configuration.md)
