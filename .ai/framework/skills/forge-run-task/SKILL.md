---
name: forge-run-task
description: Execute one approved Forge TASK through implementation, independent review, testing, and handoff for manual user acceptance. Use only after the user authorizes that TASK's separate Task Start gate.
---

# Run One TASK

## Start the TASK

1. Require `definition_status: approved`, lifecycle `status: TODO`, satisfied dependencies, no unresolved blocker, and no other code-writing TASK in progress.
2. Show the TASK goal, scope, acceptance criteria, affected surface, risk flags, Verification Plan, review focus, constraints, and any `external_sources` with their source intent. Do not require connector access for an unlinked TASK.
3. Obtain explicit Task Start authorization.
4. Let only the orchestrator transition the TASK to `IN PROGRESS`, record the gate, and establish the next implementation revision.

## Run the implementation-review-test loop

1. Invoke `implementer` for this TASK only. Require production changes and necessary tests.
2. For each bug fix or meaningful business behavior, require this test-driven cycle:
   - identify the smallest observable behavior required by an acceptance criterion;
   - add or adjust one focused test and run it to confirm an expected failure caused by the missing behavior, not by a test error;
   - implement the smallest in-scope production change that makes the focused test pass;
   - rerun the focused tests and selected affected checks;
   - refactor only while tests remain green, then repeat for the next behavior.
3. Documentation-only changes, generated artifacts, and simple configuration may record a concise TDD-not-applicable rationale instead. Exploration code is not completion evidence until the final implementation satisfies this contract.
4. Run applicable scoped quality checks. Do not require the full project suite or unscoped project-wide checks; those belong to Epic Validation. An early full run requires the user's explicit request.
5. If the actual changed or affected surface exceeds the approved Verification Plan, correct the implementation scope or update the in-scope verification selection with an explicit rationale. Removing or weakening an approved check requires orchestrator disposition; changed Task scope still requires Replan.
6. Record a compact Implementation Summary, including base revision, affected-surface or risk changes, RED/GREEN evidence or the not-applicable rationale, selected command evidence, incremented revision, and reproducible fingerprint in the TASK.
7. Build a Review Packet containing:
   - TASK and Epic-plan paths;
   - base and implementation fingerprints and implementation revision;
   - code-review paths and a reproducible code-review diff limited to implementation code, tests, and code-owned artifacts;
   - acceptance criteria, affected components and contracts, risk level and flags, and review focus;
   - implementation summary, tests added or changed, RED/GREEN evidence, selected checks, and known limitations.
   - linked external source keys and the approved source intent covered by this TASK, when applicable.
   Exclude canonical documents, ADRs, Epic plans, TASK files, lifecycle metadata, and review-record edits from the code-review paths and diff. They remain reference inputs for interpreting the acceptance criteria. Before invocation, the orchestrator independently validates and, within its existing authority, corrects its canonical records.
8. Transition to `IN REVIEW`. Read `.ai/project.yaml`, require a valid `role_execution.mode`, and build one prompt from the complete neutral `.ai/framework/agents/reviewer.yaml` contract plus the exact Review Packet. Route it exactly as configured: `native_subagents` invokes the active platform's generated reviewer with no external preflight; `claude_with_codex` requires Claude Code and uses `.claude/forge/codex-role-runner.mjs`; `codex_with_claude` requires Codex and uses `.codex/forge/claude-role-runner.mjs` with `models.claude.strong.model` and effort. For either external route, run preflight, block on unavailability or active-orchestrator mismatch, pass the prompt through a secure temporary file, and always remove the file. All routes use the same code-only review boundary. There is no fallback before or after execution; a non-zero exit, timeout, permission failure, runtime mismatch, or malformed output blocks review.
9. If review finds anything actionable in the code-review surface:
   - let the orchestrator return the TASK to `IN PROGRESS`;
   - route findings to `implementer`;
   - invalidate prior review and testing evidence;
   - record the new revision/fingerprint after fixes;
   - repeat independent review.
   A canonical-only issue is out of contract: the orchestrator handles it, does not route it to the implementer, and does not return the TASK to `IN PROGRESS` or treat it as a non-clean code-review outcome.
10. After a clean, protocol-complete review, transition to `IN TESTING` and invoke `tester` for the exact reviewed revision, fingerprint, changed surface, Verification Plan, and review evidence.
11. Require tests added or changed by the TASK, selected affected-component tests, and configured scoped quality checks. Do not require the full project suite or unscoped project-wide checks.
12. If testing fails, coverage or selection is missing, or the plan is stale, route evidence through the orchestrator to `implementer`, then repeat structured review and selected testing after any code change.

The tester never writes tests or fixes code. The reviewer and tester report only to the orchestrator. Agents never invoke one another.

## Handle execution limits and full-suite requests

The full project suite is not a Task gate. It runs during Epic Validation after all planned Tasks are DONE. If the user explicitly requests an early full run, record the authorization, exact command and result; that result is supplementary and does not replace the later fingerprint-bound Epic Validation.

If a required selected Task check is objectively impossible, explain the exact missing capability and risk, then obtain explicit user acceptance of the Task-level exception. Do not silently skip, substitute, remove, or weaken checks.

## Hand off to the user

After current review and testing evidence passes:

1. confirm the tested revision and fingerprint exactly match the clean reviewed revision; stale or mismatched evidence must be invalidated and rerun;
2. transition the TASK to `AWAITING USER ACCEPTANCE`;
3. record compact review and test summaries in the TASK, including Review Packet integrity, acceptance traceability, protocol coverage, exact selected commands, exit results, skipped checks, selection rationale, and accepted execution exceptions;
4. report the delivered behavior, verification evidence, limitations, and manual steps;
5. wait without timeout for user validation.

User-requested fixes return this same TASK to `IN PROGRESS`, invalidate stale evidence, and repeat the loop. New scope requires Replan. Do not mark the TASK `DONE`, commit, or start the next TASK in this skill.
