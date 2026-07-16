# KAI-Flow Documentation Index

Central documentation for the KAI-Flow repository. Generated from a full source scan
(2026-07-07); every statement is grounded in the actual code. Start with
[../CLAUDE.md](../CLAUDE.md) for the working rules.

## Contents

| Document | What it covers |
|---|---|
| [codebase-learning-guide.tr.md](codebase-learning-guide.tr.md) | Başlangıç seviyesinde, sade Türkçe adım adım kod tabanı rehberi |
| [project-overview.md](project-overview.md) | What KAI-Flow is, the problem it solves, use cases |
| [project-structure.md](project-structure.md) | Full folder map with links to folder-level docs |
| [ai-workflow.md](ai-workflow.md) | How the AI workflow engine works end to end |
| [tech-stack.md](tech-stack.md) | Technologies per layer and why they're used |
| [backend.md](backend.md) | Backend architecture summary |
| [frontend.md](frontend.md) | Frontend + widget architecture summary |
| [api.md](api.md) | REST API surface |
| [database.md](database.md) | PostgreSQL/pgvector schema overview |
| [configuration.md](configuration.md) | Environment variables & config files |
| [deployment.md](deployment.md) | Docker, export bundles, CI/CD |
| [development-guidelines.md](development-guidelines.md) | How to contribute changes safely |

## Folder-level docs (live next to the code)

Backend: [backend/BACKEND.md](../backend/BACKEND.md) ·
[api](../backend/app/api/API.md) · [auth](../backend/app/auth/AUTH.md) ·
[core](../backend/app/core/CORE.md) · [middleware](../backend/app/middleware/MIDDLEWARE.md) ·
[models](../backend/app/models/MODELS.md) · [nodes](../backend/app/nodes/NODES.md) ·
[routes](../backend/app/routes/ROUTES.md) · [schemas](../backend/app/schemas/SCHEMAS.md) ·
[services](../backend/app/services/SERVICES.md) ·
[migrations](../backend/migrations/MIGRATIONS.md) · [scripts](../backend/scripts/SCRIPTS.md) ·
[tests](../backend/tests/TESTS.md)

Frontend: [client/CLIENT.md](../client/CLIENT.md) ·
[components](../client/app/components/COMPONENTS.md) · [routes](../client/app/routes/ROUTES.md) ·
[services](../client/app/services/SERVICES.md) · [stores](../client/app/stores/STORES.md) ·
[lib](../client/app/lib/LIB.md)

Other: [widget/WIDGET.md](../widget/WIDGET.md) ·
[export-docker/EXPORT-DOCKER.md](../export-docker/EXPORT-DOCKER.md)

## Upstream docs (pre-existing, still authoritative for their topics)
[README.md](../README.md) (quick start) · [USER_GUIDE.md](../USER_GUIDE.md) (ops/install guide) ·
[CONTRIBUTING.md](../CONTRIBUTING.md) (contribution & node-type guide) ·
[backend/README.md](../backend/README.md) · [widget/README.md](../widget/README.md) ·
[client/DOCKER_README.md](../client/DOCKER_README.md)

## Maintenance rule
Code changes **must** update the affected folder-level `.md` and the related file(s) here in the
same change set (see "Documentation Reference Rules" in [../CLAUDE.md](../CLAUDE.md)).
