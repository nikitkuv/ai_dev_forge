## 1. Planning Contracts and Templates

- [x] 1.1 Add the structured `Epic Fuzzing Plan` to the Epic plan template and add `Fuzzing impact` plus `Task fuzz smoke` to the Task Verification Plan template; verify the template fields cover every requirement in `specs/epic-fuzzing-planning/spec.md` without creating a separate artifact.
- [x] 1.2 Update the neutral epic-planner contract and Epic preparation guidance so every proposal evaluates fuzzing applicability, targets, harness readiness, Task ownership, reproducible configuration, failure criteria, constraints, and alternative coverage; verify `not applicable` and `unresolved` cannot be emitted without their required evidence.

## 2. Conditional Runtime Invocation

- [x] 2.1 Update framework fuzzing gates and Epic completion guidance so an approved, current `not applicable` plan records `NOT APPLICABLE` without invoking the fuzzer, while `applicable`, `unresolved`, or contradictory final evidence invokes it after passing Epic Validation; verify existing lifecycle states, outcomes, and remediation transitions remain unchanged.
- [x] 2.2 Update the neutral fuzzer and framework conformance/resume/final-validation guidance to consume the approved fuzzing plan when invoked and to validate the orchestrator's current-fingerprint evidence when invocation is skipped; verify a stale plan or changed Task fuzzing impact cannot silently bypass the fuzzer.

## 3. Documentation and Regression Coverage

- [x] 3.1 Update framework documentation, runbook, scenario, and adapter guidance to describe planning-time applicability and conditional fuzzer invocation consistently; verify no maintained document still claims the fuzzer is always invoked after passing Epic Validation.
- [x] 3.2 Add automated contract tests for the Epic and Task planning fields, evidence requirements, conditional invocation branches, and unchanged lifecycle outcomes; run `node --test tests/*.test.mjs` and OpenSpec strict validation successfully.
