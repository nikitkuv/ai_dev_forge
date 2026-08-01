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
2. read the optional old `.ai/framework.lock`, `.ai/project.yaml`, and `.ai/custom/`;
3. inspect Git status and identify a recoverable baseline;
4. inspect `AGENTS.md`, `CLAUDE.md`, `.codex/`, `.agents/`, and `.claude/`;
5. inventory recognized legacy Forge IDs, manifest-declared new IDs, unlisted project files, manual changes, and same-ID collisions;
6. hash every protected project path before proposing changes.

A legacy project may be without `.ai/framework.lock`. In that case use the old bundle, known legacy IDs, content comparison, Git history, and explicit user decisions as evidence. Do not infer permission to delete an ambiguous file.

## Protected Project State

Treat all paths outside the approved framework and adapter allowlist as read-only. Never modify canonical or product state during migration, including:

- `SPEC.md`;
- `ARCHITECTURE.md`;
- `BACKLOG.md`;
- `DECISIONS.md`;
- `decisions/`;
- `execution/`;
- project documents such as `WORKFLOW.md`;
- project source code, tests, data, and unrelated configuration.

Report a canonical schema difference as a compatibility finding. Do not edit, rename, reformat, or migrate canonical content in this workflow.

## Root Router Merge

Treat `AGENTS.md` and `CLAUDE.md` as mixed-ownership files.

Preserve project title, overview, project map, confirmed commands, domain constraints, protected directories, and platform-specific guidance. Do not preserve legacy Forge lifecycle rules, routing, agent lists, skill lists, or generic process instructions.

Preview extracted project content before storing it as:

```text
.ai/custom/router-shared.md
.ai/custom/codex-router.md
.ai/custom/claude-router.md
```

Render the final routers from the staged templates plus these overlays and show their complete diff before replacement.

## Local Adapter Update

Install no global agent or skill. Manage only IDs declared by the staged manifest at:

```text
.codex/agents/
.agents/skills/
.claude/agents/
.claude/skills/
```

Remove or replace recognized legacy Forge entries, install the complete staged Forge set, and preserve unlisted project-owned entries. Preserve `.codex/config.toml`, Claude settings, commands, hooks, and other adjacent platform configuration. Stop on a same-ID collision until the user chooses the exact replacement.

## Preview and Approval

Show one complete migration preview containing:

- old and new framework versions and the rollback source;
- every framework replacement and obsolete recognized Forge path;
- extracted router overlays and final router diffs;
- adapter additions, replacements, preserved files, and collisions;
- protected-path hashes and canonical schema findings;
- `.ai/project.yaml` values that must be confirmed when absent;
- exact paths that will be backed up.

Request explicit approval for this exact scope. Approval of migration never authorizes canonical edits, product changes, commits, or pushes.

## Apply, Validate, and Roll Back

After approval:

1. create a temporary recoverable backup of the active `.ai/`, root routers, affected adapter files, and existing lock;
2. build staged candidate outputs without changing active targets;
3. compose the new `.ai/` from the staged release plus approved `.ai/project.yaml` and `.ai/custom/` project state;
4. replace recognized Forge adapter IDs while preserving unlisted files;
5. replace the active bundle and both routers as one logical operation;
6. run `forge-check-framework` against the candidate result;
7. re-hash protected paths and fail on any difference;
8. create or update `.ai/framework.lock` only after every validation passes;
9. remove `.ai-next/` only after success and keep the backup until the user acknowledges the result.

On any failure, perform rollback: restore the old `.ai/`, routers, adapters, and lock; verify protected hashes again; report the failed stage. Create no migration report Markdown file and require no framework CLI.

