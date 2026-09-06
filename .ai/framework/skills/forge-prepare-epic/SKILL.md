---
name: forge-prepare-epic
description: Prepare one PLANNED and READY Epic as an approved queued workspace under execution/planned, and optionally activate it through the separate Epic Start gate.
---

# Prepare an Epic

Use Python `context`/`validate` for inventory and ID consistency, and `section` for relevant source excerpts; do not delegate mechanical collection to a model. Pass the planner one bounded assignment with authoritative relevant context and the complete role contract. For external routes prefer `python .ai/tools/forge.py role --orchestrator <active> --role epic-planner --prompt-file <path>`; its single internal preflight replaces the separate preflight/legacy-launcher sequence below. Never switch transport after a started failure. Reuse current INV research and avoid duplicating unrelated backlog/task bodies in the prompt.

## Verify eligibility

For native_subagents the generated agent already contains the complete neutral role contract: send only the assignment/evidence, not a duplicate of those instructions. For an external CLI concatenate the full neutral contract exactly once. All routes receive the same effective contract and assignment.

1. Read `BACKLOG.md`, approved SPEC and ARCHITECTURE, relevant ADRs, execution state, templates, conventions, framework contracts, explicitly referenced `INV-NNNN` records, obvious investigation matches by subject, area, or relevant paths, and any Backlog source keys plus optional work-source provenance relevant to the selected Epic. Confirm uncertain INV matches with the user. Check each selected investigation's baseline, relevant paths, and material assumptions; reuse applicable research and recheck only doubtful portions.
2. Require the selected Epic to be `PLANNED + READY` with approved requirements and boundaries and explicitly declared dependencies and blockers.
3. Allow declared unsatisfied dependencies, `Blocked by`, another active-work Epic, and other planned workspaces during planning. They prevent Epic Start, not Plan Approval.
4. Require no workspace for the same Epic in another execution state and no conflicting planned directory or global Task ID. An existing planned workspace may change only through Replan.
5. Stop and ask the user when a planning precondition fails; do not reorder or bypass dependencies.

## Prepare the proposal

Follow `.ai/04-prepare-workspace.md`:

1. Read `.ai/project.yaml` and require a valid `role_execution.mode`. Build one assignment from the complete neutral `.ai/framework/agents/epic-planner.yaml` contract plus the canonical, repository, CI, quality-configuration, convention, contract, and template evidence. Route it exactly as configured: `native_subagents` invokes the active Codex, Claude Code, or OpenCode platform's generated planner with no external preflight; `claude_with_codex` requires Claude Code and uses `.claude/forge/codex-role-runner.mjs`; `codex_with_claude` requires Codex and uses `.codex/forge/claude-role-runner.mjs` with `models.claude.strong.model` and effort. OpenCode-led setup proposes the existing `native_subagents` value by default only when no approved route exists; it adds no mode and does not silently rewrite an approved value. For either external route, run preflight, block on unavailability or active-orchestrator mismatch, pass the assignment through a secure temporary prompt file, and always remove the file. There is no fallback before or after execution; a non-zero exit, timeout, permission failure, runtime mismatch, or malformed result blocks planning;
2. require a proposal containing the Epic strategy, Research Context with every used `INV-NNNN` and its applicability check, requirement coverage, selected quality profiles, risks, ordered Task graph, Task definitions, exactly one delivery track per Task with rationale, Task verification selections, review focus, Epic Verification Plan, and an evidence-based Epic Fuzzing Plan;
3. independently verify the proposal; never treat agent output as approval or canonical truth;
4. allocate project-global TASK IDs without restarting per Epic or reusing retired IDs;
5. create each TASK definition with scope, exclusions, constraints, acceptance criteria, affected surface, risk flags, approved delivery track, review focus, selected Task checks, manual verification, applicable `research_refs`, references, and `status: TODO`; require criterion-by-criterion fast eligibility and disqualifier evidence, treat low risk alone as insufficient, and select standard for missing or uncertain evidence;
6. when the Epic has external work sources, map every source slice to one or more proposed TASKs, set each TASK's `external_sources`, and populate the plan's source-coverage matrix without treating source status as Forge approval;
7. require the Epic Fuzzing Plan to classify applicability as `applicable`, `not applicable`, or `unresolved`; map risk surfaces, targets and invariants, harness readiness, missing harness work, Task smoke coverage, reproducible campaign configuration, failure criteria, artifact handling, constraints, and alternative coverage; reject `not applicable` without both rationale and alternative risk coverage, and reject `unresolved` without the exact missing evidence or blocker;
8. require every TASK Verification Plan to record `Fuzzing impact` and a bounded `Task fuzz smoke` command and budget or explicit not-applicable rationale;
9. reserve the full project suite and unscoped global checks for Epic Validation;
10. keep plan `document_status` and TASK `definition_status` in `draft` while revising the proposal;
11. do not require a generic atomicity classifier; reshape work only for a concrete planning or execution need.

Show the complete plan, TASK definitions, and exact planned-workspace diff. Request explicit **Plan Approval**. After approval, atomically write the approved plan and `TODO` TASK definitions to `execution/planned/EPIC-NNN-<short-name>/` without changing the Backlog Epic from `PLANNED`.

For every used investigation, add reciprocal Epic/TASK links to its Linked Work and Outcome History during the same approved plan write. Do not change an INV to `promoted` until the corresponding canonical work is approved.

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

Any later Task scope, order, composition, or external-source coverage change requires a displayed diff and the Replan gate in planned, active, or paused workspaces. Apply TASK source references, plan coverage, and `.ai/integrations/work-items.yaml` reverse mappings as one validated logical transition. Re-read versioned source items before approval; stale material content invalidates the proposal. Replan approval does not activate an Epic or start a TASK.

Weakening an approved delivery track from standard to fast before Task Start also requires Replan. Standard-to-fast is forbidden after Task Start. A recorded fast-to-standard safety escalation with unchanged scope does not require Replan; any accompanying scope change still does.

Return the planned or active workspace, validation result, queue position from Backlog, and the pending Epic Start or first Task Start decision.
