---
name: forge-complete-task
description: Record explicit user acceptance for a verified Forge TASK, close any linked scheduled Bug when appropriate, and apply the configured Git policy. Use when a TASK is awaiting user acceptance and must become DONE without automatically starting the next TASK.
---

# Complete a TASK

## Verify acceptance eligibility

1. Require lifecycle `status: AWAITING USER ACCEPTANCE`.
2. Confirm testing matches the current implementation revision and whole-implementation fingerprint, and confirm its production fingerprint matches current clean production-review evidence. A clean review may belong to an earlier implementation revision only when every intervening change was supporting-only and the production fingerprint stayed unchanged.
3. Confirm the recorded test evidence contains exact commands, selection rationale, and current results for focused, affected-component, and scoped quality checks, or an explicitly accepted Task-level exception with its risk.
4. Confirm Review Packet integrity, acceptance traceability and protocol coverage are current, and required manual verification was presented.
5. Ask for explicit Task Acceptance. Verification evidence proves eligibility for acceptance; it never constitutes acceptance. Do not infer acceptance from passing checks or positive feedback that does not clearly accept the TASK.

If the user requests changes, record the feedback and return the TASK to `IN PROGRESS`. Repeat strong review plus selected testing after a production change; after a supporting-only change, preserve a matching clean production review and repeat selected testing without another reviewer invocation.

## Record completion

After explicit acceptance:

1. record the user decision, accepting user or role, date, notes, and final revision/fingerprint in the TASK's User Acceptance and Iteration History;
2. transition only that TASK to `DONE`;
3. if the accepted TASK is the approved repair for a `SCHEDULED` Bug, transition that Bug to `RESOLVED`;
4. leave unrelated Bugs unchanged;
5. verify plan order and remaining TASK dependencies without copying TASK status into the plan.
6. preserve `external_sources` and reverse mappings unchanged; Task Acceptance does not mutate or close an external item and does not make the external system authoritative.

## Apply Git policy

Read `git.policy` from `.ai/project.yaml`.

The commit gate follows Task Acceptance; it never precedes or constitutes user acceptance. Do not commit the TASK while it is awaiting acceptance.

- `manual`: after explicit Task Acceptance and transition to `DONE`, show the exact scoped files and proposed commit message, then wait for separate explicit commit authorization.
- `auto_commit_after_acceptance`: commit only the accepted TASK's scoped changes after clean structured review, selected Task testing or an accepted exception, explicit Task Acceptance, and transition to `DONE`.

Never include unrelated user changes in the commit.

## Preserve the next gate

Task Acceptance and permission to start the next TASK are separate decisions. Do not start, delegate, or transition the next TASK unless the user explicitly authorizes its Task Start gate, even when the same message accepted the previous TASK.

If accepted work was the final TASK in the Epic, hand control to `forge-complete-epic` for automatic Epic Validation followed by the fuzzing gate; the fuzzer is invoked only for planned `applicable`, `unresolved`, or contradictory final evidence. Otherwise report the next eligible TASK and ask whether the user wants to start it.
