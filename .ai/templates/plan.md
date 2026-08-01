---
document_type: epic_plan
document_status: draft
language: "<language-code>"
epic_id: EPIC-NNN
created_at: "<YYYY-MM-DD>"
approved_at:
---

# EPIC-NNN — <Epic Name> — Execution Plan

## Document Contract

This plan is the single source of truth for the Epic strategy, ordered Task sequence, acceptance criteria, quality gates, fuzzing summary, and Epic-level user-validation history.

Lifecycle state for each individual work item belongs only in its corresponding TASK file.

Epic priority, readiness, blocking metadata and lifecycle status belong only in `BACKLOG.md`.

## Epic Objective

<State the single product or system objective of this Epic.>

## Expected Outcome

<Describe the observable result after the Epic is accepted.>

## Dependencies

| Dependency | Type | Why required | Resolution condition |
| --- | --- | --- | --- |
| <EPIC-/ADR-/external dependency> | <product/architecture/external> | <Reason> | <Condition> |

## Risks

| Risk | Likelihood and impact | Mitigation | Trigger or owner |
| --- | --- | --- | --- |
| <Risk> | <Assessment> | <Mitigation> | <Signal or owner> |

## Implementation Strategy

<Describe the high-level delivery approach, boundaries, sequencing rationale, and relevant architecture. Do not include line-by-line coding instructions or execution state.>

## Ordered Task Sequence

| Order | Task | Intended outcome | Depends on |
| --- | --- | --- | --- |
| 1 | TASK-NNN — <Title> | <One independently verifiable outcome> | — |
| 2 | TASK-NNN — <Title> | <One independently verifiable outcome> | TASK-NNN |

Changing Task scope, order, or composition after plan approval requires the Replan gate defined in `.ai/framework/contracts.yaml`.

## Epic Acceptance Criteria

- [ ] <Observable criterion linked to requirements.>

## Mandatory Quality Gates

- [ ] Every Task completed its implementation, independent review, full testing, and explicit Task Acceptance gates.
- [ ] Configured lint, typecheck, build, and project-wide test commands passed, or an explicitly accepted exception records the risk.
- [ ] Requirement, architecture, ADR, Backlog, plan, and Task references are consistent.
- [ ] Epic fuzzing produced an accepted outcome under `.ai/framework/contracts.yaml`.
- [ ] Epic-level manual validation is recorded below.

## Fuzzing Summary

- **Outcome:**
- **Targets and harnesses:** <Targets exercised and harness identifiers.>
- **Tools, seeds, and budgets:** <Reproducible configuration.>
- **Crashing inputs and reproduction:** <Stored locations and reproduction result, or —.>
- **Findings and disposition:** <Compact summary and linked remediation Tasks, or —.>
- **Not-applicable rationale:** <Why no suitable target exists, or —.>
- **Alternative risk coverage:** <Required when outcome is NOT APPLICABLE, otherwise —.>
- **Last run:** <YYYY-MM-DD or pending>

## Epic User Validation History

| Date | Validator | Scope | Result | Feedback or follow-up |
| --- | --- | --- | --- | --- |
| <YYYY-MM-DD> | <User or role> | <What was validated> | <pending/accepted/changes requested> | <Compact notes or TASK reference> |
