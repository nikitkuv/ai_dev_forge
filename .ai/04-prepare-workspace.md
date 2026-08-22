# Bootstrap Step 04 — Prepare a Planned Epic Workspace

## Purpose

Prepare one user-approved Epic plan and its initial TASK files under `execution/planned/`. Optionally activate that approved workspace through the separate explicit **Epic Start gate**.

Use:

- approved `SPEC.md`, `ARCHITECTURE.md`, and `BACKLOG.md`;
- relevant accepted ADRs;
- `.ai/templates/plan.md`;
- `.ai/templates/TASK.md`;
- `.ai/CONVENTIONS.md`;
- `.ai/framework/contracts.yaml`.
- optional Backlog `Sources` and `.ai/integrations/work-items.yaml` entries for the selected Epic.

This step prepares execution state only. Plan Approval does not change the Epic lifecycle status. Epic Start moves one approved planned workspace to active state. Neither action modifies product code, implements a Task, or starts the first Task.

## Select and Validate the Epic

The user selects the Epic to prepare. The agent may recommend the first Epic in user-defined Backlog order, but must not select or reorder it silently.

Before planning, verify:

- the Epic exists in `BACKLOG.md`;
- its lifecycle status is `PLANNED`;
- its readiness is `READY`;
- its requirements and boundaries are approved;
- dependencies and blockers are explicitly declared, even when not yet satisfied;
- no workspace for the same Epic already exists under `execution/planned/`, `active/`, `paused/`, or `completed/` unless this invocation is revising its existing planned workspace through Replan;
- no conflicting planned directory name or global Task ID exists.

An `OUTLINE` Epic or an Epic with unresolved requirements or boundaries cannot receive a detailed workspace. Declared unsatisfied dependencies, `Blocked by` entries, or another active-work Epic do not prevent planning, but they must remain visible and will block Epic Start. Never reorder or bypass them automatically.

## Prepare the Proposed Plan

Invoke the strong read-only `epic-planner` with the approved canonical documents, selected Epic, relevant repository and CI evidence, project quality configuration, framework contracts, conventions, and templates. Require `.ai/project.yaml` to contain one valid `role_execution.mode`: `claude_with_codex` requires Claude Code and the managed Codex plugin route, `codex_with_claude` requires Codex and the managed headless Claude Code route, and `native_subagents` uses the active platform's generated planner without external preflight. Active-orchestrator mismatch, unavailable selected prerequisites, or any started external-run failure blocks planning; there is no fallback. Every route receives the complete neutral contract and identical evidence. The selected executor returns a proposal only; it does not write files, approve definitions, activate the Epic, or contact the user.

The orchestrator must independently check the proposal against canonical sources and repository evidence, resolve blockers with the user, and remain responsible for the final displayed plan. Build the proposal with:

1. define the Epic objective and expected outcome;
2. identify dependencies, risks, and implementation strategy;
3. create an ordered Task sequence with explicit `Depends on` relationships;
4. define Epic acceptance criteria;
5. map requirements to planned Task and Epic-level evidence;
6. select applicable quality profiles and risk flags;
7. define Task-focused and affected verification without a mandatory full suite;
8. define Epic-wide full regression, project-wide checks, critical paths, profile gates, fuzzing, and user-validation gates.
9. when the Epic has work-source references, map every source slice to proposed TASK coverage and identify deferred, duplicate, or unresolved scope.

Use the plan template without adding Task lifecycle state or a duplicated execution-status section.

## Prepare the Initial TASK Definitions

Create one proposed TASK definition per planned unit of work.

For every TASK:

- allocate the next project-global `TASK-NNN`; numbering never restarts per Epic and retired IDs are not reused;
- define one clear outcome, context, scope, out of scope, and constraints;
- add objectively verifiable acceptance criteria;
- record affected components and contracts, risk level and flags, and review focus;
- add required Task-specific, affected-component, and scoped quality checks;
- defer the full project suite and unscoped project-wide checks to Epic Validation;
- add reproducible manual verification;
- link requirements, architecture sections, ADRs, defects, and the Epic plan where applicable;
- copy only the provider-neutral work-source keys covered by this TASK into `external_sources`;
- record dependencies through the ordered plan;
- initialize lifecycle `status: TODO`;
- keep `definition_status: draft` until the user approves the complete plan.

The planner's proposed verification selection is not self-approving. The reviewer must later challenge its coverage against the actual implementation diff, and the tester must report a stale or incomplete selection instead of silently expanding to the full suite.

Do not run a mandatory atomicity classifier. Split or reshape work only when the user requests it or when actual planning or execution reveals a concrete need.

## Plan Review and Plan Approval Gate

Before writing planned execution state:

1. show the proposed plan and all TASK definitions;
2. show the exact `execution/planned/` paths that Plan Approval will create;
3. resolve user-requested corrections while definitions remain `draft`;
4. request explicit approval of the plan and TASK definitions;
5. state that Plan Approval leaves the Epic `PLANNED`, starts no Task, and does not imply Epic Start.

After explicit Plan Approval:

1. allocate and verify all final global IDs;
2. create `execution/planned/EPIC-NNN-<short-name>/plan.md` and `tasks/`;
3. write `plan.md` with `document_status: approved` and approval metadata;
4. write every TASK with `definition_status: approved` and `status: TODO`;
5. leave the Backlog Epic status `PLANNED` and preserve its priority, order, dependencies and blockers;
6. when external sources apply, update TASK references, the plan coverage matrix, and `.ai/integrations/work-items.yaml` reverse mappings together;
7. validate links, IDs, dependencies, source coverage, directory uniqueness and the absence of product-code changes.

Treat planned-workspace creation as one logical write. On failure, remove only the partial newly created workspace and preserve the prior Backlog and other planned/active workspaces. Approval of a TASK definition is not authorization to implement it.

Multiple planned workspaces may coexist. Backlog priority and row order, not directory order or creation time, determine the queue.

## Epic Start Gate

Epic Start may follow immediately or occur in a later session. Before requesting it, verify:

- the Epic is still `PLANNED + READY`;
- its approved workspace exists only under `execution/planned/` and still matches the Backlog ID and stable short name;
- plan and TASK definitions are approved and internally consistent;
- every dependency is now satisfied;
- `Blocked by` is empty;
- no Epic occupies `ACTIVE`, `VALIDATING`, `FUZZING`, or `AWAITING EPIC ACCEPTANCE`;
- no conflicting directory exists under `execution/active/`.

If any activation condition fails, keep the workspace in `execution/planned/`, report the exact blocker, and do not change status or directory state.

Show the exact Backlog status change and planned-to-active directory move, then request explicit **Epic Start** authorization. Plan Approval and Epic Start remain separate decisions; one user message may grant both only when it clearly states both.

After Epic Start authorization:

1. atomically move the approved workspace:

```text
execution/
├── planned/
│   └── EPIC-NNN-<short-name>/   # before Epic Start
├── active/
│   └── EPIC-NNN-<short-name>/   # after Epic Start
├── paused/
└── completed/
```

2. update only the selected Epic in `BACKLOG.md` from `PLANNED` to `ACTIVE`;
3. verify Backlog state, directory state, links, IDs, dependencies and unchanged `TODO` Task statuses together.

Treat the Backlog update and planned-to-active move as one logical transition. If either write or validation fails, restore the Epic to `PLANNED` and its complete workspace to `execution/planned/`.

The first TASK remains TODO after workspace creation. Starting it requires the separate Task Start gate.

## Replan Gate

After the plan is approved, any change to Task scope, order, composition, or external-source coverage requires the **Replan gate**, whether the workspace is planned, active, or paused:

1. explain the reason;
2. show the exact plan and TASK diff;
3. request explicit user confirmation;
4. only then add, cancel, split, merge, reorder, or rescope TASK definitions.

For work-source changes, re-read versioned source records before applying the diff. Atomically update TASK `external_sources`, the plan coverage matrix, and reverse provenance. A partial or stale update leaves all three unchanged.

Typo and link corrections do not require Replan. Replan approval does not start any new or changed TASK; each still requires its own Task Start gate.

## Validation

Before reporting completion, verify:

- every directory under `execution/planned/` belongs to exactly one `PLANNED + READY` Backlog Epic;
- each planned directory contains one approved plan and the exact approved `TODO` TASK definitions listed by that plan;
- multiple planned directories have no implied order and their Epics remain ordered only in `BACKLOG.md`;
- if Epic Start occurred, exactly one Epic is `ACTIVE`, its directory is the only directory under `execution/active/`, and no directory for that Epic remains under `execution/planned/`;
- every directory name matches its Backlog Epic ID and stable short name;
- the plan is approved and contains the same ordered Tasks that exist in `tasks/`;
- all Epic and Task IDs are globally allocated and unique;
- all TASK definitions are approved;
- all TASK lifecycle values remain `TODO`;
- Task dependencies reference existing IDs and contain no cycle;
- requirement, architecture, ADR, defect, plan, and Task links resolve;
- Backlog source keys, TASK `external_sources`, plan coverage, and work-item reverse mappings agree when `work_source` is configured;
- no product code, hooks, MCP configuration, or unrelated documentation changed.

## Outputs

- `execution/planned/EPIC-NNN-<short-name>/plan.md` after Plan Approval;
- `execution/planned/EPIC-NNN-<short-name>/tasks/TASK-NNN-<short-name>.md` after Plan Approval;
- optional updated `BACKLOG.md` and moved `execution/active/EPIC-NNN-<short-name>/` after Epic Start;
- structural `execution/planned/`, `active/`, `paused/`, and `completed/` directories when absent.

If only Plan Approval occurred, report the queued planned workspace and the exact blockers or pending Epic Start decision. If Epic Start occurred, report the active workspace. Never continue to implementation automatically; the first Task still requires a separate Task Start confirmation.
