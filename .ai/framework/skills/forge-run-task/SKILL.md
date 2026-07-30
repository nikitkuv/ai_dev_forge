---
name: forge-run-task
description: Execute one approved Forge TASK through implementation, independent review, testing, and handoff for manual user acceptance. Use only after the user authorizes that TASK's separate Task Start gate.
---

# Run One TASK

## Start the TASK

1. Require `definition_status: approved`, lifecycle `status: TODO`, satisfied dependencies, no unresolved blocker, and no other code-writing TASK in progress.
2. Show the TASK goal, scope, acceptance criteria, tests, and constraints.
3. Obtain explicit Task Start authorization.
4. Let only the orchestrator transition the TASK to `IN PROGRESS`, record the gate, and establish the next implementation revision.

## Run the implementation-review-test loop

1. Invoke `implementer` for this TASK only. Require production changes and necessary tests; use TDD by default for bug fixes and meaningful business logic, with a recorded rationale when not applicable.
2. Record a compact Implementation Summary, incremented revision, and reproducible fingerprint in the TASK.
3. Transition to `IN REVIEW` and invoke the strong read-only `reviewer` for the exact revision and fingerprint.
4. If review finds anything actionable:
   - let the orchestrator return the TASK to `IN PROGRESS`;
   - route findings to `implementer`;
   - invalidate prior review and testing evidence;
   - record the new revision/fingerprint after fixes;
   - repeat independent review.
5. After a clean review, transition to `IN TESTING` and invoke `tester`.
6. Require tests added or changed by the TASK, affected-component tests, the full test suite, and configured lint, typecheck, and build checks.
7. If testing fails or coverage is missing, route evidence through the orchestrator to `implementer`, then repeat review and all required testing after any code change.

The tester never writes tests or fixes code. The reviewer and tester report only to the orchestrator. Agents never invoke one another.

## Handle execution limits

Require the full test suite for every TASK. If local execution is objectively impossible, explain the exact missing capability and risk, then obtain explicit user acceptance of the exception. Do not silently skip or weaken checks.

Optional Superpowers may assist only when enabled in `.ai/project.yaml`; their absence must not block this core loop.

## Hand off to the user

After current review and testing evidence passes:

1. transition the TASK to `AWAITING USER ACCEPTANCE`;
2. record compact review and test summaries in the TASK;
3. report the delivered behavior, verification evidence, limitations, and manual steps;
4. wait without timeout for user validation.

User-requested fixes return this same TASK to `IN PROGRESS`, invalidate stale evidence, and repeat the loop. New scope requires Replan. Do not mark the TASK `DONE`, commit, or start the next TASK in this skill.
