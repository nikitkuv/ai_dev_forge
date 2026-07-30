# Bootstrap Step 04 — Prepare the Active Epic Workspace

## Purpose

Prepare one user-approved Epic plan and its initial TASK files, then activate that Epic through the explicit **Epic Start gate**.

Use:

- approved `SPEC.md`, `ARCHITECTURE.md`, and `BACKLOG.md`;
- relevant accepted ADRs;
- `.ai/templates/plan.md`;
- `.ai/templates/TASK.md`;
- `.ai/CONVENTIONS.md`;
- `.ai/framework/contracts.yaml`.

This step prepares execution state only. It does not modify product code, implement a Task, or start the first Task.

## Select and Validate the Epic

The user selects the Epic to prepare. The agent may recommend the first Epic in user-defined Backlog order, but must not select or reorder it silently.

Before planning, verify:

- the Epic exists in `BACKLOG.md`;
- its lifecycle status is `PLANNED`;
- its readiness is `READY`;
- its requirements and boundaries are approved;
- every dependency is satisfied;
- `Blocked by` is empty;
- no other Epic is `ACTIVE`;
- no conflicting active execution directory exists.

If the Epic is `OUTLINE`, blocked, has unresolved dependencies, or conflicts with another active Epic, stop and explain the exact conflict. Ask the user how to resolve it; do not activate, reorder, or bypass it automatically.

## Prepare the Proposed Plan

Build a proposal from the approved canonical documents and repository evidence:

1. define the Epic objective and expected outcome;
2. identify dependencies, risks, and implementation strategy;
3. create an ordered Task sequence with explicit `Depends on` relationships;
4. define Epic acceptance criteria;
5. define mandatory review, testing, configured quality checks, fuzzing, and user-validation gates.

Use the plan template without adding Task lifecycle state or a duplicated execution-status section.

## Prepare the Initial TASK Definitions

Create one proposed TASK definition per planned unit of work.

For every TASK:

- allocate the next project-global `TASK-NNN`; numbering never restarts per Epic and retired IDs are not reused;
- define one clear outcome, context, scope, out of scope, and constraints;
- add objectively verifiable acceptance criteria;
- add required Task-specific, affected-component, full-suite, and configured quality checks;
- add reproducible manual verification;
- link requirements, architecture sections, ADRs, defects, and the Epic plan where applicable;
- record dependencies through the ordered plan;
- initialize lifecycle `status: TODO`;
- keep `definition_status: draft` until the user approves the complete plan.

Do not run a mandatory atomicity classifier. Split or reshape work only when the user requests it or when actual planning or execution reveals a concrete need.

## Plan Review and Epic Start Gate

Before writing active execution state:

1. show the proposed plan and all TASK definitions;
2. show the exact Backlog and workspace changes that activation will make;
3. resolve user-requested corrections while definitions remain `draft`;
4. request explicit approval of the plan and TASK definitions;
5. request explicit authorization for the **Epic Start gate**.

The user may approve the plan without starting the Epic. Do not create active execution state until Epic Start is explicitly authorized. One message may approve both decisions only when it clearly states both.

After plan approval, generated TASK files use `definition_status: approved`. Approval of a TASK definition is not authorization to implement it.

## Apply the Activation as One State Transition

After both plan approval and Epic Start authorization:

1. allocate and verify all final global IDs;
2. create the workspace:

```text
execution/
├── active/
│   └── EPIC-NNN-<short-name>/
│       ├── plan.md
│       └── tasks/
│           ├── TASK-NNN-<short-name>.md
│           └── ...
├── paused/
└── completed/
```

3. write `plan.md` with `document_status: approved` and approval metadata;
4. write every TASK with `definition_status: approved` and `status: TODO`;
5. update only the selected Epic in `BACKLOG.md` from `PLANNED` to `ACTIVE`;
6. verify Backlog state, directory state, links, IDs, and dependencies together.

Treat the Backlog update and active-directory creation as one logical transition. If any write or validation fails, restore the prior Backlog and workspace state instead of leaving a partial activation.

The first TASK remains TODO after workspace creation. Starting it requires the separate Task Start gate.

## Replan Gate

After the plan is approved, any change to Task scope, order, or composition requires the **Replan gate**:

1. explain the reason;
2. show the exact plan and TASK diff;
3. request explicit user confirmation;
4. only then add, cancel, split, merge, reorder, or rescope TASK definitions.

Typo and link corrections do not require Replan. Replan approval does not start any new or changed TASK; each still requires its own Task Start gate.

## Validation

Before reporting completion, verify:

- exactly one Epic is `ACTIVE`;
- its directory is the only directory under `execution/active/`;
- the directory name matches the Backlog Epic ID and stable short name;
- the plan is approved and contains the same ordered Tasks that exist in `tasks/`;
- all Epic and Task IDs are globally allocated and unique;
- all TASK definitions are approved;
- all TASK lifecycle values remain `TODO`;
- Task dependencies reference existing IDs and contain no cycle;
- requirement, architecture, ADR, defect, plan, and Task links resolve;
- no product code, hooks, MCP configuration, or unrelated documentation changed.

## Outputs

- updated `BACKLOG.md`;
- `execution/active/EPIC-NNN-<short-name>/plan.md`;
- `execution/active/EPIC-NNN-<short-name>/tasks/TASK-NNN-<short-name>.md`;
- structural `execution/paused/` and `execution/completed/` directories when absent.

Do not continue to implementation automatically. Report that the workspace is ready and request a separate Task Start confirmation.
