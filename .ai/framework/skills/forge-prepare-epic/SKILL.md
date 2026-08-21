---
name: forge-prepare-epic
description: Prepare one PLANNED and READY Epic as an approved queued workspace under execution/planned, and optionally activate it through the separate Epic Start gate.
---

# Prepare an Epic

## Verify eligibility

1. Read `BACKLOG.md`, approved SPEC and ARCHITECTURE, relevant ADRs, execution state, templates, conventions, and framework contracts.
2. Require the selected Epic to be `PLANNED + READY` with approved requirements and boundaries and explicitly declared dependencies and blockers.
3. Allow declared unsatisfied dependencies, `Blocked by`, another active-work Epic, and other planned workspaces during planning. They prevent Epic Start, not Plan Approval.
4. Require no workspace for the same Epic in another execution state and no conflicting planned directory or global Task ID. An existing planned workspace may change only through Replan.
5. Stop and ask the user when a planning precondition fails; do not reorder or bypass dependencies.

## Prepare the proposal

Follow `.ai/04-prepare-workspace.md`:

1. On Codex, invoke the strong read-only `epic-planner` with canonical, repository, CI, quality-configuration, contract, convention, and template evidence. On Claude Code, read the complete neutral `.ai/framework/agents/epic-planner.yaml` contract, build the identical assignment, and run `.claude/forge/codex-role-runner.mjs --preflight`. If preflight is available, write the contract and assignment to a secure temporary prompt file and invoke the runner with `--role epic-planner --prompt-file <path>`; always remove that temporary file. If preflight is unavailable, invoke the generated native Claude `epic-planner` with the identical assignment and report the fallback reason. Once a Codex task starts, a non-zero exit or malformed result blocks planning and never falls back;
2. require a proposal containing the Epic strategy, requirement coverage, selected quality profiles, risks, ordered Task graph, Task definitions, Task verification selections, review focus, and Epic Verification Plan;
3. independently verify the proposal; never treat agent output as approval or canonical truth;
4. allocate project-global TASK IDs without restarting per Epic or reusing retired IDs;
5. create each TASK definition with scope, exclusions, constraints, acceptance criteria, affected surface, risk flags, review focus, selected Task checks, manual verification, references, and `status: TODO`;
6. reserve the full project suite and unscoped global checks for Epic Validation;
7. keep plan `document_status` and TASK `definition_status` in `draft` while revising the proposal;
8. do not require a generic atomicity classifier; reshape work only for a concrete planning or execution need.

Show the complete plan, TASK definitions, and exact planned-workspace diff. Request explicit **Plan Approval**. After approval, atomically write the approved plan and `TODO` TASK definitions to `execution/planned/EPIC-NNN-<short-name>/` without changing the Backlog Epic from `PLANNED`.

Multiple planned workspaces may coexist. Their queue order remains the user-defined Backlog priority and row order; directory names or creation times never reorder them.

## Optionally activate atomically

Epic Start may occur immediately or later. Before requesting it, require satisfied dependencies, empty `Blocked by`, no other nonterminal active-work Epic, and an unchanged approved planned workspace.

After explicit Epic Start authorization:

1. move `execution/planned/EPIC-NNN-<short-name>/` to `execution/active/`;
2. transition only that Epic from `PLANNED` to `ACTIVE` in `BACKLOG.md`;
3. validate the Backlog and execution tree as one logical state transition;
4. on failure, restore the complete workspace under `execution/planned/` and the Backlog status to `PLANNED`.

Plan Approval and Epic Start are separate gates. One user message may grant both only when it clearly states both decisions.

The first TASK remains `TODO`. Do not implement it until its separate Task Start gate.

Any later Task scope, order, or composition change requires a displayed diff and the Replan gate in planned, active, or paused workspaces. Replan approval does not activate an Epic or start a TASK.

Return the planned or active workspace, validation result, queue position from Backlog, and the pending Epic Start or first Task Start decision.
