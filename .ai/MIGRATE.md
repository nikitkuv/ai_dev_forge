# AI Development Forge Migration Router

## Purpose

Upgrade a consumer repository that already contains an older `.ai/` bundle. The new release must be staged at `.ai-next/`; never copy it over the active `.ai/` before preview and approval.

Migration updates only Forge-owned release files, mixed-ownership root routers, and manifest-declared local Forge agents and skills. It does not bootstrap the product again.

## Required Layout

Require both directories:

```text
.ai/       # active old release
.ai-next/  # staged new release containing this file
```

Stop if the directories resolve to the same path, the staged manifest is incomplete, or `.ai-next/` contains anything other than one staged Forge bundle.

## Read-only Discovery

Before writing:

1. read both manifests, contracts, workflows, templates, neutral agents, and portable skills;
2. read the optional old `.ai/framework.lock`, `.ai/project.yaml`, `.ai/custom/`, and project-owned `.ai/integrations/`; read old and staged integration contracts when present;
3. inspect Git status and identify a recoverable baseline;
4. inspect `AGENTS.md`, `CLAUDE.md`, `.codex/`, `.agents/`, and `.claude/`;
5. inventory recognized legacy Forge IDs, manifest-declared new IDs, unlisted project files, manual changes, and same-ID collisions;
6. hash every protected project path before proposing changes;
7. without invoking MCP, API, CLI, or other connectors, classify each integration definition/state file as `absent`, `current_supported`, `older_migratable`, `malformed`, `unsupported_future`, `custom_profile`, or `ownership_collision`.

Absence of `.ai/integrations/` is the clean Forge baseline. It adds no migration step, preflight, file, or blocker. A malformed, future-version, custom, or offline integration blocks only its consumers; only an ownership/path collision or repository-safety violation blocks the framework migration itself.

For upgrades to v4 or later, also inspect:

- whether `.ai/project.yaml` has approved `quality.profiles`, Task-scoped command catalogs, Epic-wide commands, and selection rules;
- whether planned, active, or paused Epic plans contain requirement coverage, quality profiles, an Epic Verification Plan, and appropriate evidence;
- whether any existing `execution/planned/` directory maps to exactly one `PLANNED + READY` Backlog Epic and contains only approved `TODO` definitions;
- whether TASK files contain affected surfaces, risk flags, review focus, Verification Plans, Review Packets, and structured review evidence;
- whether an Epic already in `FUZZING` or `AWAITING EPIC ACCEPTANCE` has a current passing Epic Validation result on the same aggregate fingerprint.

A legacy project may be without `.ai/framework.lock`. In that case use the old bundle, known legacy IDs, content comparison, Git history, and explicit user decisions as evidence. Do not infer permission to delete an ambiguous file.

## Protected Project State

Treat all paths outside the approved framework and adapter allowlist as read-only. Never modify canonical or product state during migration, including:

- `SPEC.md`;
- `ARCHITECTURE.md`;
- `BACKLOG.md`;
- `DECISIONS.md`;
- `decisions/`;
- `execution/`;
- project source code, tests, data, and unrelated configuration.
- `.ai/integrations/`, project-owned integration consumers, and connector configuration.

Report a canonical schema difference as a compatibility finding. Do not edit, rename, reformat, or migrate canonical content in this workflow.

Framework migration and integration-schema migration are separate approvals and transactions. Preserve every integration definition, unknown profile, state file, and custom consumer byte-for-byte while replacing the framework bundle. Do not downgrade, normalize, or silently rewrite an unsupported or malformed file.

A pre-v4 planned, active, or paused plan is not silently upgraded or moved. After the framework migration, use `forge-resume-development` and present the exact plan/TASK compatibility diff. Changes to approved Task scope, order, or composition still require Replan; adding or correcting in-scope verification evidence requires an explicit rationale and may not remove or weaken an approved check. A pre-v4 Epic in `FUZZING` or `AWAITING EPIC ACCEPTANCE` cannot continue to Epic Acceptance until current Epic Validation passes under the new contract.

Migration never infers that a `PLANNED` Backlog Epic already has approved Task definitions. It does not create `execution/planned/` from Backlog rows or move active/paused/completed workspaces. Future Plan Approval creates the new planned workspace; an existing project-owned planned directory is preserved and validated as a compatibility finding.

## Root Router Merge

Treat `AGENTS.md` and `CLAUDE.md` as mixed-ownership files.

Preserve project title, overview, project map, confirmed commands, domain constraints, protected directories, and applicable platform guidance. Check preserved statements against canonical state, especially `BACKLOG.md`, and report contradictions without modifying canonical files. Do not preserve legacy Forge lifecycle rules, routing, agent lists, skill lists, or generic process instructions.

Merge preserved project content from both routers and from any legacy `.ai/custom/router-shared.md`, `.ai/custom/codex-router.md`, or `.ai/custom/claude-router.md`, then preview it before storing it as:

```text
.ai/custom/router-shared.md
```

If old routers or overlays contain conflicting project rules, stop for an explicit reconciliation decision. Back up legacy platform-specific overlays and remove them only as part of the exact approved migration scope after their preserved content is present in the shared overlay. Render the final routers from the staged byte-identical templates plus the shared overlay, verify that the outputs are byte-identical, and show their complete diff before replacement.

## Local Adapter Update

Install no global agent or skill. Manage only IDs declared by the staged manifest at:

```text
.codex/agents/
.agents/skills/
.claude/agents/
.claude/skills/
.claude/forge/codex-role-runner.mjs
```

Keep all nine generated Claude agents. Copy the managed launcher and preferred-route metadata, but do not install `codex-plugin-cc` 1.0.6+ or run Codex authentication during migration. The launcher is optional: unavailable preflight selects the existing native Claude `epic-planner` or `reviewer`; a Codex task that has already started and fails remains blocked. Roll back by removing the managed launcher and preferred-route metadata through adapter sync; retain the native agents.

Remove or replace recognized legacy Forge entries, install the complete staged Forge set, and preserve unlisted project-owned entries. Preserve `.codex/config.toml`, Claude settings, commands, hooks, and other adjacent platform configuration. Stop on a same-ID collision until the user chooses the exact replacement.

## Preview and Approval

Show one complete migration preview containing:

- old and new framework versions and the rollback source;
- every framework replacement and obsolete recognized Forge path;
- extracted shared router overlay and byte-identical final router diffs;
- adapter additions, replacements, preserved files, and collisions;
- protected-path hashes and canonical schema findings;
- `.ai/project.yaml` values that must be confirmed when absent;
- v4 quality-profile, verification-plan, Review-Packet, `VALIDATING`, and Epic Validation compatibility findings;
- exact paths that will be backed up.
- the offline integration compatibility matrix, including the clean absent case, isolated consumer blockers, ownership collisions, and any separately available schema migrations.

Request explicit approval for this exact scope. Approval of migration never authorizes canonical edits, product changes, commits, or pushes.

## Apply, Validate, and Roll Back

After approval:

1. create a temporary recoverable backup of the active `.ai/`, root routers, affected adapter files, existing lock, and any project-owned integration paths that the staged operation references;
2. build staged candidate outputs without changing active targets;
3. compose the new `.ai/` from the staged release plus approved `.ai/project.yaml` and `.ai/custom/` project state while preserving optional `.ai/integrations/` and project-owned consumers byte-for-byte; add missing quality configuration only from explicit user decisions and confirmed repository or CI evidence;
4. replace recognized Forge adapter IDs while preserving unlisted files;
5. replace the active bundle and both byte-identical routers as one logical operation;
6. run `forge-check-framework` against the candidate result;
7. re-hash protected paths and fail on any unauthorized difference; validate integration files structurally but do not include their contents in managed-output lock hashes;
8. create or update `.ai/framework.lock` only after every validation passes;
9. remove `.ai-next/` only after success and keep the backup until the user acknowledges the result.

On any framework-migration failure, perform rollback: restore the old `.ai/`, routers, adapters, lock, and exact integration bytes; verify protected hashes again; report the failed stage. Create no migration report Markdown file and require no framework CLI.

## Optional Integration-Schema Migration

After a compatible framework upgrade, an `older_migratable` integration may be migrated through a separate gate:

1. show the exact definition, state, Backlog source-field, plan coverage, and TASK frontmatter diff;
2. identify the supported source/target schema versions and every affected consumer;
3. create a recoverable pre-migration copy outside the replacement targets;
4. request explicit approval for only this project-owned migration;
5. stage all related files, validate schemas, unique identities, consumer compatibility, and bidirectional work-source references offline;
6. atomically replace only the approved integration and relationship files;
7. on failure, restore the complete pre-migration representation without rolling back an otherwise valid framework install.

Framework rollback never deletes project-owned integrations. Before re-enabling an affected consumer, select the newest representation supported by the restored framework or report an explicit compatibility blocker. External identities and canonical Epic, Bug, and Task records are never deleted as rollback cleanup.
