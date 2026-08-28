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
   - derive the expected outcome independently from acceptance criteria, public contracts, domain invariants, approved examples, or a simpler independent oracle; never use output captured from the current implementation as the expectation;
   - identify the smallest observable behavior required by an acceptance criterion;
   - add or adjust one focused test and run it to confirm an expected failure caused by the missing behavior, not by a test error;
   - implement the smallest in-scope production change that makes the focused test pass;
   - rerun the focused tests and selected affected checks;
   - refactor only while tests remain green, then repeat for the next behavior.
3. Documentation-only changes, generated artifacts, and simple configuration may record a concise TDD-not-applicable rationale instead. Exploration code is not completion evidence until the final implementation satisfies this contract.
4. Require test integrity, not test count alone. Within scope, trace every acceptance criterion and affected risk to the strongest practical behavioral evidence, including applicable normal, boundary, invalid-input, error/recovery, state-transition and side-effect cases. Tests must execute real production logic through the lowest stable public boundary, mock only true external or nondeterministic dependencies, never mock the subject under test or its decision logic, and contain assertions that fail for plausible wrong implementations. Reject tests that mirror production algorithms, test mocks or private call structure instead of behavior, assert only execution or non-null output, or accept self-generated snapshots as an oracle.
5. A production edit does not by itself authorize a test edit. Classify each changed test, fixture, snapshot, golden file, baseline or metric as a behavior-contract change, demonstrably defective-test correction, or coverage extension, and record the independent source of the new expectation. Any removed case, weaker assertion, broader tolerance, new skip, or increased mocking requires explicit orchestrator disposition. If the approved contract is unchanged, require production code to be fixed instead of adapting the test.
6. Run applicable scoped quality checks and the bounded `Task fuzz smoke` when the actual fuzzing impact identifies an existing or new target or a completed harness. For impact `none`, verify the approved rationale still matches the actual changed and affected surfaces. Do not require the full project suite or unscoped project-wide checks; those belong to Epic Validation. An early full run requires the user's explicit request.
7. If the actual changed or affected surface exceeds the approved Verification Plan, correct the implementation scope or update the in-scope verification selection with an explicit rationale. Removing or weakening an approved check requires orchestrator disposition; changed Task scope still requires Replan.
8. Record a compact Implementation Summary, including base revision, affected-surface or risk changes, acceptance/risk-to-test traceability, independent test oracles, test-change classifications, RED/GREEN evidence or the not-applicable rationale, selected command evidence, incremented revision, reproducible whole-implementation fingerprint, and reproducible production-surface fingerprint in the TASK. Classify every review-relevant changed path by production effect:
   - `production_review_paths` contains executable production code and runtime configuration, schemas, migrations, generated runtime assets, packaging, production build, or deployment artifacts whose contents can change shipped behavior;
   - `supporting_evidence_paths` contains tests, fixtures, snapshots, golden files, test-only configuration, development tooling, examples, and other files that cannot change shipped behavior;
   - record a rationale for every ambiguous path. Canonical and lifecycle records remain context only and belong to neither list.
9. Build a Review Packet containing:
   - TASK and Epic-plan paths;
   - base and whole-implementation fingerprints, production-surface fingerprint, and implementation revision;
   - production review paths, supporting evidence paths, ambiguous-path classification rationale, and reproducible diffs for both surfaces;
   - acceptance criteria, affected components and contracts, risk level and flags, and review focus;
   - implementation summary, acceptance/risk-to-test traceability, independent test oracles, test-change classifications, tests added or changed, RED/GREEN evidence, selected checks, and known limitations.
   - linked external source keys and the approved source intent covered by this TASK, when applicable.
   Exclude canonical documents, ADRs, Epic plans, TASK files, lifecycle metadata, and review-record edits from both path lists and diffs. They remain reference inputs for interpreting the acceptance criteria. Before invocation, the orchestrator independently validates and, within its existing authority, corrects its canonical records.
10. Transition to `IN REVIEW` and determine review freshness from the production fingerprint:
   - if no prior clean review has the same production fingerprint, or legacy evidence lacks a production fingerprint, read `.ai/project.yaml`, require a valid `role_execution.mode`, and build one prompt from the complete neutral `.ai/framework/agents/reviewer.yaml` contract plus the exact Review Packet. Route it exactly as configured: `native_subagents` invokes the active platform's generated reviewer with no external preflight; `claude_with_codex` requires Claude Code and uses `.claude/forge/codex-role-runner.mjs`; `codex_with_claude` requires Codex and uses `.codex/forge/claude-role-runner.mjs` with `models.claude.strong.model` and effort. For either external route, run preflight, block on unavailability or active-orchestrator mismatch, pass the prompt through a secure temporary file, and always remove the file. All routes use the same production-only blocking boundary. There is no fallback before or after execution; a non-zero exit, timeout, permission failure, runtime mismatch, packet-integrity failure, or malformed output blocks review;
   - if a protocol-complete `CLEAN` review has the same production fingerprint and packet integrity remains complete, preserve that review, record the current implementation revision as a supporting-only continuation, and do not invoke the strong reviewer. A changed whole-implementation fingerprint alone never invalidates clean production review.
11. If review finds any production finding in a production review path:
   - let the orchestrator return the TASK to `IN PROGRESS`;
   - route only production findings to `implementer`;
   - invalidate prior review and testing evidence;
   - record both new fingerprints after fixes;
   - repeat independent review because the production fingerprint changed.
   A defect confined to tests or another supporting evidence path is a non-production observation: record it separately, preserve `CLEAN`, do not return the TASK to `IN PROGRESS`, and do not invoke the reviewer again for its correction. A supporting artifact may justify a production finding only when the finding identifies a concrete failure and exact location in a production review path. A canonical-only issue remains out of contract and is handled by the orchestrator without affecting review.
12. After a new or preserved clean, protocol-complete production review, transition to `IN TESTING` and invoke `tester` for the current implementation revision and whole-implementation fingerprint, the matching reviewed production fingerprint, both classified surfaces, the Verification Plan, test-integrity evidence, review evidence, and all non-production observations.
13. Require tests added or changed by the TASK, selected affected-component tests, the applicable bounded Task fuzz smoke, and configured scoped quality checks. Record the final fuzzing impact and smoke result or current not-applicable rationale. Do not require the full project suite or unscoped project-wide checks.
14. If testing fails, test integrity, coverage or selection is missing, or the plan is stale, route evidence through the orchestrator to `implementer` and return the TASK to `IN PROGRESS`. After remediation, recompute both fingerprints. If the production fingerprint changed, invalidate review and testing evidence and repeat strong review plus selected testing. If only supporting evidence changed, preserve the clean production review, invalidate affected testing evidence, pass through `IN REVIEW` without invoking the reviewer, and rerun selected testing directly.

The tester never writes tests or fixes code. The reviewer and tester report only to the orchestrator. Agents never invoke one another.

## Handle execution limits and full-suite requests

The full project suite is not a Task gate. It runs during Epic Validation after all planned Tasks are DONE. If the user explicitly requests an early full run, record the authorization, exact command and result; that result is supplementary and does not replace the later fingerprint-bound Epic Validation.

If a required selected Task check is objectively impossible, explain the exact missing capability and risk, then obtain explicit user acceptance of the Task-level exception. Do not silently skip, substitute, remove, or weaken checks.

## Hand off to the user

After current review and testing evidence passes:

1. confirm testing matches the current implementation revision and whole-implementation fingerprint, and its production fingerprint exactly matches the new or preserved clean review; a whole-implementation mismatch invalidates testing, while a production-fingerprint mismatch invalidates both review and testing;
2. transition the TASK to `AWAITING USER ACCEPTANCE`;
3. record compact review and test summaries in the TASK, including Review Packet integrity, acceptance traceability, protocol coverage, exact selected commands, exit results, skipped checks, selection rationale, and accepted execution exceptions;
4. report the delivered behavior, verification evidence, limitations, and manual steps;
5. wait without timeout for user validation.

User-requested fixes return this same TASK to `IN PROGRESS` and invalidate affected evidence. Production changes repeat strong review and testing; supporting-only changes preserve a matching clean production review and repeat testing without another reviewer invocation. New scope requires Replan. Do not mark the TASK `DONE`, commit, or start the next TASK in this skill.
