# backend/app/nodes/ — Workflow Node Classes (Plugin System)

## Folder Purpose
Every block a user can drag onto the canvas is a Python class in this folder. Nodes are
auto-discovered at startup by `app/core/node_registry.py` — dropping a new file here registers a
new node with zero extra wiring. Node `metadata` also drives the frontend form UI automatically.

## What This Folder Contains
- `base.py` — the contract: `BaseNode` and its abstract subclasses `ProviderNode`,
  `ProcessorNode`, `TerminatorNode`, `MemoryNode`; `NodeType` enum (PROVIDER / PROCESSOR /
  TERMINATOR / MEMORY); `NodeMetadata`, `NodeProperty` (typed inputs/outputs + UI field types
  like `text`, `select`, `credential-select`, `code-editor`, `json-editor`, `session-id`, …).
- `__init__.py` — package exports (`BaseNode` etc.).
- One subfolder per category (category names surface in the frontend sidebar).

## File-by-File Explanation (all concrete nodes)
| Category | File | Class (base) | Role |
|---|---|---|---|
| default | `start_node.py` | `StartNode` (Terminator) | Workflow entry point |
| default | `end_node.py` | `EndNode` (Terminator) | Workflow exit / final output |
| agents | `react_agent.py` | `ReactAgentNode` (Processor) | LangChain ReAct agent combining LLM + tools + memory |
| llms | `openai_node.py` | `OpenAINode` (BaseNode) | OpenAI chat models provider |
| llms | `openai_compatible_node.py` | `OpenAICompatibleNode` (BaseNode) | Any OpenAI-compatible endpoint (custom base_url) |
| tools | `tavily_search.py` | `TavilySearchNode` (Provider) | Tavily web search tool |
| tools | `http_client.py` | `HttpClientNode` (Processor) | HTTP requests from workflows |
| tools | `retriever.py` | `RetrieverProvider` (Provider) | Vector-store retriever for RAG |
| tools | `cohere_reranker.py` | `CohereRerankerNode` (Provider) | Cohere reranking for retrieval |
| tools | `markitdown_tool.py` | `MarkItDownToolNode` (Provider) | Document→markdown conversion tool |
| memory | `buffer_memory.py` | `BufferMemoryNode` (Memory) | Conversation buffer memory |
| embeddings | `openai_embeddings_provider.py` | `OpenAIEmbeddingsProvider` (Provider) | OpenAI embeddings |
| vector_stores | `vector_store_orchestrator.py` | `VectorStoreOrchestrator` (Processor) | pgvector store/search orchestration |
| splitters | `chunk_splitter.py` | `ChunkSplitterNode` (Processor) | Text chunking for RAG |
| document_loaders | `document_loader.py` | `DocumentLoaderNode` (Processor) | Load documents (PDF/DOCX/… via pypdf, python-docx, markitdown) |
| document_loaders | `web_scraper.py` | `WebScraperNode` (Processor) | Scrape web pages (BeautifulSoup/lxml) |
| processing | `code_node.py` | `CodeNode` (Processor) | Execute user Python code |
| processing | `condition_node.py` | `ConditionNode` (Processor) | Branching / control flow |
| processing | `json_parser_node.py` | `JsonParserNode` (Processor) | Parse/extract JSON |
| processing | `cryptography_node.py` | `CryptographyNode` (Processor) | Encrypt/decrypt/hash operations |
| processing | `kafka_producer.py` | `KafkaProducerNode` (BaseNode) | Publish messages to Kafka |
| text_processing | `string_input_node.py` | `StringInputNode` (Processor) | Static/templated text input |
| triggers | `webhook_trigger.py` | `WebhookTriggerNode` (Terminator) | Inbound webhooks; also defines `webhook_test_router` & `webhook_production_router` (mounted in `main.py`) |
| triggers | `respond_to_webhook.py` | `RespondToWebhookNode` (Terminator) | Custom webhook response |
| triggers | `timer_start_node.py` | `TimerStartNode` (Terminator) | Cron/timer-started workflows |
| triggers | `kafka_trigger.py` | `KafkaTriggerNode` (BaseNode) | Kafka-consumer trigger; defines `kafka_router`, `KafkaListenerService`, `kafka_reconciliation_loop` (started in `main.py` lifespan) |
| triggers | `error_trigger.py` | `ErrorTriggerNode` (BaseNode) | Runs a workflow when another errors |
| security | `llm_red_team_node.py` | `LLMRedTeamNode` (Processor) | LLM red-team testing (deepteam) |
| security | `agentic_red_team_node.py` | `AgenticRedTeamNode` (Processor) | Agentic red-team scenarios |
| security | `custom_red_team_node.py` | `CustomRedTeamNode` (Processor) | Custom red-team probes |
| decorative | `sticky_note.py` | `StickyNoteNode` (Terminator) | Canvas sticky note (no runtime role) |

## Important Files
`base.py` is the single most important file — read it fully before writing a node.

## Relationship With Other Folders
- Instantiated/executed by `app/core/graph_builder/`; discovered by `app/core/node_registry.py`.
- Metadata is served via `app/api/nodes.py` and rendered by
  `client/app/components/node/GenericNodeForm.tsx` (field components in
  `client/app/components/node/fields/`).
- Credentials referenced by `credential-select` fields resolve through
  `app/core/credential_provider.py`.

## How This Folder Fits Into the AI Workflow
Nodes wrap LangChain/LangGraph building blocks (LLMs, tools, retrievers, memory) so the visual
canvas can compose them. Node type determines execution semantics: PROVIDER creates objects,
PROCESSOR orchestrates, TERMINATOR finalizes, MEMORY persists conversation state.

## Developer Notes — Adding a Node
1. Pick the category folder (or create one; discovery is recursive).
2. Subclass the right base (`ProviderNode`/`ProcessorNode`/`TerminatorNode`/`MemoryNode`).
3. Define `metadata` (`NodeMetadata`): `name` (unique, used as flow `type`), `display_name`,
   `category`, `inputs`/`outputs` (`NodeProperty`).
4. Implement `execute(...)` returning JSON-serializable output (use
   `app/core/json_utils.make_json_serializable_with_langchain` for LangChain objects).
5. Restart backend; the node appears in the canvas sidebar automatically.
See also [CONTRIBUTING.md](../../../CONTRIBUTING.md) (node-type patterns explained by maintainers).

## Things to Be Careful About
- `NodeProperty.name` must match `^[a-zA-ZçÇğĞıİöÖşŞüÜ_][a-zA-ZçÇğĞıİöÖşŞüÜ0-9_]*$` (Python
  identifier incl. Turkish chars).
- `webhook_trigger.py` and `kafka_trigger.py` are **not just nodes** — they define FastAPI routers
  and background services mounted in `backend/main.py`. Renaming/moving them breaks startup.
- `CodeNode` executes user-supplied Python — treat changes as security-sensitive.
- Node `name` values are referenced by saved workflows in the DB; renaming a node breaks existing
  workflows.

## Related Documentation Files
[../core/CORE.md](../core/CORE.md) · [../../BACKEND.md](../../BACKEND.md) ·
[../../../docs/ai-workflow.md](../../../docs/ai-workflow.md) ·
[../../../client/app/components/COMPONENTS.md](../../../client/app/components/COMPONENTS.md)
