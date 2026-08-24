# AI Development Forge Conventions

## Purpose

This document is the human-readable companion to the machine-readable framework contracts. `.ai/framework/contracts.yaml` is the single source of truth for lifecycle enums, transitions, gates, Task/Epic quality policy, quality profiles, Epic Validation and fuzzing outcomes, and invariants. Do not duplicate or locally redefine lifecycle status lists.

## Naming and global identifiers

Identifiers are globally unique within a project and zero-padded to three digits. Allocate each entity type independently by taking its maximum existing ID and adding one; do not fill gaps. Task numbering is project-global and never restarts for an Epic. Never reuse an ID that was deleted, cancelled, skipped, or otherwise retired:

| Entity | Identifier | Canonical location |
| --- | --- | --- |
| Epic | `EPIC-001` | `execution/<state>/EPIC-001-<short-name>/` |
| Task | `TASK-001` | `execution/<state>/EPIC-001-<short-name>/tasks/TASK-001-<short-name>.md` |
| Bug | `BUG-001` | `BACKLOG.md` |
| Decision | `ADR-001` | `decisions/ADR-001-<short-name>.md` |

`<short-name>` is stable, lowercase kebab-case, and one to four words. An Epic folder name must match its Epic name in `BACKLOG.md`; each Task belongs to exactly one Epic.

## Canonical project paths

```text
project/
|- README.md
|- AGENTS.md
|- CLAUDE.md
|- SPEC.md
|- ARCHITECTURE.md
|- BACKLOG.md
|- DECISIONS.md
|- decisions/
|- execution/{planned,active,paused,completed}/
|- .ai/{project.yaml,framework.lock,custom/}
|- .ai/integrations/                 # optional, project-owned, absent by default
|- .codex/
|- .claude/
`- .agents/
```

`execution/planned/EPIC-*` stores approved detailed plans and `TODO` TASK definitions for `PLANNED + READY` Epics that have not passed Epic Start. Multiple planned workspaces may coexist; their directory order has no priority meaning because Backlog row order remains authoritative.

`execution/active`, `execution/paused`, and `execution/completed` are structural representations of non-planned Epic status. Epic Start atomically moves one approved directory from `execution/planned/` to `execution/active/` and changes only that Backlog Epic from `PLANNED` to `ACTIVE`. The same Epic may exist in at most one execution state directory; a mismatch is invalid.

## Ownership and generated files

Ownership is defined by `.ai/framework/manifest.yaml`.

- Framework-owned: bootstrap control documents, `CONVENTIONS.md`, `.ai/templates/`, and `.ai/framework/`.
- Project-owned state and customizations: `.ai/project.yaml`, `.ai/framework.lock`, `.ai/custom/`, optional `.ai/integrations/`, canonical documents, decisions, execution state, and project-specific hooks, MCP, APIs, or CLIs.
- Generated adapter outputs: `AGENTS.md`, `CLAUDE.md`, and manifest-declared Forge entries under `.codex/`, `.claude/`, and `.agents/`. Unlisted entries remain project-owned.

Generated Forge adapter entries are derived files, not project-owned files. `AGENTS.md` and `CLAUDE.md` are byte-identical. Do not edit them manually; put project-specific router additions only in `.ai/custom/router-shared.md`. Adapter synchronization detects manual edits, shows the regeneration diff, and requires explicit confirmation before overwriting a managed collision. The framework provides no default hooks, MCP server, CLI, or external lifecycle layer.

## Project-local integrations

`.ai/integrations/` is an optional project-owned registry. A clean Forge project does not contain it and runs bootstrap, migration, adapter synchronization, validation, and the complete development lifecycle without connector discovery or integration-specific blockers.

Definitions use `.ai/framework/integrations/contracts.yaml`. They describe provider-neutral capability profiles, semantic operations, resource scope, access/data policy, allowed consumer skills, and platform-local bindings. Registration never grants implicit tool authority: a selected framework-owned or project-owned skill must explicitly consume a compatible profile, and effective access is the intersection of both contracts. Credentials and raw MCP/API/CLI configuration stay outside the registry.

`work_source` is one optional profile. Only it uses `.ai/integrations/work-items.yaml`, Backlog `Sources`, TASK `external_sources`, and an Epic source-coverage matrix. Knowledge, data, analysis, and custom profiles do not receive synthetic Epic or Task links.

Framework upgrades preserve unknown profiles, definitions, state, and project-owned consumers. Unsupported or malformed integrations block only their consumers unless they collide with a framework-owned path or violate repository safety. Local integration content is not a managed adapter input and its normal changes are not framework drift.

Forge lifecycle behavior comes only from bundled Forge skills, `.ai/framework/contracts.yaml`, and generated agent definitions. External process skills may not introduce additional lifecycle gates, canonical or report artifacts, status transitions, agent routing, or Git actions.

## Language rules

Framework control text, technical identifiers, statuses, paths, and commands are English. Canonical project documents (`README`, `SPEC`, `ARCHITECTURE`, `BACKLOG`, `DECISIONS`, ADRs, plans, and Tasks) use the user communication language recorded in `.ai/project.yaml`.

## One source of truth

Each kind of information has one canonical owner:

- Product behavior: `SPEC.md`; architecture: `ARCHITECTURE.md`.
- Epic priority, readiness, and lifecycle status, plus bug lifecycle state: `BACKLOG.md`; Epic strategy, Task order, requirement coverage, quality profiles, Epic Verification Plan, Epic Fuzzing Plan, Epic Validation, fuzzing outcome, and Epic user-validation summaries: its `plan.md`.
- Task scope, acceptance criteria, affected surface, risk flags, review focus, Verification Plan including fuzzing impact and Task smoke, lifecycle state, and implementation/structured-review/testing/user-validation summaries: the Task file.
- Architectural decision content: its ADR; ADR navigation: `DECISIONS.md`.
- File history: Git.
- Local integration definitions and reverse source mappings: optional `.ai/integrations/`; Forge lifecycle and acceptance remain owned by Backlog, plans, and TASK files.

Do not create separate progress, report, checkpoint, user-validation, security, research, or fuzzing Markdown files. Keep document approval status separate from lifecycle status. If source documents disagree, report the inconsistency instead of silently reconciling it.

Generated root `AGENTS.md` and `CLAUDE.md` contain byte-identical Common Engineering Prohibitions. Project overlays may add stricter rules but may not remove or weaken those framework prohibitions.
