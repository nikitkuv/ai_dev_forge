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
external_sources: []
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

## Acceptance Criteria

- [ ] <Observable, objectively verifiable condition.>

## Verification Plan

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

- <Acceptance invariant, boundary, failure mode, compatibility concern, or risk that the independent reviewer must challenge.>

## Manual Verification

1. <Reproducible manual step and expected result.>

## References

- **Requirements:** <FR-/NFR-/BR-IDs>
- **Architecture:** <Section or component>
- **Decisions:** <ADR-IDs or —>
- **Epic plan:** <Relative path to plan.md>
- **Related defects:** <BUG-IDs or —>
- **External sources:** <Provider-neutral work-source keys from `external_sources`, or —>

## Workflow State

Lifecycle values and transitions are defined only in `.ai/framework/contracts.yaml`. `status` in frontmatter is the sole lifecycle status for this Task.

Set `status` to `IN REVIEW` only after implementation evidence and the Review Packet are current, to `IN TESTING` only after a protocol-complete `CLEAN` review, and to `AWAITING USER ACCEPTANCE` only after selected Task testing passes. Code changes return the Task to `IN PROGRESS` and invalidate older review and testing evidence.

```yaml
current_gate: task_start
implementation_revision: 0
current_fingerprint:
review_packet:
  base_fingerprint:
  implementation_revision:
  implementation_fingerprint:
  diff_fingerprint:
  changed_paths: []
  code_review_paths: []
review:
  revision:
  fingerprint:
  outcome:
  completed_at:
testing:
  revision:
  fingerprint:
  outcome:
  completed_at:
```

Use a reproducible Git commit, tree, or scoped diff hash as the fingerprint. Review and testing evidence is current only when both its revision and fingerprint equal the implementation values.

## Implementation Summary

- **Base revision:** <Base commit, tree, or reproducible fingerprint>
- **Revision:** <implementation revision>
- **Fingerprint:** <Git commit, tree, or scoped diff hash>
- **Files changed:** <Compact list>
- **Affected-surface or risk changes:** <None, or correction to the approved plan>
- **Behavior delivered:** <Compact summary>
- **Tests added or changed:** <Compact summary>
- **RED/GREEN evidence:** <Commands and expected RED/GREEN results, or allowed not-applicable rationale>
- **Selected checks:** <Focused, affected, and scoped command/result summary>
- **Early full-suite authorization:** <Explicit user request and result, or —>
- **Known limitations:** <None or compact list>

Do not paste full agent responses or long tool logs.

## Review Summary

- **Revision reviewed:** <revision>
- **Fingerprint reviewed:** <fingerprint>
- **Outcome:** <pending/CLEAN/FINDINGS/BLOCKED>
- **Reviewed at:** <YYYY-MM-DD or pending>
- **Packet integrity:** <pass/fail and compact mismatch summary>
- **Acceptance traceability:** <Criterion-to-implementation/test evidence summary>
- **Protocol coverage:** <Scope/context, adversarial, architecture, contracts/data/security, test quality, verification-selection result>
- **Focused diagnostics:** <Commands and results, or —>
- **Findings:** <None or compact actionable code-review summary; canonical-only issues are handled by the orchestrator and excluded>

## Test Summary

- **Revision tested:** <revision>
- **Fingerprint tested:** <fingerprint>
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
