---
name: forge-complete-epic
description: Complete a Forge Epic after its final TASK is accepted by running mandatory Epic fuzzing, handling harnesses or findings through new TASK work, and requesting the separate Epic Acceptance gate.
---

# Complete an Epic

## Enter fuzzing

1. Verify every planned TASK is `DONE`, all accepted changes have current review and testing evidence, and Epic acceptance criteria are ready for validation.
2. Transition the Epic from `ACTIVE` to `FUZZING` in `BACKLOG.md`.
3. Invoke `fuzzer` automatically for existing local harnesses. No extra confirmation is required because the role makes no source changes.
4. Record the reproducible fuzzing summary in the Epic plan; never create a separate fuzzing report.

## Handle the outcome

- `PASSED`: transition to `AWAITING EPIC ACCEPTANCE`.
- `NOT APPLICABLE`: require both a rationale for no suitable target and alternative risk coverage, then transition to `AWAITING EPIC ACCEPTANCE`.
- `HARNESS REQUIRED`: transition back to `ACTIVE`; show a Replan diff for a new harness TASK, obtain Replan approval and a separate Task Start authorization, run its full lifecycle, then re-enter `FUZZING`.
- `FINDINGS`: preserve reproduction evidence, transition back to `ACTIVE`, show remediation TASK changes through Replan, require separate Task Start, full implementation, review, testing, and Task Acceptance, then rerun Epic fuzzing.

Any code change invalidates the prior fuzzing result. Repeat fuzzing after every harness or remediation change.

## Run Epic user validation

When fuzzing permits progression:

1. record the Epic-level validation scope and result in `plan.md`;
2. present the outcome, acceptance criteria, quality gates, fuzzing evidence, and known limitations;
3. request explicit **Epic Acceptance**.

If the user finds a problem, return the Epic to `ACTIVE`, propose a Replan diff, create a new TASK only after approval, run the full TASK lifecycle, and repeat fuzzing.

## Complete atomically

After explicit Epic Acceptance:

1. transition the Epic to `COMPLETED` in `BACKLOG.md`;
2. record acceptance in `plan.md`;
3. move its directory from `execution/active/` to `execution/completed/`;
4. validate Backlog and directory state as one logical transition and roll back partial changes on failure.

Do not activate the next Epic automatically. Report the next planned candidate and wait for a separate Epic Start gate.
