## Why

Forge evaluates fuzzing applicability only at the end of an Epic, so a missing harness can be discovered after every planned Task is already complete. Epic planning should identify fuzzable risk surfaces and harness work early while still allowing fuzzing to be explicitly not applicable when alternative risk coverage is defined.

## What Changes

- Add an `Epic Fuzzing Plan` section to the Epic plan, separate from the post-run `Fuzzing Summary`.
- Require `epic-planner` to propose fuzzing applicability, targets and invariants, harness readiness, Task mapping, tools and commands, corpus/seeds, budgets, failure criteria, artifact handling, constraints, and alternative coverage where fuzzing is not applicable.
- Add compact `Fuzzing impact` and `Task fuzz smoke` entries to each Task Verification Plan.
- Treat the planner's applicability assessment as a proposal checked by the orchestrator. After passing Epic Validation, skip the fuzzer subagent and record `NOT APPLICABLE` only when that approved assessment remains current against final Task and affected-surface evidence and its alternative coverage passed.
- Invoke the runtime fuzzer for `applicable` or `unresolved` plans and whenever final evidence contradicts a planned `not applicable` assessment.
- Preserve the existing Epic lifecycle, fuzzing outcomes, Epic-level timing for applicable fuzzing, and remediation flow.

## Capabilities

### New Capabilities

- `epic-fuzzing-planning`: Defines advance, risk-based fuzzing planning for an Epic and its Tasks without changing the existing runtime fuzzing gate.

### Modified Capabilities

None.

## Impact

- Affects the neutral `epic-planner` and `fuzzer` contracts, Epic and Task templates, Epic preparation and completion workflow guidance, framework contracts, final validation guidance, and their contract tests.
- Does not add a fuzzing engine, require fuzzing for inapplicable work, or change lifecycle states and outcomes.
