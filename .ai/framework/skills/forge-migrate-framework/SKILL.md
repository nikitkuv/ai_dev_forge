---
name: forge-migrate-framework
description: Use when the user asks an agent—whether opened in the Forge clone or the consumer repository—to update a consumer that contains an older AI Development Forge bundle from a local clone, a staged `.ai-next/`, or an explicitly approved remote release, including legacy installations without a lock.
---

# Migrate the Framework

The migration is a deterministic local command operated by the agent. The user should not have to copy a preview token, assemble CLI flags, or read the command documentation. Your job is staging, invoking the command, explaining the meaningful result, collecting the few decisions that require judgment, carrying the token and approved flags into apply, and reporting — never reimplementing discovery, hashing, diffing, rendering, replacement, validation, locking, or rollback by hand.

## Prerequisites

1. Resolve the consumer target and release source from the user's explicit paths. The agent may be opened in either repository: a named consumer path plus the current Forge clone, or the current consumer plus a named Forge clone. Never treat the Forge source clone as the consumer unless the user explicitly names it as the target. Require the target's active `.ai/` bundle. Resolve the new release in this order: the target's existing inspected `.ai-next/`; the local Forge clone; or the remote source explicitly requested or approved by the user. A request such as "update Forge in `TARGET` using this clone" or "update Forge here from `SOURCE`" authorizes reading those local paths and staging the bundle — do not ask the user to confirm them again. Network clone/download still requires explicit authority.
2. If `.ai-next/` is absent, stage the resolved release yourself using the documented local-copy or sparse-clone procedure in `MIGRATION.md`. Verify that the source manifest is a newer version and that only release/framework-owned content enters `.ai-next/`. Never overwrite an existing `.ai-next/`; inspect it and report a source/version mismatch instead. Do not ask the user to run the staging command.
3. Python 3.11+ with the pinned `.ai-next/tools/requirements.txt` dependencies must be available. If it is not, stop and use the manual migration path documented in `.ai-next/MIGRATE.md` — do not approximate the command's behavior.

## Run the command

```text
python .ai-next/tools/forge.py migrate --diff
```

Interpret the preview for the user. Present the old/new versions, exact affected scope, deletions, preserved unknown files, collisions, protected-state result, configuration decisions, integration compatibility, and every finding in concise human language. Exit code 1 means blocking findings — show them before anything else. Keep the machine JSON and `preview_token` as agent working data; never ask the user to copy or re-enter the token. Offer the raw output or full diff when useful or requested.

## Resolve blocking findings

- `router_extraction_required` — the only judgment task. Extract the preserved project-owned router content (project title, overview, project map, confirmed commands, domain constraints, protected directories — never legacy Forge lifecycle rules, routing, agent/skill lists, or generic process instructions) from the old `AGENTS.md`/`CLAUDE.md` into one Markdown file inside the project, show it to the user for approval, and pass it via `--router-shared <path>`. The command stores it as `.ai/custom/router-shared.md`.
- `config_decision_required` — present each listed key with its suggestion and the user's decision; pass values via `--set key=value`. Never write a suggestion without approval and never overwrite an already-approved value; the skill adds no new mode. For an OpenCode-led project with no approved route, propose the existing `native_subagents` value by default and record it only after explicit approval.
- `legacy_overlay_present` — reconcile legacy platform-specific overlays with the user first; the merge result enters through `--router-shared`.
- `unexpected_staged_file`, `downgrade_refused`, `already_current`, `render_validation`, `integration_ownership_collision` — report and follow the finding's guidance; do not work around them.

Advisory findings (`backfill_available`, `version_note`, `breaking_change`, `terminal_backlog_rows`, `preserved_unknown`, `dirty_git_tree`, isolated integration classes) are reported, not acted on. Backfill commands are quoted for the user to run later; never execute them inside the migration. A dirty Git tree is the user's recoverable baseline.

Legacy TASK semantics are fixed, not interpreted: Missing legacy delivery track means standard for every in-flight state, and the migration must never synthesize fast eligibility or assurance — an already-started standard TASK never downgrades, and a pre-start change to fast requires Replan and complete evidence.

## Apply and report

Re-run the preview after each decision so the token matches the reviewed state. Show the final scope and ask for approval of that migration. After approval, run the apply command yourself with the returned token and every approved flag:

```text
python .ai-next/tools/forge.py migrate --apply PREVIEW_TOKEN [--set key=value ...] [--router-shared path] [--approve-collision path ...]
```

`--approve-collision` may authorize overwriting a manually edited generated output listed in `collisions` or deleting a listed `preserved_unknown` file — only with explicit user authority for that exact path. On success report the applied set, deleted paths, and the new version. On failure the command rolls back and retains `.ai-next/`; report the failed stage and re-run the preview. An interrupted transaction is recovered only through `migrate --recover`.

Do not hand the command sequence back to the user unless they explicitly ask for a manual procedure. The normal interaction is: the user names the release source and asks to migrate; the agent stages, previews, resolves decisions, requests one final approval, applies, validates, and reports.

## Boundaries

Canonical documents, decisions, execution state, `investigations/`, `intents/`, integrations, the exact mutation history under `quality/mutation-testing/` (the `mutation-runner`/`mutation-analyzer` IDs are managed, the history is not), project code, tests, and unrelated configuration are never migration inputs — the command preserves them byte-for-byte and verifies it by re-hashing. Everything runs offline, without invoking MCP, API, CLI, or other connectors. Framework migration and integration-schema migration remain separate approvals; an `older_migratable` schema is offered only as a separate project-owned change. Approval of the migration authorizes no canonical edits, product changes, commits, or pushes.
