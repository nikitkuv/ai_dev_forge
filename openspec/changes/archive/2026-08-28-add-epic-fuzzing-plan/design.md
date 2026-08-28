## Context

The preparation workflow currently mentions fuzzing, but the neutral planner contract does not require a structured fuzzing proposal. The Epic template records only execution results in `Fuzzing Summary`, so target selection and missing harness work may be deferred until the final `FUZZING` stage. Task verification is already planned in each TASK file and Epic-wide checks are already planned in `plan.md`.

## Goals / Non-Goals

**Goals:**

- Make fuzzing applicability and harness readiness visible at Plan Approval.
- Keep planned fuzzing inputs separate from execution evidence.
- Map relevant Task changes to bounded fuzz smoke checks without duplicating Task test plans.
- Avoid invoking the runtime fuzzer when an approved `not applicable` assessment remains current at Epic completion.

**Non-Goals:**

- Add or select a framework-wide fuzzing engine.
- Require fuzzing where no meaningful target exists.
- Change lifecycle states, outcomes, remediation gates, or the Epic-level timing of applicable fuzzing.
- Create a separate fuzzing or test-plan artifact.

## Decisions

### Store planned and observed fuzzing information separately in `plan.md`

Add `Epic Fuzzing Plan` before the mandatory quality gates and retain `Fuzzing Summary` for runtime evidence. This avoids mixing approved intent with mutable execution results. A separate file was rejected because Forge deliberately keeps Epic strategy and evidence in one plan and prohibits separate fuzzing reports.

### Let an approved planner assessment avoid an unnecessary fuzzer invocation

The planner proposes `applicable`, `not applicable`, or `unresolved` from repository evidence, and the orchestrator checks it before Plan Approval. After passing Epic Validation, the orchestrator compares an approved `not applicable` assessment with final Task fuzzing-impact entries, the actual affected surface, alternative-coverage results, and the current aggregate fingerprint. If all remain consistent, it records the existing `NOT APPLICABLE` outcome without invoking the fuzzer subagent. For `applicable`, `unresolved`, or contradictory evidence, it invokes the fuzzer normally. The Epic still enters `FUZZING`, so no lifecycle transition is added or removed.

### Extend existing Task Verification Plans with two compact entries

Each TASK gains `Fuzzing impact` and `Task fuzz smoke`. These fields live beside focused and affected checks, because the existing per-Task Verification Plan is already the source of truth for Task test selection. A separate Task test plan was rejected as duplicative and prone to drift.

### Keep planning fields structured but tool-neutral

The Epic section records applicability, surfaces, targets/invariants, harness readiness and Task ownership, smoke mapping, Epic campaign configuration, failure criteria, artifacts, constraints, and alternative coverage. It does not mandate a library or command when repository evidence does not establish one; unresolved inputs remain explicit blockers.

## Risks / Trade-offs

- More planning fields can encourage speculative detail. -> Require evidence-backed values and allow `unresolved` with an exact blocker.
- Planned applicability can become stale as implementation changes. -> Skip the fuzzer only after an orchestrator freshness check against final Task and affected-surface evidence; invoke it on any mismatch or unresolved assessment.
- Task fuzz smoke can be mistaken for the final campaign. -> Keep it bounded and selected for the affected Task surface; retain the mandatory Epic-level stage after validation.
- Documentation surfaces can drift. -> Add contract tests covering planner instructions, templates, preparation/completion guidance, conditional fuzzer invocation, and unchanged lifecycle outcomes.

## Migration Plan

Update the framework-owned neutral sources and tests in one release. Existing project plans remain valid under the current migration policy; compatibility checks can report the missing new planning fields when such plans are resumed or migrated, without silently inventing them.
