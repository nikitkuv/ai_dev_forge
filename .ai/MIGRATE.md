# AI Development Forge Migration Router

## Purpose

Upgrade a consumer repository from an active `.ai/` bundle using a local Forge clone, an already staged `.ai-next/`, or an explicitly approved remote release. The migration itself is deterministic local tooling; this router tells the agent how to stage the release, drive the command, and interpret its findings. The user does not operate preview tokens or compose apply commands.

## Agent-First Entry Point

The normal request is short. When the Forge clone is open in the agent session:

```text
Update AI Development Forge in the project at <path-to-consumer> using this Forge clone.
Read .ai/MIGRATE.md and run the migration for me.
Stage and preview it yourself, ask only for real decisions and final approval, then apply it yourself.
Do not ask me to copy preview tokens or assemble commands.
```

The reverse layout is equally valid: when the consumer repository is open, the user may name `<path-to-ai_dev_forge>` and ask the agent to read `<path-to-ai_dev_forge>/.ai/MIGRATE.md`. Resolve source and target from those explicit paths: this file's `.ai/` is the release source, while the named consumer project is the target; or the open consumer is the target while the named Forge clone is the source. Never assume the Forge clone itself is the target unless the user explicitly says so. The user's request naming local source and target is sufficient authority to read and stage them. If the user requests a remote/latest release instead, clone or download only with the applicable explicit authority.

## Prepare the Layout

The target starts with an active old release and must be staged as follows:

```text
.ai/       # active old release
.ai-next/  # staged new release copied by the agent
```

If `.ai-next/` does not exist, the agent copies the release clone's `.ai/` directory to `.ai-next/` using the platform-specific local-copy procedure in `MIGRATION.md`. Before copying, verify both manifests and require the source version to be newer. The staged bundle must contain only release/framework-owned content: never import `project.yaml`, `framework.lock`, `custom/`, `integrations/`, `local/`, or any other project-owned state from a source consumer. Do not copy the release over the active `.ai/` before preview and approval.

If `.ai-next/` already exists, inspect its manifest and origin instead of overwriting it. Stop on a source or version mismatch. Do not ask the user to perform these staging steps.

## Run the Command

```text
python .ai-next/tools/forge.py migrate --diff
```

Preview is read-only. It computes the complete change set as a pure function of repository state — framework replacements, provenance-proven deletions, preserved unknown files, rendered routers and adapters, the version bump and explicit configuration decisions, the offline integration matrix, and a protected-path fingerprint — bound to one preview token. Execute the command; do not re-derive its results by reading and comparing files yourself. Explain the result concisely and keep the token as agent working data; never ask the user to copy or type it.

## Interpret Findings

- `router_extraction_required`: no `.ai/custom/router-shared.md` exists. Perform the one judgment task — extract preserved project-owned router content from the old `AGENTS.md`/`CLAUDE.md` (title, overview, project map, confirmed commands, domain constraints, protected directories; never legacy Forge lifecycle rules, routing, or agent/skill lists), get user approval, and pass the file via `--router-shared`. The command writes it to `.ai/custom/router-shared.md`.
- `legacy_overlay_present`: reconcile `.ai/custom/codex-router.md`/`claude-router.md` into the extracted shared overlay first.
- `config_decision_required`: collect one explicit `--set key=value` per listed key from the user; suggestions are informational and are never written without approval. Approved values are never overwritten silently.
- `unexpected_staged_file`, `downgrade_refused`, `already_current`, `render_validation`, `integration_ownership_collision`: report and stop; do not work around the gate.
- Advisory findings (`backfill_available`, `version_note`, `breaking_change`, `terminal_backlog_rows`, `preserved_unknown`, `dirty_git_tree`, isolated integration classes): relay them; backfill commands run later as separate user decisions, never inside the migration.

## Apply

After resolving blockers, re-run preview, explain the exact final scope, and ask for final approval. After the user approves it, apply the same reviewed token yourself:

```text
python .ai-next/tools/forge.py migrate --apply PREVIEW_TOKEN [--set ...] [--router-shared path] [--approve-collision path ...]
```

`--approve-collision` requires explicit user authority for that exact path (a manually edited generated output or a preserved unknown file slated for deletion). Apply runs one guarded transaction: backup journal, atomic writes with the lock last, validation, protected-path re-hash, and `.ai-next/` removal on success. Any failure rolls everything back and keeps the staged bundle; report the failed stage and re-preview. An interrupted transaction recovers only through `migrate --recover`, which refuses to overwrite later user edits.

The normal workflow must stay agent-operated end to end. Give the user manual commands only when they explicitly request them.

## Offline and Adapter Scope

The migration runs entirely offline, without invoking MCP, API, CLI, or other connectors; integration classification is structural. Adapter changes stay within the manifest-declared local set: `.codex/agents/`, `.claude/agents/`, `.opencode/agents/`, `.agents/skills/`, and both managed launchers, rendered deterministically from the staged templates. Remove only OpenCode files proven by the prior lock to be Forge-managed; `opencode.json`, commands, plugins, skills, and unlisted agents remain project-owned. New managed IDs (including the fast `mutation-runner` and strong `mutation-analyzer`) replace recognized legacy Forge entries while unlisted files are preserved.

## Protected Project State

All project-owned and canonical paths pass through byte-for-byte: `SPEC.md`, `ARCHITECTURE.md`, `BACKLOG.md`, `DECISIONS.md`, `decisions/`, `execution/`, `investigations/`, `intents/`, `.ai/integrations/`, `quality/mutation-testing/` (the exact mutation history), project configuration beyond the declared migration keys, code, tests, and unrelated configuration. Integration definitions are classified offline and block only their consumers. Framework migration and integration-schema migration are separate approvals and transactions. Report canonical contradictions as compatibility findings; never edit canonical content here. Post-migration compatibility findings are resolved through `forge-resume-development` and the required user gates; a legacy Epic cannot finish fuzzing or Epic Acceptance without current Epic Validation evidence.

## Manual Fallback (no Python)

When Python or the pinned dependencies are unavailable, perform the migration manually under the same contract: read both manifests, contracts and project state; hash protected paths; show the complete diff (bundle replacement, shared-overlay extraction, rendered routers, adapter changes, deletions with provenance, integration matrix); get explicit approval; back up; apply atomically; validate; write `.ai/framework.lock` last; roll back completely on any failure. The command remains the canonical path; treat manual results as needing the same evidence.
