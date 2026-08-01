# AI Development Forge Conventions

## Purpose

This document is the human-readable companion to the machine-readable framework contracts. `.ai/framework/contracts.yaml` is the single source of truth for lifecycle enums, transitions, gates, fuzzing outcomes, and invariants. Do not duplicate or locally redefine lifecycle status lists.

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
|- execution/{active,paused,completed}/
|- .ai/{project.yaml,framework.lock,custom/}
|- .codex/
|- .claude/
`- .agents/
```

`execution/active`, `execution/paused`, and `execution/completed` are structural representations of Epic status. The orchestrator updates `BACKLOG.md` and moves the matching Epic directory together; a mismatch is an invalid state.

## Ownership and generated files

Ownership is defined by `.ai/framework/manifest.yaml`.

- Framework-owned: bootstrap control documents, `CONVENTIONS.md`, `.ai/templates/`, and `.ai/framework/`.
- Project-owned state and customizations: `.ai/project.yaml`, `.ai/framework.lock`, `.ai/custom/`, canonical documents, decisions, execution state, and project-specific hooks or MCP.
- Generated adapter outputs: `AGENTS.md`, `CLAUDE.md`, and manifest-declared Forge entries under `.codex/`, `.claude/`, and `.agents/`. Unlisted entries remain project-owned.

Generated Forge adapter entries are derived files, not project-owned files. Do not edit them manually; put project-specific router additions in `.ai/custom/`. Adapter synchronization detects manual edits, shows the regeneration diff, and requires explicit confirmation before overwriting a managed collision. The framework provides no default hooks, MCP server, CLI, or external lifecycle layer.

Forge lifecycle behavior comes only from bundled Forge skills, `.ai/framework/contracts.yaml`, and generated agent definitions. External process skills may not introduce additional lifecycle gates, canonical or report artifacts, status transitions, agent routing, or Git actions.

## Language rules

Framework control text, technical identifiers, statuses, paths, and commands are English. Canonical project documents (`README`, `SPEC`, `ARCHITECTURE`, `BACKLOG`, `DECISIONS`, ADRs, plans, and Tasks) use the user communication language recorded in `.ai/project.yaml`.

## One source of truth

Each kind of information has one canonical owner:

- Product behavior: `SPEC.md`; architecture: `ARCHITECTURE.md`.
- Epic priority, readiness, and lifecycle status, plus bug lifecycle state: `BACKLOG.md`; Epic strategy, Task order, Epic fuzzing summary, and Epic user-validation summary: its `plan.md`.
- Task scope, acceptance criteria, lifecycle state, and implementation/review/testing/user-validation summaries: the Task file.
- Architectural decision content: its ADR; ADR navigation: `DECISIONS.md`.
- File history: Git.

Do not create separate progress, report, checkpoint, user-validation, security, research, or fuzzing Markdown files. Keep document approval status separate from lifecycle status. If source documents disagree, report the inconsistency instead of silently reconciling it.
