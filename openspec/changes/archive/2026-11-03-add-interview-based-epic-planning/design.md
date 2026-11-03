# Design — add-interview-based-epic-planning

## Context

See proposal.md for motivation. Today `forge-prepare-epic` drives `epic-planner` to produce `plan.md` and all TASK definitions in one run; `Plan Approval` is the first human read. The framework already runs interviews where they fit (`forge-intake-feature`'s short INT interview, bootstrap's product interview). Role split that shapes this design: the orchestrator owns all user dialogue; subagents are one-shot assignment-and-report workers and never talk to the user. Timing contracts in `contracts.yaml` (`test_planning` and `task_change_map` prepared `task_definition_before_plan_approval`) must be preserved — the deferral introduced here happens inside the pre-approval phase, not across it.

## Goals / Non-Goals

**Goals:**
- Interface decisions are reviewed by the human on small artifacts before any bulk detail exists.
- The planner implements the plan behind a confirmed skeleton instead of presenting its first draft as the review unit.
- Contract shapes for public interfaces are approved before code exists and checked at review.
- Total human planning effort goes down: stepwise confirmations replace one large first read.

**Non-Goals:**
- No change to `Plan Approval`'s authority, gate timing, or any existing lifecycle transition.
- No human design of internal implementation — the interface stage stops at contract shapes and boundaries (the framework's existing ban on line-by-line instructions stays).
- No change to delivery tracks, review gating scope, or fuzzing contracts.
- No new subagent that interviews the user; no interview automation outside the orchestrator.

## Decisions

### D1: The orchestrator conducts the interview; the planner fills details after skeleton confirmation

`forge-prepare-epic` is reworked into four orchestrator-led stages with per-stage confirmation. `epic-planner`'s assignment input becomes the confirmed skeleton (plus the interface stage output), and its output is the filled plan and TASK details. *Alternatives:* repeated `epic-planner` calls between stages (rejected — subagents are one-shot reporters and cannot conduct dialogue; it would also multiply strong-tier cost); user-filled planning forms (rejected — the interview must feel like a dialogue, matching INT intake).

### D2: Stage artifacts reuse existing plan sections plus one new `Interface Delta`

Stage outputs map onto plan.md sections already owned by the plan: Objective / Expected Outcome (stage 1), Implementation Strategy with a new `Interface Delta` subsection listing intended interface changes (stage 2), Risks (stage 3), Ordered Task Sequence skeleton rows (stage 4). Interview confirmations are recorded as rows in the existing Epic User Validation History table — no new tracking document. *Alternatives:* a separate interview record file (rejected — one more source of truth to drift); frontmatter-only timestamps (rejected — the history table already carries Date/Scope/Result and is user-visible).

### D3: Contract sketches live in `TASK.md` beside Affected Surface, wired through packet and review

A `Contract Sketch` section (table: contract, approved shape, references) sits beside `Affected Surface and Risk`. Applicability follows the existing risk flags — sketch required when affected contracts include public interfaces, explicit "none" otherwise. The Review Packet carries sketches; `reviewer.yaml` gains a conformance step per changed contract inside acceptance traceability; `forge-run-task` binds sketches at Task Start. Shape changes route through Replan like any scope change. *Alternatives:* sketches in ADRs (rejected — ADRs are decisions, not per-task contract shapes); sketches generated from code after implementation (rejected — inverts the principle; the shape must exist before code).

### D4: Stage collapse follows the delivery-tracks evidence pattern

Collapsing or merging stages requires a recorded rationale in the interview record — the same "proportional with evidence" discipline as `fast` eligibility. Missing rationale keeps all four stages.

### D5: Compatibility is additive

Existing approved plans and legacy TASKs continue unchanged; `contracts.yaml` timing fields keep their current values; the interview is the default only for newly prepared epics. The consistency check at Plan Approval is the only new hard behavior, and it can only fire on plans that used the interview.

## Risks / Trade-offs

- [Interview feels heavier than one-shot planning] → it replaces the one-shot first read rather than adding to it; stages are one artifact each; the collapse path exists for bounded epics. If human time still grows, the stage count is the first knob.
- [Filled details drift from the confirmed skeleton] → Plan Approval's consistency check returns the plan to the interview; contract tests cover the return path.
- [Contract sketches over-specify internals] → the sketch is shape-only (signatures, fields, error behavior); reviewer guidance and the spec explicitly exclude internal structure.
- [Planner bypasses the skeleton] → the assignment contract requires the confirmed skeleton as input; plan-order validation is extended to reject detail sections without skeleton confirmations.
- [Interview stages become a rubber stamp] → confirmations are recorded rows with scope and result; a declined stage must be revised, which keeps the gate meaningful.

## Migration Plan

1. Ship the bundle update (skills, templates, contracts, definitions) through the existing `MIGRATE.md` preview/apply flow; template additions are additive.
2. Run adapter sync so planner/reviewer role definitions and the router regenerate, then recompute `.ai/framework.lock`.
3. New epics use the interview; in-flight epics finish under their approved plans; rollback is the additive-field inverse with no data repair.

## Open Questions

None that would change the specs or task breakdown.
