# AI Workflow Architecture

How a workflow goes from pixels on the canvas to LangGraph execution. All paths relative to repo
root.

## 1. The workflow definition (`flow_data`)
The canvas ([client/app/components/canvas/FlowCanvas.tsx](../client/app/components/canvas/FlowCanvas.tsx))
produces XYFlow-format JSON stored on `Workflow.flow_data`
([backend/app/models/workflow.py](../backend/app/models/workflow.py)):

```json
{
  "nodes": [{ "id": "node_1", "type": "StartNode", "position": {...}, "data": {...} }, ...],
  "edges": [{ "source": "node_1", "target": "node_2", "sourceHandle": "output", "targetHandle": "input" }, ...]
}
```
`type` must match a registered backend node class name.

## 2. Nodes — the building blocks
Defined in [backend/app/nodes/](../backend/app/nodes/NODES.md). Contract in `base.py`:

- `NodeType.PROVIDER` — factory: builds a LangChain object from config only (OpenAI LLM, Tavily
  tool, embeddings, retriever, reranker).
- `NodeType.PROCESSOR` — orchestrator: consumes connected inputs (ReAct agent, condition, code,
  HTTP client, vector store orchestrator, splitters, loaders, red-team nodes).
- `NodeType.TERMINATOR` — finalizer/transformer (Start/End, webhook trigger & response, timer).
- `NodeType.MEMORY` — conversation persistence (BufferMemory).

`NodeMetadata` declares inputs/outputs (`NodeProperty`) and drives the auto-generated
configuration UI ([client/app/components/node/GenericNodeForm.tsx](../client/app/components/node/GenericNodeForm.tsx)).
Registration is automatic: [backend/app/core/node_registry.py](../backend/app/core/node_registry.py)
discovers all concrete `BaseNode` subclasses at startup (~31 node classes as of 2026-07).

## 3. Engine & compilation
There are two engine entry layers over the same `GraphBuilder` runtime:

- [backend/app/core/engine.py](../backend/app/core/engine.py): `get_engine()` →
  `LangGraphWorkflowEngine` (singleton; `StubWorkflowEngine` if `AF_USE_STUB_ENGINE=true`). This
  interface is initialized during backend startup and exposes `validate` / `build` / `execute`.
- The primary ad-hoc/canvas execution path currently goes through
  `WorkflowExecutor` → `WorkflowExecutionEnhancer` → `DynamicWorkflowEngine`. The enhancer creates
  a fresh dynamic engine per request, then delegates compilation and execution to `GraphBuilder`.
  See `workflow_enhancer.py` and `dynamic_workflow_engine.py` in
  [backend/app/core/](../backend/app/core/CORE.md).

The standard engine interface provides:

- `validate(flow_data)` — structural checks with helpful errors (unknown type suggestions,
  isolated-node warnings).
- `build(flow_data)` — delegates to `GraphBuilder`
  ([backend/app/core/graph_builder/](../backend/app/core/CORE.md)) which compiles a LangGraph
  `StateGraph` using: `ConnectionMapper` (edges → typed connections), `NodeExecutor` (wraps node
  `execute()`), `ControlFlowManager` (branching), `ValidationEngine`, with `MemorySaver`
  checkpointing.
- `execute(inputs, stream=?, user_context=?)` — runs the compiled graph; returns a dict or an
  async generator of SSE events. Wrapped by `@trace_workflow`
  ([backend/app/core/tracing.py](../backend/app/core/tracing.py)); optional LangSmith tracing via
  `LANGCHAIN_TRACING_V2`.

State: `FlowState` ([backend/app/core/state.py](../backend/app/core/state.py)) with merge
reducers so parallel branches can write `node_outputs` / `executed_nodes` / `errors` safely.

## 4. Execution entry points
| Entry | Where |
|---|---|
| Ad-hoc/canvas run (SSE) | `POST /api/v1/workflows/execute` ([backend/app/api/workflows.py](../backend/app/api/workflows.py)) |
| Chat interaction | `POST /api/v1/chat/{chatflow_id}/interact` ([backend/app/api/chat.py](../backend/app/api/chat.py)) |
| Webhooks (test + production routers) | [backend/app/nodes/triggers/webhook_trigger.py](../backend/app/nodes/triggers/webhook_trigger.py), [backend/app/api/webhooks.py](../backend/app/api/webhooks.py) |
| Timers / scheduled jobs | [backend/app/api/timers.py](../backend/app/api/timers.py), [scheduled_jobs.py](../backend/app/api/scheduled_jobs.py) (APScheduler + croniter) |
| Kafka messages | `KafkaTriggerNode` + `kafka_reconciliation_loop` started in [backend/main.py](../backend/main.py) lifespan |
| Error triggers | `ErrorTriggerNode` — run a workflow when another fails |
| Widget / external callers | widget chat → backend; API keys / `MASTER_API_KEY` for auth |

Service-side glue: [backend/app/services/workflow_executor.py](../backend/app/services/workflow_executor.py).
For the ad-hoc endpoint, that service creates/tracks the execution record, calls the fresh-engine
build path, wraps the async stream, and finalizes the database status.

## 5. AI Builder (LLM generates the workflow)
[backend/app/services/ai_builder/](../backend/app/services/SERVICES.md) — `AIBuilderOrchestrator`:
1. **Skeleton phase** — LLM (AsyncOpenAI, default `gpt-4o`, custom `base_url` supported) gets a
   compiled node catalog + connection rules and returns a graph skeleton.
2. **Parameterization phase** — second prompt fills node parameters.
3. `validator.py` (structure + topology) → `hydrator.py` (defaults) → `layout_engine.py`
   (positions) → `diff_engine.py` (edit mode changesets against an existing workflow).

## 6. RAG pipeline (as nodes)
DocumentLoader / WebScraper → ChunkSplitter → OpenAIEmbeddings → VectorStoreOrchestrator
(pgvector) → Retriever (+ CohereReranker) → Agent/LLM. Persistence:
`vector_collections`/`vector_documents` + document tables
([database.md](database.md)).

## 7. Memory & chat
`BufferMemoryNode` + [backend/app/services/memory/](../backend/app/services/SERVICES.md) persist
conversation state (`memories`, `chat_message` tables); `session_id` in `user_context` scopes a
conversation.

## Related docs
[backend.md](backend.md) · [api.md](api.md) · [database.md](database.md) ·
folder docs: [NODES.md](../backend/app/nodes/NODES.md), [CORE.md](../backend/app/core/CORE.md),
[SERVICES.md](../backend/app/services/SERVICES.md)
