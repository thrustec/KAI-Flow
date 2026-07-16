# Project Overview

## What KAI-Flow Is
KAI-Flow is an open-source (Apache 2.0) **visual platform for building AI-powered assistants and
workflow automations**. Users drag nodes onto a canvas, connect them, configure them through
auto-generated forms, test them live in a chat panel, and deploy them — via REST API, webhooks,
timers, Kafka, or an embeddable chat widget for third-party websites.

Developed by Kafein (GitHub org `kafein-product-space`, active remote `kafein-technology`).
Website: kaiflow.io. Comparable in spirit to Flowise/n8n, implemented on LangChain + LangGraph.

## The Problem It Solves
Building production LLM applications normally requires hand-writing LangChain/LangGraph code:
wiring models, tools, memory, retrieval, triggers, credentials, and deployment. KAI-Flow turns
that into a visual, testable, deployable experience:

- **No-code composition** — LLMs, agents, tools, RAG pipelines, and triggers as canvas blocks.
- **Full lifecycle** — design → configure (credentials vault, variables) → test (chat + live log
  terminal, SSE streaming) → operate (executions history, scheduling, webhooks) → distribute
  (widget embed, export bundles, external workflows).
- **AI-assisted building** — the AI Builder generates or edits a workflow graph from a natural-
  language description.

## Typical Scenarios
- Customer-support / Q&A assistant over internal documents (RAG with pgvector).
- Web-research agent (ReAct agent + Tavily search) embedded on a website via the widget.
- Scheduled automation (timer/cron) or event-driven flows (webhook, Kafka message).
- API orchestration (HTTP client node + JSON parsing + conditions + code node).
- LLM security testing (red-team nodes powered by deepteam).

## System Architecture (high level)

```
┌──────────────┐   HTTP/SSE   ┌───────────────────────────────┐
│  client/     │◄────────────►│  backend/ (FastAPI, /api/v1)  │
│  React 19    │              │  ┌─────────────────────────┐  │
│  XYFlow      │              │  │ Engine (LangGraph)      │  │
│  canvas      │              │  │ GraphBuilder + FlowState│  │
└──────────────┘              │  │ Node registry (~31)     │  │
┌──────────────┐              │  └───────────┬─────────────┘  │
│  widget/     │◄────────────►│              │                │
│  embeddable  │              │  Services / AI Builder        │
│  chat        │              └──────┬────────────────────────┘
└──────────────┘                     │ SQLAlchemy (async)
   third-party sites          ┌──────▼────────┐   LLM/tool APIs
                              │ PostgreSQL 15 │   (OpenAI-compatible,
                              │  + pgvector   │    Tavily, Cohere, …)
                              └───────────────┘
Triggers: webhooks · timers/cron (APScheduler) · Kafka · error-triggers
```

- The **frontend** builds a `flow_data` JSON graph (nodes + edges).
- The **backend engine** validates it, compiles it to a LangGraph `StateGraph`, and executes it
  with streaming feedback.
- **PostgreSQL + pgvector** stores everything: users, workflows, executions, chat, memory,
  documents, embeddings.
- The **widget** and **export-docker** bundle carry finished assistants to the outside world.

## Deeper Reading
[ai-workflow.md](ai-workflow.md) · [tech-stack.md](tech-stack.md) ·
[project-structure.md](project-structure.md) · [../CLAUDE.md](../CLAUDE.md)
