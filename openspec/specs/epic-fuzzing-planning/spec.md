# epic-fuzzing-planning Specification

## Purpose

Defines how Forge plans Epic and Task fuzzing early enough to identify applicable targets and missing harness work without making fuzzing mandatory where it provides no meaningful risk coverage.

## Requirements

### Requirement: Epic planning includes a distinct fuzzing plan
The system SHALL include an `Epic Fuzzing Plan` in every proposed Epic plan, distinct from the execution-time `Fuzzing Summary`. The plan SHALL record applicability as `applicable`, `not applicable`, or `unresolved`; risk surfaces; targets and invariants; harness readiness and owning Tasks; Task-level smoke coverage; Epic-level tools or commands, corpus and seeds, budgets, failure criteria, artifact handling, and execution constraints as applicable.

#### Scenario: Applicable fuzzing is planned
- **WHEN** repository evidence identifies a meaningful fuzzable boundary for the Epic
- **THEN** the proposed Epic Fuzzing Plan identifies its targets, invariants, harness readiness, Task mapping, reproducible execution configuration, and failure criteria

#### Scenario: Applicability is unresolved
- **WHEN** available evidence is insufficient to decide whether a meaningful fuzz target or harness exists
- **THEN** the plan records `unresolved` with the exact missing evidence or blocker instead of inventing a target or declaring fuzzing not applicable

### Requirement: Not-applicable fuzzing remains explicit and evidence based
The system SHALL allow planned fuzzing applicability to be `not applicable` only when the plan records why no suitable target exists and identifies alternative risk coverage. After passing Epic Validation, the orchestrator SHALL treat that assessment as current only when final Task fuzzing-impact evidence introduces no target, the implemented affected surface remains consistent with the approved plan, and the planned alternative coverage passed on the current aggregate fingerprint.

#### Scenario: Fuzzing is not meaningful for the Epic
- **WHEN** repository and Epic-scope evidence shows no suitable fuzzable boundary
- **THEN** the proposed plan records `not applicable`, a concrete rationale, and alternative risk coverage without creating a fuzz harness Task

#### Scenario: A planner proposes not applicable without supporting coverage
- **WHEN** the proposed plan lacks either a concrete rationale or alternative risk coverage
- **THEN** the proposal is incomplete and cannot treat fuzzing as not applicable

#### Scenario: Final evidence supports planned not applicable
- **WHEN** Epic Validation passes and final Task and affected-surface evidence satisfies every freshness condition for an approved `not applicable` plan
- **THEN** the orchestrator does not invoke the fuzzer subagent and records the existing `NOT APPLICABLE` outcome with the approved rationale, alternative coverage, and current aggregate fingerprint

#### Scenario: Final evidence contradicts planned not applicable
- **WHEN** final Task or affected-surface evidence identifies a target, missing harness, unresolved applicability, or other mismatch with the approved `not applicable` plan
- **THEN** the orchestrator invokes the runtime fuzzer instead of silently preserving the planner's assessment

### Requirement: Task verification records fuzzing impact without a separate test-plan artifact
Every proposed Task Verification Plan SHALL include a compact `Fuzzing impact` entry and a `Task fuzz smoke` entry. The entries SHALL state whether the Task affects an existing target, introduces a new target, requires a harness, or has no fuzzing impact, and SHALL provide a selected smoke command and budget or an explicit not-applicable rationale.

#### Scenario: Task affects an existing fuzz target
- **WHEN** a Task changes a boundary covered by an existing harness
- **THEN** its Verification Plan maps the affected target to a bounded Task fuzz smoke command and budget

#### Scenario: Task has no fuzzing impact
- **WHEN** a Task does not change or introduce a meaningful fuzzable boundary
- **THEN** its Verification Plan records no fuzzing impact and an explicit not-applicable rationale for Task fuzz smoke

#### Scenario: Task requires a new harness
- **WHEN** the Epic Fuzzing Plan identifies a suitable target without an existing harness
- **THEN** the approved Task sequence assigns harness creation to a Task and records that Task's fuzzing impact accordingly

### Requirement: Existing fuzzing lifecycle semantics are preserved
Advance fuzzing planning SHALL NOT change the existing Epic lifecycle states, runtime fuzzing outcomes, Epic-level execution point for applicable fuzzing, or remediation flow. A planner assessment alone SHALL NOT satisfy the fuzzing acceptance gate; a skipped fuzzer invocation requires the orchestrator's current-fingerprint freshness check and recorded `NOT APPLICABLE` evidence.

#### Scenario: Planned fuzzing is applicable
- **WHEN** the last Task is accepted and Epic Validation passes on the current aggregate fingerprint
- **THEN** the fuzzer runs under the existing `FUZZING` lifecycle stage and returns an existing framework outcome

#### Scenario: Planned fuzzing is not applicable
- **WHEN** Epic Validation passes and the orchestrator confirms that the approved `not applicable` plan remains current and its alternative risk coverage passed
- **THEN** the Epic enters the existing `FUZZING` stage, records `NOT APPLICABLE` without invoking the fuzzer subagent, and may proceed under the existing acceptance gate

#### Scenario: Planned fuzzing is unresolved
- **WHEN** Epic Validation passes while fuzzing applicability remains `unresolved`
- **THEN** the orchestrator invokes the fuzzer under the existing `FUZZING` stage to return an existing framework outcome
