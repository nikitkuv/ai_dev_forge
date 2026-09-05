# Production Review Gating Specification

## Purpose

Defines how Forge limits strong-review blockers and repeated strong-model invocations to the production surface while preserving non-production observations and mandatory testing.

## Requirements

### Requirement: Review Packets separate production and supporting surfaces
The system SHALL classify every review-relevant changed path as a production review path or a supporting evidence path. Production review paths SHALL include executable production code and runtime, schema, migration, packaging, build, or deployment artifacts whose contents can change shipped behavior. Supporting evidence paths SHALL include tests, fixtures, snapshots, golden files, test-only configuration, development tooling, examples, and other artifacts that cannot change production behavior. Canonical and lifecycle records SHALL remain context-only inputs outside both surfaces.

#### Scenario: Runtime artifact is production review scope
- **WHEN** a changed schema, migration, runtime configuration, packaging file, build definition, or deployment artifact can alter the shipped system
- **THEN** the Review Packet classifies it as a production review path even though it is not an application source-code file

#### Scenario: Test artifact is supporting evidence
- **WHEN** a changed test, fixture, snapshot, golden file, or test-only configuration cannot alter production behavior
- **THEN** the Review Packet classifies it as supporting evidence and not as a production review path

#### Scenario: An ambiguous path is classified
- **WHEN** a changed artifact's production effect is not obvious from its path or extension
- **THEN** the orchestrator records a classification rationale based on whether its contents can change shipped behavior

### Requirement: Only production findings affect the strong-review outcome
The reviewer SHALL report defects in production review paths as outcome-affecting production findings. The reviewer MAY report defects confined to supporting evidence paths in a separate non-production observations section, but every such observation SHALL be advisory and SHALL NOT prevent `CLEAN`, return the TASK to implementation, or require another reviewer invocation. A supporting artifact that reveals a production defect MAY support a production finding only when the finding identifies the concrete production failure and production location.

#### Scenario: Reviewer finds a defective test assertion
- **WHEN** the production review has no actionable defect and the reviewer finds an incorrect assertion confined to a test
- **THEN** the reviewer returns `CLEAN` with a non-blocking test observation and the orchestrator proceeds toward testing without returning the TASK for another review cycle

#### Scenario: Test evidence exposes a production defect
- **WHEN** a test or fixture demonstrates a concrete failure caused by a production review path
- **THEN** the reviewer reports a production finding with the affected production location and the finding blocks review

#### Scenario: Reviewer finds a dev-only file defect
- **WHEN** a defect is confined to development tooling, examples, or another supporting evidence path and cannot alter shipped behavior
- **THEN** the reviewer records it only as a non-production observation and it does not affect the review outcome

### Requirement: Review freshness depends on track and production fingerprint
For a `standard` TASK, the system SHALL record a reproducible production-surface fingerprint separately from the whole implementation fingerprint. A clean review SHALL remain current while the production fingerprint is unchanged. A production-path change SHALL invalidate review and testing evidence and require another strong review. A supporting-only change SHALL preserve current clean production-review evidence, invalidate affected testing evidence, and SHALL NOT invoke the strong reviewer again. A `fast` TASK SHALL not claim independent-review freshness; every implementation change SHALL invalidate its orchestrator assurance and require current fast eligibility and assurance evidence for the new whole-implementation fingerprint.

#### Scenario: Standard test-only remediation follows clean production review
- **WHEN** remediation of a standard TASK changes only tests or other supporting evidence and the production fingerprint remains equal to the clean reviewed fingerprint
- **THEN** the orchestrator preserves the clean review and sends the new implementation revision directly to the tester gate without another strong-review call

#### Scenario: Standard production remediation changes reviewed behavior
- **WHEN** remediation of a standard TASK changes any production review path or changes the production fingerprint
- **THEN** the orchestrator invalidates the prior review and testing evidence and requires a new strong review before testing

#### Scenario: Standard legacy evidence lacks a production fingerprint
- **WHEN** an active standard TASK has clean review evidence but no reproducible production fingerprint
- **THEN** the system does not reuse that review and requires classification plus a fresh strong review

#### Scenario: Fast implementation changes after assurance
- **WHEN** any production or supporting path in a fast TASK changes after orchestrator assurance
- **THEN** the system invalidates that assurance and requires a new whole-implementation fingerprint, renewed eligibility validation, and repeated fast assurance or escalation to standard

### Requirement: Verification remains a blocking track-specific gate
For a `standard` TASK, non-production observations and review reuse SHALL NOT waive changed tests, selected affected-component tests, applicable Task fuzz smoke, scoped quality checks, coverage selection, or test-integrity requirements. The tester SHALL receive the current implementation fingerprint, current production fingerprint, preserved review evidence, and non-production observations. For a `fast` TASK, the same applicable focused and scoped verification requirements SHALL remain blocking, but the orchestrator SHALL execute or reproduce them as part of fast assurance without invoking a separate tester. Any verification failure SHALL return the TASK to implementation; a fast failure or evidence gap SHALL also escalate the TASK to `standard`.

#### Scenario: Standard advisory test observation corresponds to a failing check
- **WHEN** the reviewer reports a non-production observation and the tester confirms that a required selected check fails
- **THEN** testing fails and the standard TASK returns to implementation without retroactively changing the clean production-review outcome

#### Scenario: Standard tester failure is fixed without production changes
- **WHEN** a tester failure in a standard TASK is remediated only in supporting evidence and the production fingerprint remains unchanged
- **THEN** the orchestrator reruns required testing without invoking the strong reviewer

#### Scenario: Standard required test evidence remains missing
- **WHEN** review is clean but required test execution, integrity, coverage, or selection evidence is missing
- **THEN** the standard TASK cannot advance to user acceptance even though the production review remains clean

#### Scenario: Fast focused verification passes
- **WHEN** the orchestrator reproduces every applicable selected fast check on the current implementation fingerprint and confirms test integrity and acceptance traceability
- **THEN** verification is satisfied without invoking a tester

#### Scenario: Fast verification evidence is incomplete
- **WHEN** any required command, result, coverage selection, independent oracle, or applicability rationale is missing or stale for a fast TASK
- **THEN** the TASK cannot advance, returns to implementation as needed, and escalates to `standard`

### Requirement: Packet and output integrity failures remain blocking
The production-only finding boundary SHALL NOT make missing packet fields, inconsistent fingerprints, unreproducible review diffs, route failures, or malformed reviewer output advisory. Such failures SHALL block progression as orchestration or input-integrity failures without being misclassified as production findings.

#### Scenario: Production fingerprint does not match the packet
- **WHEN** the reviewer cannot reproduce or match the declared production fingerprint
- **THEN** review is blocked until the orchestrator supplies a consistent packet and no clean review is recorded
