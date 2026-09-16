---
name: forge-migrate-framework
description: Use when a consumer repository already contains an older AI Development Forge bundle and a newer release is staged at `.ai-next/`, including legacy installations without a lock.
---

# Migrate the Framework

The migration is a deterministic local command. Your job is staging, relaying its output, collecting the few decisions that require judgment, and reporting — never performing mechanical migration steps yourself. Do not reimplement discovery, hashing, diffing, rendering, replacement, validation, locking, or rollback by hand.

## Prerequisites

1. Require the active `.ai/` bundle and a staged `.ai-next/` bundle of a newer release. If `.ai-next/` is absent, stage it with the documented shell one-liner (local copy, or the sparse-clone script from `MIGRATION.md`) after the user confirms the source. Never download or clone anything without explicit approval.
2. Python 3.11+ with the pinned `.ai-next/tools/requirements.txt` dependencies must be available. If it is not, stop and use the manual migration path documented in `.ai-next/MIGRATE.md` — do not approximate the command's behavior.

## Run the command

```text
python .ai-next/tools/forge.py migrate --diff
```

Relay the preview verbatim: versions, change set, deletions, preserved unknown files, collisions, configuration decisions, integration matrix, and every finding. Exit code 1 means blocking findings — show them before anything else.

## Resolve blocking findings

- `router_extraction_required` — the only judgment task. Extract the preserved project-owned router content (project title, overview, project map, confirmed commands, domain constraints, protected directories — never legacy Forge lifecycle rules, routing, agent/skill lists, or generic process instructions) from the old `AGENTS.md`/`CLAUDE.md` into one Markdown file inside the project, show it to the user for approval, and pass it via `--router-shared <path>`. The command stores it as `.ai/custom/router-shared.md`.
- `config_decision_required` — present each listed key with its suggestion and the user's decision; pass values via `--set key=value`. Never write a suggestion without approval and never overwrite an already-approved value; the skill adds no new mode. For an OpenCode-led project with no approved route, propose the existing `native_subagents` value by default and record it only after explicit approval.
- `legacy_overlay_present` — reconcile legacy platform-specific overlays with the user first; the merge result enters through `--router-shared`.
- `unexpected_staged_file`, `downgrade_refused`, `already_current`, `render_validation`, `integration_ownership_collision` — report and follow the finding's guidance; do not work around them.

Advisory findings (`backfill_available`, `version_note`, `breaking_change`, `terminal_backlog_rows`, `preserved_unknown`, `dirty_git_tree`, isolated integration classes) are reported, not acted on. Backfill commands are quoted for the user to run later; never execute them inside the migration. A dirty Git tree is the user's recoverable baseline.

Legacy TASK semantics are fixed, not interpreted: Missing legacy delivery track means standard for every in-flight state, and the migration must never synthesize fast eligibility or assurance — an already-started standard TASK never downgrades, and a pre-start change to fast requires Replan and complete evidence.

## Apply and report

Re-run the preview after each decision so the token matches the reviewed state, then:

```text
python .ai-next/tools/forge.py migrate --apply PREVIEW_TOKEN [--set key=value ...] [--router-shared path] [--approve-collision path ...]
```

`--approve-collision` may authorize overwriting a manually edited generated output listed in `collisions` or deleting a listed `preserved_unknown` file — only with explicit user authority for that exact path. On success report the applied set, deleted paths, and the new version. On failure the command rolls back and retains `.ai-next/`; report the failed stage and re-run the preview. An interrupted transaction is recovered only through `migrate --recover`.

## Boundaries

Canonical documents, decisions, execution state, `investigations/`, `intents/`, integrations, the exact mutation history under `quality/mutation-testing/` (the `mutation-runner`/`mutation-analyzer` IDs are managed, the history is not), project code, tests, and unrelated configuration are never migration inputs — the command preserves them byte-for-byte and verifies it by re-hashing. Everything runs offline, without invoking MCP, API, CLI, or other connectors. Framework migration and integration-schema migration remain separate approvals; an `older_migratable` schema is offered only as a separate project-owned change. Approval of the migration authorizes no canonical edits, product changes, commits, or pushes.
