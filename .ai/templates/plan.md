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

This plan is the single source of truth for the Epic strategy, ordered Task sequence, acceptance criteria, requirement coverage, quality profiles, Epic verification plan, Epic Validation evidence, fuzzing summary, and Epic-level user-validation history.

Lifecycle state for each individual work item belongs only in its corresponding TASK file.

Epic priority, readiness, blocking metadata and lifecycle status belong only in `BACKLOG.md`.

External work-source relationships are traceability metadata only. They never own lifecycle state or approval.

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

## Requirement Coverage

| Requirement or invariant | Planned Task evidence | Epic-level evidence |
| --- | --- | --- |
| <FR-/NFR-/BR-ID> | <TASK-NNN acceptance criterion or check> | <Cross-component, regression, manual, or profile-specific check> |

## External Source Coverage

| Source key | Source intent covered by this Epic | Planned TASK coverage | Disposition or gap |
| --- | --- | --- | --- |
| <integration-id:external-id or —> | <Source slice retained in this Epic> | <TASK-NNN list or pending until plan approval> | <covered/deferred/duplicate/unresolved> |

Use this matrix only for configured `work_source` integrations. For an Epic with no external work source, keep one `—` row. Every source in the Backlog Epic must be covered, explicitly deferred, or identified as unresolved; one source may map to several TASKs and one TASK may cover several sources.

## Quality Profiles and Risk Strategy

- **Selected profiles:** <One or more of backend, frontend, ml, data_pipeline, infrastructure, library_cli.>
- **Critical user or system paths:** <Paths that require Epic-level integration or end-to-end evidence.>
- **Cross-cutting risk flags:** <Public contract, authorization, persistence, migration, concurrency, shared core, dependency/build, data/ML, operations, or other risks.>
- **Profile-specific gates:** <Applicable checks from `.ai/framework/contracts.yaml`, plus project-specific checks.>

## Ordered Task Sequence

### Task Delivery Tracks

Every TASK records exactly one delivery track independently from model tier and risk level. For each proposed `fast` TASK, record criterion-by-criterion evidence for bounded scope, reversibility, low risk, unambiguous expected behavior, deterministic focused verification, and the absence of every framework disqualifier. Missing, uncertain, or contradictory evidence selects `standard`. Record the selected track and rationale beside each Task in the ordered sequence or directly below its row.

| Order | Task | Intended outcome | Depends on |
| --- | --- | --- | --- |
| 1 | TASK-NNN — <Title> | <One independently verifiable outcome> | — |
| 2 | TASK-NNN — <Title> | <One independently verifiable outcome> | TASK-NNN |

Changing Task scope, order, composition, or weakening its approved delivery track before Task Start requires the Replan gate defined in `.ai/framework/contracts.yaml`. Fast-to-standard safety escalation with unchanged scope does not.

## Epic Acceptance Criteria

- [ ] <Observable criterion linked to requirements.>

## Epic Verification Plan

- **Full test suite:** <Exact project-wide command or unresolved blocker. Run only during Epic Validation by default.>
- **Project-wide lint:** <Exact command, not applicable rationale, or unresolved blocker.>
- **Project-wide typecheck:** <Exact command, not applicable rationale, or unresolved blocker.>
- **Project-wide build/package:** <Exact command, not applicable rationale, or unresolved blocker.>
- **Integration and end-to-end:** <Commands or reproducible procedures for critical paths.>
- **Profile-specific validation:** <Performance, accessibility, migrations, ML evaluation, infrastructure plan, compatibility, or other selected-profile checks.>
- **Execution constraints:** <Environment, services, datasets, credentials, resource budgets, or explicit limitations.>

## Epic Fuzzing Plan

- **Applicability:** <applicable/not applicable/unresolved>.
- **Risk surfaces:** <Parsers, protocol or API boundaries, serializers, validators, state machines, public inputs, or none.>
- **Targets and invariants:** <Target-to-property mapping, or explicit unresolved evidence.>
- **Harness readiness and Task ownership:** <Existing harness identifiers; missing harness mapped to TASK-NNN; or not applicable.>
- **Task-level fuzz smoke:** <TASK-NNN to target, command, and bounded budget mapping; or not applicable rationale.>
- **Epic campaign:** <Tools, commands, corpus, deterministic seeds, time and resource budgets; or unresolved blocker.>
- **Failure criteria:** <Crash, hang, timeout, sanitizer finding, invariant violation, security-relevant behavior, or other objective outcome.>
- **Artifact handling:** <Corpus, crashing-input, log, and reproduction locations or retention constraints.>
- **Execution constraints:** <Environment, platform, service, credential, safety, or resource limitations.>
- **Not-applicable rationale:** <Why no suitable fuzzable boundary exists; required for `not applicable`, otherwise —.>
- **Alternative risk coverage:** <Checks covering the relevant robustness risk; required for `not applicable`, otherwise —.>

`not applicable` is a planning assessment, not a standalone waiver. After passing Epic Validation, the orchestrator may record `NOT APPLICABLE` without invoking the fuzzer only when final Task fuzzing-impact evidence, actual affected surfaces, alternative-coverage results, and the current aggregate fingerprint still match this approved plan. `applicable`, `unresolved`, or contradictory evidence requires the fuzzer.

## Mandatory Quality Gates

- [ ] Every Task completed implementation, its track-specific assurance (`fast` orchestrator assurance or `standard` independent review plus tester verification), and explicit Task Acceptance gates.
- [ ] Requirement-to-Task and Epic-level evidence coverage is complete.
- [ ] Epic Validation ran the full project test suite and project-wide lint, typecheck, build, integration, and end-to-end commands applicable to this project on the current fingerprint.
- [ ] Selected quality-profile gates passed, were objectively not applicable, or have an explicitly accepted exception with recorded risk.
- [ ] Requirement, architecture, ADR, Backlog, plan, and Task references are consistent.
- [ ] Epic fuzzing produced an accepted outcome under `.ai/framework/contracts.yaml`.
- [ ] Epic-level manual validation is recorded below.

## Epic Validation Summary

- **Revision or tree:** <Git commit, tree, or reproducible aggregate fingerprint.>
- **Outcome:** <pending/PASSED/PASSED WITH ACCEPTED EXCEPTIONS/FAILED/BLOCKED>
- **Validated at:** <YYYY-MM-DD or pending>
- **Full-suite commands and results:** <Compact command/result list.>
- **Project-wide checks and results:** <Compact lint/typecheck/build/integration/E2E/profile result list.>
- **Requirement and critical-path coverage:** <Compact evidence summary.>
- **Skipped or not-applicable checks:** <Rationale and risk, or —.>
- **Accepted exceptions:** <User decision and risk, or —.>

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
