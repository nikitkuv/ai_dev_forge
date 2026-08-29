# AI Development Forge Conventions

## Purpose

This document is the human-readable companion to the machine-readable framework contracts. `.ai/framework/contracts.yaml` is the single source of truth for lifecycle enums, transitions, gates, Task/Epic quality policy, quality profiles, Epic Validation and fuzzing outcomes, and invariants. Do not duplicate or locally redefine lifecycle status lists.

## Naming and global identifiers

Identifiers are globally unique within a project. Epic, Task, Bug, and Decision IDs are zero-padded to three digits; independent mutation-run IDs are zero-padded to at least four digits. Allocate each entity type independently by taking its maximum existing ID and adding one; do not fill gaps. Task numbering is project-global and never restarts for an Epic. Never reuse an ID that was deleted, cancelled, skipped, or otherwise retired:

| Entity | Identifier | Canonical location |
| --- | --- | --- |
| Epic | `EPIC-001` | `execution/<state>/EPIC-001-<short-name>/` |
| Task | `TASK-001` | `execution/<state>/EPIC-001-<short-name>/tasks/TASK-001-<short-name>.md` |
| Bug | `BUG-001` | `BACKLOG.md` |
| Decision | `ADR-001` | `decisions/ADR-001-<short-name>.md` |
| Mutation run | `MUT-0001` | `quality/mutation-testing/runs/MUT-0001.yaml` |

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
|- quality/mutation-testing/         # optional, project-owned, created on first requested run
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
- Independent mutation history under `quality/mutation-testing/` is optional project-owned state. Bootstrap and adapter synchronization do not create or overwrite it.
- Generated adapter outputs: `AGENTS.md`, `CLAUDE.md`, and manifest-declared Forge entries under `.codex/`, `.claude/`, and `.agents/`. Unlisted entries remain project-owned.

Generated Forge adapter entries are derived files, not project-owned files. `AGENTS.md` is the single full router; `CLAUDE.md` contains only `@AGENTS.md`. Do not edit them manually; put project-specific router additions only in `.ai/custom/router-shared.md`. Adapter synchronization detects manual edits, shows the regeneration diff, and requires explicit confirmation before overwriting a managed collision. The framework provides no default hooks, MCP server, CLI, or external lifecycle layer.

## Project-local integrations

`.ai/integrations/` is an optional project-owned registry. A clean Forge project does not contain it and runs bootstrap, migration, adapter synchronization, validation, and the complete development lifecycle without connector discovery or integration-specific blockers.

Definitions use `.ai/framework/integrations/contracts.yaml`. They describe provider-neutral capability profiles, semantic operations, resource scope, access/data policy, allowed consumer skills, and platform-local bindings. Registration never grants implicit tool authority: a selected framework-owned or project-owned skill must explicitly consume a compatible profile, and effective access is the intersection of both contracts. Credentials and raw MCP/API/CLI configuration stay outside the registry.

`work_source` is one optional profile. Only it uses `.ai/integrations/work-items.yaml`, Backlog `Sources`, TASK `external_sources`, and an Epic source-coverage matrix. Knowledge, data, analysis, and custom profiles do not receive synthetic Epic or Task links.

Framework upgrades preserve unknown profiles, definitions, state, and project-owned consumers. Unsupported or malformed integrations block only their consumers unless they collide with a framework-owned path or violate repository safety. Local integration content is not a managed adapter input and its normal changes are not framework drift.

Forge lifecycle behavior comes only from bundled Forge skills, `.ai/framework/contracts.yaml`, and generated agent definitions. External process skills may not introduce additional lifecycle gates, canonical or report artifacts, status transitions, agent routing, or Git actions.

## Independent mutation testing

`quality/mutation-testing/registry.yaml` indexes monotonically allocated `MUT-NNNN` records under `quality/mutation-testing/runs/`. These records own mutation scope, exact fingerprints, backend commands and versions, budgets, baseline evidence, normalized metrics, optional strong-model analysis, artifact retention, and informational disposition references.

Mutation testing is invoked only by an explicit user request and is independent of Backlog, Epic, TASK, review, testing, validation, fuzzing, acceptance, and commit state. A run or finding never changes lifecycle status, satisfies a quality gate, invalidates development evidence, or creates remediation automatically. The bare workflow is metrics-only; strong analysis requires separate explicit authorization and current candidates. Tool installation or configuration is a separate repository change.

## Test integrity

Tests are executable evidence of approved behavior, not a description of the current implementation. Derive their oracles from acceptance criteria, public contracts, domain invariants, architecture and independently calculated expectations before using production output. Never copy current output into an expectation, reproduce the production algorithm inside the test, assert private call structure as a substitute for behavior, or weaken an assertion merely because the implementation fails it.

Within the approved Task scope, cover every acceptance criterion and affected risk with the strongest practical evidence: successful behavior, boundaries, invalid input, failure and recovery paths, relevant state transitions and side effects, and regression cases. Prefer the lowest stable public boundary that executes real production code. Mock only true external or nondeterministic boundaries; do not mock the subject under test or the decision logic being verified. Assertions must discriminate correct behavior from plausible wrong implementations, not merely prove that code ran, returned a value, or matched a self-generated snapshot.

A production behavior change does not automatically authorize a test change. Every changed test, fixture, snapshot, golden file, baseline or expected metric must be classified as a behavior-contract change, correction of a demonstrably defective test, or coverage extension. Record the independent source of the new expectation and obtain orchestrator disposition for any removed case, reduced assertion strength, broader tolerance, new skip, or increased mocking. When the contract has not changed, fix production code rather than adapting the test to current behavior.

## Language rules

Framework control text, technical identifiers, statuses, paths, and commands are English. Canonical project documents (`README`, `SPEC`, `ARCHITECTURE`, `BACKLOG`, `DECISIONS`, ADRs, plans, and Tasks) use the user communication language recorded in `.ai/project.yaml`.

## One source of truth

Each kind of information has one canonical owner:

- Product behavior: `SPEC.md`; architecture: `ARCHITECTURE.md`.
- Epic priority, readiness, and lifecycle status, plus bug lifecycle state: `BACKLOG.md`; Epic strategy, Task order, requirement coverage, quality profiles, Epic Verification Plan, Epic Fuzzing Plan, Epic Validation, fuzzing outcome, and Epic user-validation summaries: its `plan.md`.
- Task scope, acceptance criteria, affected surface, risk flags, approved delivery track and rationale, review focus, Verification Plan including fuzzing impact and Task smoke, lifecycle state, and implementation/fast-assurance-or-standard-review-testing/user-validation summaries: the Task file.
- Architectural decision content: its ADR; ADR navigation: `DECISIONS.md`.
- File history: Git.
- Local integration definitions and reverse source mappings: optional `.ai/integrations/`; Forge lifecycle and acceptance remain owned by Backlog, plans, and TASK files.
- Independent mutation-test history: optional `quality/mutation-testing/`; it may reference later approved work but never owns or changes that work's state.

Do not create separate progress, report, checkpoint, user-validation, security, research, or fuzzing Markdown files. Keep document approval status separate from lifecycle status. If source documents disagree, report the inconsistency instead of silently reconciling it.

Generated root `AGENTS.md` contains the Common Engineering Prohibitions once, and `CLAUDE.md` imports them through `@AGENTS.md`. Project overlays may add stricter rules but may not remove or weaken those framework prohibitions.
