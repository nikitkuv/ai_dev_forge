---
name: forge-complete-task
description: Record explicit user acceptance for a verified Forge TASK, close any linked scheduled Bug when appropriate, and apply the configured Git policy. Use when a TASK is awaiting user acceptance and must become DONE without automatically starting the next TASK.
---

# Complete a TASK

## Verify acceptance eligibility

1. Require lifecycle `status: AWAITING USER ACCEPTANCE`.
2. Resolve the recorded delivery track, treating a legacy TASK without the field as `standard`.
3. For `fast`, require a current `PASSED` Fast Assurance Summary whose assurance fingerprint exactly matches the current whole implementation; confirm eligibility was revalidated against the actual surface and the orchestrator executed or reproduced every selected check. Stale, incomplete, failed, or disqualified fast evidence is ineligible for acceptance and escalates to standard.
4. For `standard`, confirm testing matches the current implementation revision and whole-implementation fingerprint, and confirm its production fingerprint matches current clean production-review evidence. A clean review may belong to an earlier implementation revision only when every intervening change was supporting-only and the production fingerprint stayed unchanged.
5. Confirm the track-specific evidence contains exact commands, selection rationale, and current results for focused, affected-component, and scoped quality checks, or an explicitly accepted Task-level exception with its risk. For standard also confirm Review Packet integrity, acceptance traceability and protocol coverage; for fast confirm diff inspection, test integrity and eligibility traceability. Confirm required manual verification was presented for both tracks.
6. Ask for explicit Task Acceptance. Verification evidence proves eligibility for explicit Task Acceptance; it never constitutes acceptance. Do not infer acceptance from passing checks or positive feedback that does not clearly accept the TASK.

If the user requests changes, record the feedback and return the TASK to `IN PROGRESS`. For standard, repeat strong review plus selected testing after a production change; after a supporting-only change, preserve a matching clean production review and repeat selected testing without another reviewer invocation. For fast, invalidate assurance after any implementation change, repeat the entire fast procedure, and escalate to standard on any eligibility or verification failure. Standard to fast is forbidden after Task Start.

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
- `auto_commit_after_acceptance`: commit only the accepted TASK's scoped changes after current track-specific evidence (passing fast assurance or clean standard review plus selected testing, including any accepted exception), explicit Task Acceptance, and transition to `DONE`.

Never include unrelated user changes in the commit.

## Preserve the next gate

Task Acceptance and permission to start the next TASK are separate decisions. Do not start, delegate, or transition the next TASK unless the user explicitly authorizes its Task Start gate, even when the same message accepted the previous TASK.

If accepted work was the final TASK in the Epic, hand control to `forge-complete-epic` for automatic Epic Validation followed by the fuzzing gate; the fuzzer is invoked only for planned `applicable`, `unresolved`, or contradictory final evidence. Otherwise report the next eligible TASK and ask whether the user wants to start it.
