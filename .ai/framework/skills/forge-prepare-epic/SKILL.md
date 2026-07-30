---
name: forge-prepare-epic
description: Prepare and activate one approved Epic by creating its plan and initial TASK files. Use when a user selects a PLANNED Epic for execution and the workflow must verify READY state, blockers, plan approval, and the explicit Epic Start gate.
---

# Prepare an Epic

## Verify eligibility

1. Read `BACKLOG.md`, approved SPEC and ARCHITECTURE, relevant ADRs, execution state, templates, conventions, and framework contracts.
2. Require the selected Epic to be `PLANNED`, `READY`, dependency-satisfied, and free of unresolved `Blocked by` entries.
3. Require no other `ACTIVE` Epic or conflicting active directory.
4. Stop and ask the user when any precondition fails; do not reorder or bypass dependencies.

## Prepare the proposal

Follow `.ai/04-prepare-workspace.md`:

1. create the Epic objective, outcome, dependencies, risks, strategy, ordered Task sequence, acceptance criteria, and quality gates;
2. allocate project-global TASK IDs without restarting per Epic or reusing retired IDs;
3. create each TASK definition with scope, exclusions, constraints, acceptance criteria, required tests, manual verification, references, and `status: TODO`;
4. keep plan `document_status` and TASK `definition_status` in `draft` while revising the proposal;
5. do not require a generic atomicity classifier; reshape work only for a concrete planning or execution need.

Show the complete plan, TASK definitions, and exact Backlog/workspace diff. Request explicit user approval of the plan and definitions, then request the separate **Epic Start** authorization. One user message may grant both only when it states both decisions clearly.

## Activate atomically

After both gates:

1. write the approved plan and all approved TASK definitions;
2. create `execution/active/EPIC-NNN-<short-name>/plan.md` and its `tasks/` files;
3. transition only that Epic from `PLANNED` to `ACTIVE` in `BACKLOG.md`;
4. validate the Backlog and execution tree as one logical state transition and roll back partial writes on failure.

The first TASK remains `TODO`. Do not implement it until its separate Task Start gate.

Any later Task scope, order, or composition change requires a displayed diff and the Replan gate. Replan approval does not start a TASK.

Return the prepared workspace, validation result, and the pending first Task Start decision.
