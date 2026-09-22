---
document_type: task
id: TASK-NNN
epic_id: EPIC-NNN
definition_status: draft
status: TODO
blocked_by: []
created_at: "<YYYY-MM-DD>"
definition_approved_at:
started_at:
risk_level: standard
risk_flags: []
delivery_track: standard
external_sources: []
research_refs: []
---

# TASK-NNN — <Task Title>

## Goal

<State one logical, independently verifiable outcome.>

## Context

<Explain why this Task exists and the relevant product or architecture context. Link to canonical sources instead of duplicating them.>

## Scope

- <Required change or deliverable.>

## Out of Scope

- <Explicit exclusion that protects the Task boundary.>

## Constraints

- <File, component, compatibility, security, operational, or process constraint.>

## Affected Surface and Risk

- **Affected components:** <Components, packages, services, screens, pipelines, models, or infrastructure units.>
- **Affected contracts:** <APIs, schemas, events, storage formats, public interfaces, training/serving contracts, or —.>
- **Risk level:** <low/standard/high with rationale.>
- **Risk flags:** <Public contract, authorization, persistence, migration, concurrency, shared core, dependency/build, frontend critical path, data/ML, operations, or —.>
- **Failure impact:** <User, data, compatibility, security, availability, cost, or model-quality impact.>

## Planned Change Map

Record this map during Task definition, before Plan Approval. It owns the per-Task implementation forecast; the Epic plan links here. Follow `task_change_map` in `.ai/framework/contracts.yaml`.

| System part | Repository path and symbol or section | Action | Planned change and reason |
| --- | --- | --- | --- |
| <Component, service, screen, pipeline, or other unit> | <Repository-relative file; function/class/section when useful> | <modify/create/delete/move> | <What changes here and which Task outcome it supports> |

Include production code and relevant tests, configuration, schemas, migrations, and documentation. Verify existing paths against the repository; label new paths as proposed. For a move, record both paths. A bounded directory is acceptable only with a reason why exact files cannot yet be named and a concrete step to resolve them. Do not present guessed paths as existing files or list line-by-line implementation instructions.

- **Indirect impact:** <Consumers, callers, shared components, data flows, or contracts affected without planned edits; explain the dependency and link each impact to Verification Plan coverage, or explicit none with rationale.>
- **Uncertainties:** <Unconfirmed path or impact, missing evidence, and resolution step; or none. Unknown component/contract boundaries must be resolved before Plan Approval.>

This is a planning forecast, not the actual changed-file inventory. Recheck it at Task Start. Record justified file-level refinements within approved boundaries; changes to scope, affected components, or contracts require Replan. Keep actual paths and deviations in Implementation Summary.

## Delivery Track

- **Selected track:** <fast/standard; defaults to standard and remains independent from model tier and risk level.>
- **Track rationale:** <Why this assurance route is appropriate for the approved scope.>
- **Fast eligibility evidence:** <For fast: criterion-by-criterion evidence for bounded scope, reversible change, low risk, unambiguous expected behavior, and deterministic focused verification; otherwise not applicable.>
- **Disqualifier disposition:** <For fast: explicit none-with-evidence disposition for public contract, authorization, security/privacy, persistence/data format, schema/migration, concurrency/shared core, dependency/production build, packaging/deployment/runtime infrastructure, external integration, critical paths, test weakening, and unresolved surface/verification; otherwise standard rationale.>
- **Approved through:** <Plan Approval/Replan and date.>
- **Track escalation history:** <None, or fast -> standard trigger, timestamp, fingerprint, and whether scope changed.>

Missing, uncertain, or contradictory fast evidence requires `standard`. `fast -> standard` is a monotonic safety escalation; `standard -> fast` is forbidden after Task Start.

## Acceptance Criteria

- [ ] <Observable, objectively verifiable condition.>

## Verification Plan

### Planned Test Cases

Prepare this list before Plan Approval under `test_planning` in `.ai/framework/contracts.yaml`. Give acceptance criteria stable local IDs (for example AC-1) and each case a stable Task-local ID (TC-1). Cover every acceptance criterion and affected risk; include applicable normal, boundary, invalid-input, failure/recovery, state-transition and side-effect scenarios. Keep the list proportional to the Task; do not fill a fixed quota of test categories.

| Case | AC or risk | Scenario and inputs/preconditions | Expected observable result and independent source | Level and target | Existing or new | Expected RED or rationale |
| --- | --- | --- | --- | --- | --- | --- |
| TC-1 | AC-1 / <risk> | <Given / when, including relevant boundary values> | <Then; requirement, contract, invariant or approved example> | <unit/integration/E2E/manual; existing test reference or proposed location> | <reuse/extend/new> | <Missing behavior that should fail before the production edit; or why an existing regression/manual check should not start RED> |

Do not derive expected results from current production output or freeze private implementation details. Verify existing test references and label proposed locations. Reuse adequate existing tests; a check already proving unchanged behavior need not be made artificially RED. Documentation-only or other TDD-not-applicable work still names proportionate checks and expected results with a rationale. No executable tests or claimed RED results are required during planning.

Unknown expected behavior or material coverage gaps block Plan Approval. For a missing harness or command, name the missing evidence, owning Task and resolution step before dependent execution; never invent a runnable command. Revalidate cases at Task Start, refine in-scope details with reasons, and use Replan for scope or behavior-contract changes. A planned list is not evidence of execution and does not prohibit discovering additional in-scope cases.

### Check Selection and Execution

- **Approach:** <TDD by default for bug fixes and meaningful business logic, or a recorded reason why it is not applicable.>
- **Focused behavior tests:** <Tests that directly prove the acceptance criteria and important failure paths.>
- **Affected-component tests:** <Selected related suites and why they cover the affected surface.>
- **Scoped quality checks:** <Scoped lint, typecheck, build, contract, security, performance, accessibility, ML, data, or infrastructure checks.>
- **Selection rationale:** <Map changed and affected surfaces to the selected commands.>
- **Epic-only checks:** <Full project suite and unscoped project-wide checks deferred to Epic Validation.>
- **Execution constraints:** <Required services, fixtures, datasets, environments, budgets, or objective limitations.>
- **Fuzzing impact:** <existing target affected/new target/harness required/none, with target or rationale.>
- **Task fuzz smoke:** <Bounded command and budget for an affected target, or explicit not-applicable rationale.>

Removing or weakening an approved check requires an explicit rationale and orchestrator disposition. Expanding implementation beyond the affected surface requires scope correction or Replan, not a silent fallback to the full project suite.

## Review Focus

- <Acceptance invariant, boundary, failure mode, compatibility concern, or risk that the independent reviewer challenges for standard or the orchestrator assurance challenges for fast.>

## Manual Verification

1. <Reproducible manual step and expected result.>

## References

- **Requirements:** <FR-/NFR-/BR-IDs>
- **Architecture:** <Section or component>
- **Decisions:** <ADR-IDs or —>
- **Epic plan:** <Relative path to plan.md>
- **Related defects:** <BUG-IDs or —>
- **External sources:** <Provider-neutral work-source keys from `external_sources`, or —>
- **Investigations:** <INV-NNNN keys from `research_refs`, or —>

## Workflow State

Lifecycle values and transitions are defined only in `.ai/framework/contracts.yaml`. `status` in frontmatter is the sole lifecycle status for this Task.

For `standard`, set `status` to `IN REVIEW` only after implementation evidence and the Review Packet are current, to `IN TESTING` only after a protocol-complete `CLEAN` production review, and to `AWAITING USER ACCEPTANCE` only after selected Task testing passes. For `fast`, transition directly from `IN PROGRESS` to `AWAITING USER ACCEPTANCE` only after current passing orchestrator assurance for the exact whole-implementation fingerprint. Any fast implementation change invalidates fast assurance. A fast eligibility failure escalates to standard before acceptance.

```yaml
current_gate: task_start
implementation_revision: 0
current_fingerprint:
production_fingerprint:
review_packet:
  base_fingerprint:
  implementation_revision:
  implementation_fingerprint:
  production_fingerprint:
  diff_fingerprint:
  changed_paths: []
  production_review_paths: []
  supporting_evidence_paths: []
  ambiguous_path_classification: []
review:
  revision:
  implementation_fingerprint:
  production_fingerprint:
  outcome:
  non_production_observations: []
  completed_at:
testing:
  revision:
  implementation_fingerprint:
  production_fingerprint:
  outcome:
  completed_at:
fast_assurance:
  revision:
  implementation_fingerprint:
  eligibility_revalidated:
  outcome:
  completed_at:
```

Use a reproducible Git commit, tree, or scoped diff hash for the whole implementation fingerprint and a reproducible hash of `production_review_paths` for the production fingerprint. Classify by production effect, not directory name: executable code plus runtime configuration, schemas, migrations, generated runtime assets, packaging, production build and deployment files are production when they can change shipped behavior; tests, fixtures, snapshots, golden files, test-only configuration, development tooling and examples are supporting evidence when they cannot. Record a rationale for ambiguous paths. Canonical and lifecycle records remain context only and belong to neither list.

Standard review evidence is current when its production fingerprint equals the current production fingerprint and packet integrity is complete. Standard testing evidence is current only for the current implementation revision and whole implementation fingerprint. Fast assurance is current only for the exact current whole implementation fingerprint and revalidated eligibility. Legacy TASKs without `delivery_track` are standard; legacy review evidence without a production fingerprint is not reusable and requires a fresh review.

## Implementation Summary

- **Base revision:** <Base commit, tree, or reproducible fingerprint>
- **Revision:** <implementation revision>
- **Fingerprint:** <Git commit, tree, or scoped diff hash>
- **Production fingerprint:** <Reproducible hash of the production review paths>
- **Files changed:** <Compact list>
- **Change-map reconciliation:** <Planned versus actual paths, justified refinements, unused planned paths, and any Replan reference.>
- **Production review paths:** <Executable or shipped-behavior-affecting paths>
- **Supporting evidence paths:** <Tests and other non-production paths>
- **Ambiguous path classification:** <Path, classification, and production-effect rationale, or —>
- **Affected-surface or risk changes:** <None, or correction to the approved plan>
- **Behavior delivered:** <Compact summary>
- **Tests added or changed:** <Compact summary>
- **Planned-case reconciliation:** <TC IDs mapped to actual test references, commands and results; added, changed or unexecuted cases with reasons and required dispositions.>
- **RED/GREEN evidence:** <Commands and expected RED/GREEN results, or allowed not-applicable rationale>
- **Selected checks:** <Focused, affected, and scoped command/result summary>
- **Early full-suite authorization:** <Explicit user request and result, or —>
- **Known limitations:** <None or compact list>

Do not paste full agent responses or long tool logs.

## Fast Assurance Summary

- **Assurance fingerprint:** <Exact current whole-implementation fingerprint, or not applicable for standard>
- **Revision assured:** <implementation revision>
- **Outcome:** <pending/PASSED/ESCALATED/BLOCKED/not applicable>
- **Assured at:** <YYYY-MM-DD or pending>
- **Eligibility revalidation:** <Criterion-by-criterion result against actual changed and affected surfaces>
- **Scoped diff inspection:** <Acceptance/risk traceability and production/supporting path classification result>
- **Test integrity:** <Independent-oracle and test-change-classification result>
- **Commands reproduced:** <Focused, affected, scoped quality, and Task fuzz smoke commands/results or justified not-applicable items>
- **Escalation disposition:** <None, or trigger and standard next gate>

This section is authoritative only for `delivery_track: fast`; it never claims an independent `CLEAN` review or separate tester result.

## Review Summary

- **Revision reviewed:** <revision>
- **Implementation fingerprint reviewed:** <whole implementation fingerprint at review time>
- **Production fingerprint reviewed:** <production-surface fingerprint>
- **Outcome:** <pending/CLEAN/FINDINGS/BLOCKED>
- **Reviewed at:** <YYYY-MM-DD or pending>
- **Packet integrity:** <pass/fail and compact mismatch summary>
- **Acceptance traceability:** <Criterion-to-implementation/test evidence summary>
- **Protocol coverage:** <Scope/context, adversarial, architecture, contracts/data/security, test quality, verification-selection result>
- **Focused diagnostics:** <Commands and results, or —>
- **Production findings:** <None or compact outcome-affecting production-defect summary; canonical-only issues are excluded>
- **Non-production observations:** <None or separate advisory observations about tests or other supporting evidence; these do not prevent CLEAN or require another reviewer invocation>

## Test Summary

- **Revision tested:** <revision>
- **Implementation fingerprint tested:** <whole implementation fingerprint>
- **Production fingerprint:** <matching reviewed production fingerprint>
- **Outcome:** <pending/passed/failed/exception accepted>
- **Tested at:** <YYYY-MM-DD or pending>
- **Commands and results:** <Compact command/result list>
- **Selection rationale:** <Why the selected checks cover the actual affected surface>
- **Skipped or not-applicable checks:** <Rationale and risk, or —>
- **Accepted exception:** <User decision and risk, or —>

## User Validation

| Date | Scope | Result | Feedback and disposition |
| --- | --- | --- | --- |
| <YYYY-MM-DD> | <What the user checked> | <pending/accepted/changes requested> | <Compact notes> |

User-requested fixes before acceptance return this same Task to `IN PROGRESS`. New scope requires the Replan gate; an unrelated defect in previously accepted code is recorded in the Backlog Defect Queue after user confirmation.

## Iteration History

| Revision | Date | Trigger | Summary | Evidence invalidated |
| --- | --- | --- | --- | --- |
| 0 | <YYYY-MM-DD> | Task definition approved | <Initial scope> | — |

## User Acceptance

- **Decision:** <pending/accepted/changes requested>
- **Accepted by:** <User or role>
- **Accepted at:** <YYYY-MM-DD or pending>
- **Notes:** <Compact acceptance note>

Task Acceptance and permission to start the next Task are separate explicit gates.
