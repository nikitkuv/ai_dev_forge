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

## Acceptance Criteria

- [ ] <Observable, objectively verifiable condition.>

## Required Tests

- **Approach:** <TDD by default for bug fixes and meaningful business logic, or a recorded reason why it is not applicable.>
- **Task-specific tests:** <Tests that prove this Task.>
- **Affected-component tests:** <Related suites.>
- **Full-suite command:** <Project-wide test command.>
- **Additional checks:** <Lint, typecheck, build, security, performance, or other configured checks.>

## Manual Verification

1. <Reproducible manual step and expected result.>

## References

- **Requirements:** <FR-/NFR-/BR-IDs>
- **Architecture:** <Section or component>
- **Decisions:** <ADR-IDs or —>
- **Epic plan:** <Relative path to plan.md>
- **Related defects:** <BUG-IDs or —>

## Workflow State

Lifecycle values and transitions are defined only in `.ai/framework/contracts.yaml`. `status` in frontmatter is the sole lifecycle status for this Task.

Set `status` to `IN REVIEW` only after implementation evidence is current, to `IN TESTING` only after review approval, and to `AWAITING USER ACCEPTANCE` only after required testing passes. Code changes return the Task to `IN PROGRESS` and invalidate older review and testing evidence.

```yaml
current_gate: task_start
implementation_revision: 0
current_fingerprint:
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

- **Revision:** <implementation revision>
- **Fingerprint:** <Git commit, tree, or scoped diff hash>
- **Files changed:** <Compact list>
- **Behavior delivered:** <Compact summary>
- **Tests added or changed:** <Compact summary>
- **Known limitations:** <None or compact list>

Do not paste full agent responses or long tool logs.

## Review Summary

- **Revision reviewed:** <revision>
- **Fingerprint reviewed:** <fingerprint>
- **Outcome:** <pending/approved/changes requested>
- **Reviewed at:** <YYYY-MM-DD or pending>
- **Findings:** <None or compact actionable summary>

## Test Summary

- **Revision tested:** <revision>
- **Fingerprint tested:** <fingerprint>
- **Outcome:** <pending/passed/failed/exception accepted>
- **Tested at:** <YYYY-MM-DD or pending>
- **Commands and results:** <Compact command/result list>
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
