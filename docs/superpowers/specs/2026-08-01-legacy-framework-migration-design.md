# Legacy Framework Migration Design

## Goal

Add a dedicated, rollback-safe migration path for repositories already initialized with an older AI Development Forge release, including legacy repositories without `.ai/framework.lock`.

Migration must update Forge itself and its local platform adapters without changing project-owned product or execution state.

## Entry Points and Distribution

The framework repository keeps exactly one release source: `.ai/`.

- Fresh initialization or first adoption copies `.ai/` to the consumer repository and starts from `.ai/BOOTSTRAP.md`.
- Framework upgrade copies the same `.ai/` to `.ai-next/` in the consumer repository and starts from `.ai-next/MIGRATE.md`.

There is no committed `.ai-migration/` copy and no second maintained framework payload.

The root `MIGRATION.md` is the only user-facing migration guide. It documents both a local-copy workflow and commands that fetch only `.ai/` from the GitHub `main` branch with Git sparse checkout and place it at `.ai-next/`.

## Protected Project State

Migration uses an allowlist of writable framework and adapter paths. Everything else is project-owned and remains unchanged.

The protected set explicitly includes:

- `SPEC.md`;
- `ARCHITECTURE.md`;
- `BACKLOG.md`;
- `DECISIONS.md`;
- `decisions/`;
- `execution/`;
- project-specific documents such as `WORKFLOW.md`;
- product source code, tests, data, and unrelated configuration.

The migration records pre-migration hashes for canonical and execution paths and verifies them after applying the update. Any unexpected change fails migration and triggers rollback.

Canonical schema differences are reported as compatibility findings. They are never applied as part of framework migration.

## Migration Flow

1. Keep the old `.ai/` active and copy the new release to `.ai-next/`.
2. Invoke `.ai-next/MIGRATE.md` explicitly.
3. Inspect the old and new bundles, Git state, routers, local adapters, and protected paths without writing.
4. Classify old Forge outputs, project-owned additions, unknown files, and collisions.
5. Present one complete migration preview and request explicit approval.
6. Back up the old `.ai/`, root routers, and affected adapter files to a temporary recoverable location.
7. Build staged candidates for the new `.ai/`, both root routers, and both platform adapter sets.
8. Replace the old bundle and approved adapter paths as one logical operation.
9. Validate Forge sources, adapter parity, required IDs, router rendering, and protected-path hashes.
10. Create or update `.ai/framework.lock` only after all validation passes.
11. On failure, restore the old bundle, routers, adapters, and lock. On success, remove `.ai-next/` and retain the temporary backup until the user acknowledges the result.

For a legacy repository without a lock, no obsolete or ambiguous file is deleted solely by inference. The old bundle, known legacy IDs, content comparison, Git history, and explicit user decisions provide the migration baseline.

## Root Router Merge

`AGENTS.md` and `CLAUDE.md` are mixed-ownership files.

Migration extracts and preserves project-specific content such as:

- project title and overview;
- project map and authoritative project documents;
- confirmed setup, run, and test commands;
- domain-specific constraints and protected directories;
- platform-specific project guidance.

Legacy Forge lifecycle, routing, agent lists, skill lists, and generic process rules are not preserved. They are replaced by the new router templates.

Preserved content becomes durable project-owned overlay input under `.ai/custom/`:

- `.ai/custom/router-shared.md` for shared project context;
- `.ai/custom/codex-router.md` for Codex-only additions;
- `.ai/custom/claude-router.md` for Claude-only additions.

The migration previews both the extracted overlays and final rendered routers before replacement. Future adapter synchronization renders the new framework routers plus these overlays, so framework sections can be updated without losing project context.

## Local Adapter Synchronization

Forge installs no global agents or skills.

Required local paths are:

- Codex agents: `.codex/agents/*.toml`;
- Codex skills: `.agents/skills/<forge-skill-id>/SKILL.md`;
- Claude agents: `.claude/agents/*.md`;
- Claude skills: `.claude/skills/<forge-skill-id>/SKILL.md`.

Synchronization is ID-based rather than directory-replacement-based:

- remove or replace recognized legacy Forge agents and skills;
- install every agent and skill declared by the new manifest;
- preserve unlisted project-owned agents, skills, platform configuration, hooks, commands, and unknown files;
- never replace `.codex/config.toml`, Claude settings, hooks, or commands as Forge output;
- stop on a same-ID collision unless the user explicitly chooses the replacement.

Validation requires the complete manifest-declared Forge set but permits additional project-owned agents and skills. The previous exact-directory-count rule is removed.

If `.codex/` or `.agents/` does not exist in a legacy project, migration creates the required local subdirectories.

## Ownership and Lock State

The active new `.ai/` consists of the new framework-owned bundle plus preserved or newly created project-owned control state:

- `.ai/project.yaml`;
- `.ai/custom/`;
- `.ai/framework.lock`.

Legacy repositories may not contain any of these files. Migration creates `.ai/project.yaml` only from confirmed language, model mappings, reasoning effort, enabled platforms, and Git policy. It creates the first lock only after successful validation.

The lock records framework source hashes, generated Forge output hashes, exact managed IDs and paths, and ownership data needed for later migrations. It does not claim ownership of unrelated files beside Forge outputs.

## Documentation Ownership

User-facing migration guidance lives only in root `MIGRATION.md`.

Existing migration prose is removed from `README.md`, `RUNBOOK.md`, `FRAMEWORK.md`, `FRAMEWORK_DESIGN.md`, scenarios, and other general documentation. Internal executable migration contracts remain where required:

- `.ai/MIGRATE.md`;
- `forge-migrate-framework`;
- `forge-sync-adapters`;
- manifest ownership metadata;
- adapter-generation and conformance instructions that enforce migration behavior.

## Verification

Repository checks must cover:

- only one committed `.ai/` framework payload exists;
- `.ai/MIGRATE.md` and root `MIGRATION.md` agree on the `.ai-next/` flow;
- legacy migration without a lock never changes protected paths;
- project router content survives regeneration through `.ai/custom/`;
- legacy Forge adapters are removed and new required adapters are installed locally;
- unrelated adapter files and platform configuration survive;
- validation accepts additional project-owned agents and skills;
- failed migration restores the complete pre-migration state;
- all general documentation is free of migration instructions outside `MIGRATION.md`.
