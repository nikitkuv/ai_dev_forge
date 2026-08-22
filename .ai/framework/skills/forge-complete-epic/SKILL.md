---
name: forge-complete-epic
description: Complete a Forge Epic after its final TASK is accepted by running mandatory Epic Validation and fuzzing, handling failures through new TASK work, and requesting the separate Epic Acceptance gate.
---

# Complete an Epic

## Enter Epic Validation

1. Verify every planned TASK is `DONE`; every accepted implementation has current structured review and selected Task-testing evidence; requirement coverage is complete; any work-source coverage matrix has no unexplained gaps or contradictory reverse mappings; and the approved Epic Verification Plan contains evidenced commands or explicit blockers.
2. Establish one reproducible aggregate commit, tree, or scoped-diff fingerprint covering the Epic implementation and accepted Task evidence.
3. Transition the Epic from `ACTIVE` to `VALIDATING` in `BACKLOG.md`.
4. Invoke `epic-validator` automatically for the exact fingerprint. No extra confirmation is required because the role makes no source changes.
5. Require the configured full project test suite; project-wide lint, typecheck and build or package checks; cross-component integration and end-to-end checks; requirement and critical-path coverage; and applicable quality-profile gates.
6. Record the compact reproducible Epic Validation Summary in `plan.md`; never create a separate validation report.

## Handle Epic Validation outcome

- `PASSED`: transition from `VALIDATING` to `FUZZING`.
- `PASSED WITH ACCEPTED EXCEPTIONS`: require the user's explicit acceptance of every exact exception and recorded risk, then transition to `FUZZING`.
- `FAILED`: preserve commands and failure evidence, transition back to `ACTIVE`, show a Replan diff for remediation work, obtain Replan approval and a separate Task Start authorization, run the full Task lifecycle, then repeat Epic Validation.
- `BLOCKED`: record the exact missing capability, configuration, service, dataset, environment or authorization and its risk; transition back to `ACTIVE` and obtain Replan or user direction. Never reinterpret a blocker as a passing result.

Any implementation change invalidates prior Task review/testing evidence where affected, the entire Epic Validation result, and prior fuzzing evidence. The Epic cannot enter `FUZZING` without current passing Epic Validation evidence.

## Enter fuzzing

1. Confirm the Epic is `FUZZING` and the current aggregate fingerprint exactly matches passing Epic Validation evidence.
2. Invoke `fuzzer` automatically for existing local harnesses. No extra confirmation is required because the role makes no source changes.
3. Record the reproducible fuzzing summary in the Epic plan; never create a separate fuzzing report.

## Handle the outcome

- `PASSED`: transition to `AWAITING EPIC ACCEPTANCE`.
- `NOT APPLICABLE`: require both a rationale for no suitable target and alternative risk coverage, then transition to `AWAITING EPIC ACCEPTANCE`.
- `HARNESS REQUIRED`: transition back to `ACTIVE`; show a Replan diff for a new harness TASK, obtain Replan approval and a separate Task Start authorization, run its full lifecycle, then repeat Epic Validation before re-entering `FUZZING`.
- `FINDINGS`: preserve reproduction evidence, transition back to `ACTIVE`, show remediation TASK changes through Replan, require separate Task Start, full implementation, review, selected Task testing, and Task Acceptance, then repeat Epic Validation and fuzzing.

Any code change invalidates the prior Epic Validation and fuzzing results. Repeat both after every harness or remediation change.

## Run Epic user validation

When fuzzing permits progression:

1. record the Epic-level validation scope and result in `plan.md`;
2. present the outcome, acceptance criteria, Epic Validation evidence, quality-profile gates, fuzzing evidence, accepted exceptions, and known limitations;
3. request explicit **Epic Acceptance**.

If the user finds a problem, return the Epic to `ACTIVE`, propose a Replan diff, create a new TASK only after approval, run the full TASK lifecycle, and repeat Epic Validation and fuzzing.

## Complete atomically

After explicit Epic Acceptance:

1. transition the Epic to `COMPLETED` in `BACKLOG.md`;
2. record acceptance in `plan.md`;
3. move its directory from `execution/active/` to `execution/completed/`;
4. validate Backlog and directory state as one logical transition and roll back partial changes on failure.

Preserve external source identities and canonical mappings throughout completion. Do not move, edit, comment on, or close an external item; bidirectional write-back requires a separate capability and explicit authorization.

Do not activate the next Epic automatically. Report queued `execution/planned/` candidates in Backlog order, identify the first eligible one and its blockers, and wait for its separate Epic Start gate. An unprepared `PLANNED + READY` Epic requires Plan Approval before Epic Start.
