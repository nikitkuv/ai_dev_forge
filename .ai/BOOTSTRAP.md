# AI Development Forge Bootstrap Router

## Purpose

Initialize a consumer product repository for coordinated development with Codex CLI and Claude Code CLI. Bootstrap creates approved canonical documents, one gated execution workspace, both native adapter sets, and recoverable project configuration.

Bootstrap does not implement product features or initialize the AI Development Forge source repository itself.

If the repository already has an active Forge `.ai/` and a newer bundle staged at `.ai-next/`, stop bootstrap and read `.ai-next/MIGRATE.md`. Bootstrap is only for first initialization or first adoption.

## Entry Modes

Determine and record one mode before starting:

- **new** — begin from the user's product description, linked brief, or iterative interview;
- **existing** — inspect repository evidence before interviewing and adopting target-state canonical documents.

If the user intent or repository type is ambiguous, ask. Never infer that an existing implementation is the desired product.

## Preflight

1. Confirm `.ai/framework/manifest.yaml`, `.ai/framework/contracts.yaml`, `.ai/CONVENTIONS.md`, numbered steps, neutral agents, portable skills, and templates belong to the same framework release.
2. Confirm the repository is a consumer project. If it is the framework source repository, stop without creating root canonical documents or generated adapters.
3. Inspect root canonical files, `.ai/project.yaml`, `.ai/framework.lock`, `.ai/custom/`, generated adapters, Git state, and unrelated user files.
4. Determine with the user:
   - bootstrap mode;
   - documentation language;
   - both enabled platforms: Codex and Claude;
   - whether the project accepts the bundled default `strong`, `balanced`, and `fast` model mappings or explicitly overrides them;
   - Git policy: `manual` or `auto_commit_after_acceptance`.
5. After these settings are approved, create or update `.ai/project.yaml` from `.ai/templates/project.yaml` immediately. Persist the documentation language, both platforms, the accepted defaults or explicit model overrides, and Git policy so interrupted bootstrap can recover without conversation history. Step 05 revalidates this configuration before rendering.
6. Detect collisions with existing canonical files, project configuration, custom overlays, or generated adapters. Show the exact affected paths and request confirmation before overwriting project work.
7. Create no framework hooks, MCP configuration, or CLI dependency. Existing project-owned hooks or MCP remain outside framework ownership.

## Interrupted Bootstrap Recovery

Session history is not authoritative.

Before starting or repeating a step:

1. inspect canonical frontmatter and approval metadata;
2. inspect `.ai/project.yaml`, `.ai/framework.lock`, adapter hashes, directory state, and Git diff;
3. identify the first incomplete or invalid numbered step;
4. preserve approved outputs and resume from that step;
5. rerun any validation or generation stage whose durable result is missing or stale.

Do not recreate approved documents merely because the current session did not create them.

## Six Gated Steps

Run these files in order and read each one in full before acting:

1. [Product Discovery](01-product-discovery.md) — create approved target `SPEC.md`.
2. [System Design](02-system-design.md) — create approved `ARCHITECTURE.md`, ADRs, and generated `DECISIONS.md`.
3. [Release Planning](03-release-planning.md) — create approved Epic Roadmap and Defect Queue in `BACKLOG.md`.
4. [Prepare Workspace](04-prepare-workspace.md) — approve one Epic plan and TASK definitions, then use the Epic Start gate.
5. [Create Platform Adapters](05-create-platform-adapters.md) — write project configuration and generate both native adapter sets.
6. [Final Validation](06-final-validation.md) — verify canonical state, lifecycle, ownership, adapters, and recovery.

Each step has its own explicit user approval. Report its proposed outputs and wait before entering the next step. Approval of one step never implies Task Start or another later gate.

## Ownership and Language

- Framework-owned release content stays under `.ai/` as declared by the manifest.
- `.ai/project.yaml`, `.ai/framework.lock`, `.ai/custom/`, canonical documents, ADRs, and execution state are project-owned.
- Root routers and native agent/skill directories are generated adapter outputs; detect manual edits before regeneration.
- Write framework control text, generated routers, agent contracts, and skills in English.
- Write root canonical documents in the user's documentation language. Keep IDs, statuses, paths, model IDs, and commands in English.

## Bootstrap Boundaries

Do not:

- write or refactor product code;
- invent requirements, architecture, priority, acceptance, or model overrides;
- create report, progress, checkpoint, review, testing, fuzzing, security, or validation Markdown files;
- modify canonical scope or decisions without the applicable approval gate;
- commit unless the configured Git policy and user authorization permit it.

## Completion

Bootstrap is complete only when Step 06 passes. If an Epic was activated, every initial TASK must still be `TODO`; end by asking for a separate Task Start authorization.
