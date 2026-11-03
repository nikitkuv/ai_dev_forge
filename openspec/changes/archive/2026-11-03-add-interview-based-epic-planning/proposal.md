# Proposal — add-interview-based-epic-planning

## Why

Epic planning today is one-shot: `epic-planner` produces `plan.md` and every TASK definition in a single run, and `Plan Approval` is the human's first read of a large artifact. Interface decisions — which contracts, schemas, and component boundaries change, and to what shape — are therefore reviewed late and in bulk, which is the most expensive place to catch a wrong direction and the main source of review fatigue. The framework already uses the interview pattern where it works well (INT intake's short interview, bootstrap's product interview); epic planning is the only large flow without it. The "design the interface, delegate the implementation" principle should govern planning: the human approves the epic's interface step by step, and the planner fills the details afterward.

## What Changes

- **Staged planning interview** — epic preparation becomes a stepwise interview: objective and expected outcome → interface design → risks and critical paths → decomposition skeleton (task names, one verifiable outcome each). Each stage's artifact is confirmed by the user before the next stage begins.
- **Contract sketches** — the interface stage produces a sketch of every public contract the epic changes (signatures, schema fields, error behavior): the human-approved shape that implementation must honor. TASKs that touch no public contracts record that no sketch applies.
- **Deferred detail filling** — test cases, change maps, fuzz plans, and delivery-track evidence are filled in by the planner only after the skeleton is confirmed. Plan Approval then verifies consistency of an already-agreed design; any interface change that appears at that point returns to the interview instead of being approved silently.
- **Proportional fast path** — trivial epics may collapse interview stages with recorded rationale; nothing collapses silently.

## Capabilities

### New Capabilities

- `epic-planning-interview`: Staged interview flow for epic preparation with per-stage user confirmation, interface-first ordering, and detail filling deferred until the skeleton is approved.
- `task-contract-sketch`: Per-task contract-shape artifacts for public-contract work — prepared before Plan Approval, bound at Task Start, and checked at independent review.

### Modified Capabilities

(none — today's planning behavior lives in skills, templates, and contracts rather than in existing spec requirements; the timing contracts of `test_planning` and `task_change_map` are preserved unchanged)

## Impact

- **Skills and roles**: `forge-prepare-epic` is reworked into the staged interview; `epic-planner`'s neutral definition takes the confirmed skeleton as its assignment input; `forge-run-task` binds the approved sketch at Task Start and includes sketches in the Review Packet; `reviewer` checks sketch conformance.
- **Templates**: `plan.md` gains an `Interface Delta` section and records interview stage confirmations in Epic User Validation History; `TASK.md` gains a `Contract Sketch` section.
- **Contracts**: `.ai/framework/contracts.yaml` gains a `contract_sketch` contract (applicability, preparation time, Replan on shape change) without altering existing gate timing.
- **Existing projects**: additive and legacy-tolerant — already planned or active epics continue without re-interview; TASKs without sketches behave exactly as today. New epics default to the interview flow.
- **Tests**: contract tests for stage gating and sketch conformance, Python unit tests for template contracts, matching the existing `tests/` layout.
