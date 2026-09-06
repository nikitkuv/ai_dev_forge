---
name: forge-run-task
description: Execute one approved Forge TASK through its fast or standard delivery track and hand it off for manual user acceptance. Use only after the user authorizes that TASK's separate Task Start gate.
---

# Run One TASK

## Mechanical work and compact evidence

Use `python .ai/tools/forge.py fingerprint <explicit-files>` for whole/production surfaces, and `section` to read only the selected TASK/plan sections. Include additions/deletions and relevant dependencies; a file hash is not proof that scope is complete. Preserve base revision and reproducible Git diffs separately. New fingerprint algorithms invalidate incompatible old evidence.

Execute approved command packets through `checks <packet.json> --execute`; use `--reuse` only for approved deterministic Task checks with complete input closure, matching runtime/environment/commands and no external mutable state. Reuse revalidates command evidence, never the independent fast assurance, standard review/test-integrity judgment, RED failure requirement or acceptance. Epic Validation always executes afresh. Do not call a model just to run commands or summarize success. Persist compact command results/fingerprints in TASK; raw logs remain local. Read `.ai/tools/USAGE.md` for packet fields. Record available actual usage via `metrics-record`; missing token counts remain unknown.

For external planner/reviewer transport prefer `forge.py role` with the active orchestrator, role and secure prompt path; it resolves the existing route and performs one bounded preflight internally. Do not execute a separate preflight and then repeat it inside the launcher. Legacy launcher paths below remain the compatibility transport if Python is unavailable. A started failure never changes provider or transport automatically.

## Start the TASK

Native generated agents already receive their neutral instructions; do not duplicate the role contract in their assignment. External role prompts include that contract exactly once. This preserves identical effective instructions while avoiding repeated input tokens.

1. Require `definition_status: approved`, lifecycle `status: TODO`, satisfied dependencies, no unresolved blocker, and no other code-writing TASK in progress.
2. Resolve the delivery track. Treat a legacy TASK without `delivery_track` as `standard`. Require an approved track and rationale; for `fast`, revalidate bounded scope, reversibility, low risk, unambiguous expected behavior, deterministic focused verification, and absence of every disqualifier in `.ai/framework/contracts.yaml`. Missing, uncertain, stale, or contradictory evidence selects or escalates to `standard` rather than guessing.
3. Show the TASK goal, scope, acceptance criteria, affected surface, risk flags, delivery track and rationale, Verification Plan, review focus, constraints, and any `external_sources` with their source intent. Do not require connector access for an unlinked TASK.
4. Obtain explicit Task Start authorization, or verify an existing user-approved bounded grant using `task-start-check <TASK-path>`. A matching grant covers only this unchanged approved definition and never bypasses dependencies, blockers, eligibility or single-writer checks. Do not ask again for authorization already granted within those boundaries.
5. Let only the orchestrator transition the TASK to `IN PROGRESS`, record the gate, establish the next implementation revision, and record the track used at start. Standard to fast is forbidden after Task Start.

## Run common implementation

1. Invoke `implementer` for this TASK only and pass the approved delivery track and its constraints. Require production changes and necessary tests on both tracks.
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

## Fast track

Use this branch only while `delivery_track: fast` remains eligible. Do not invoke `reviewer` or `tester` for a fast TASK.

1. Reproduce the whole-implementation fingerprint and exact scoped diff; do not accept the implementer's fingerprint or command claims on assertion alone.
2. Revalidate every positive fast criterion and every disqualifier against the actual changed and affected surfaces. Inspect all production and supporting paths, their callers and consumers as needed, and trace every acceptance criterion and affected risk to the diff and evidence.
3. Audit test integrity independently: verify oracles, test-change classifications, discriminating assertions, and applicable normal, boundary, invalid-input, error/recovery, state-transition, and side-effect coverage.
4. Execute or reproduce every selected focused behavior test, affected-component check, applicable scoped quality check, and bounded Task fuzz smoke. For any not-applicable item, verify its rationale against the actual surface. The orchestrator may not silently skip, weaken, substitute, or expand to the full project suite.
5. If scope, risk, eligibility, path classification, test integrity, command selection, fingerprint, or verification is missing, stale, contradictory, unexpectedly failing, or disqualified, record the trigger, invalidate fast assurance, escalate monotonically from fast to standard, and continue through the complete Standard track. Unchanged-scope safety escalation does not require Replan; an actual scope change still does. Standard to fast after Task Start is forbidden.
6. Otherwise record a `PASSED` Fast Assurance Summary bound to the exact whole-implementation fingerprint, including eligibility revalidation, diff inspection, acceptance/risk traceability, path classification, test integrity, commands and results, and not-applicable rationales. Fast assurance never claims independent `CLEAN` review or separate tester evidence.
7. Transition directly from `IN PROGRESS` to `AWAITING USER ACCEPTANCE`, report the delivered behavior, assurance evidence, limitations and manual steps, then wait without timeout for user validation.

Any implementation change after fast assurance invalidates the whole assurance result. User-requested in-scope fixes return the TASK to `IN PROGRESS` and require renewed fast eligibility plus the entire assurance procedure; any eligibility failure escalates to standard.

## Standard track

Use this branch for `delivery_track: standard`, every legacy TASK without a track, and every TASK escalated from fast. It preserves the independent reviewer and tester gates.
10. Transition to `IN REVIEW` and determine review freshness from the production fingerprint:
   - if no prior clean review has the same production fingerprint, or legacy evidence lacks a production fingerprint, read `.ai/project.yaml`, require a valid `role_execution.mode`, and build one prompt from the complete neutral `.ai/framework/agents/reviewer.yaml` contract plus the exact Review Packet. Route it exactly as configured: `native_subagents` invokes the active Codex, Claude Code, or OpenCode platform's generated reviewer with no external preflight; `claude_with_codex` requires Claude Code and uses `.claude/forge/codex-role-runner.mjs`; `codex_with_claude` requires Codex and uses `.codex/forge/claude-role-runner.mjs` with `models.claude.strong.model` and effort. OpenCode-led setup proposes the existing `native_subagents` value by default only when no approved route exists; it adds no mode and does not silently rewrite an approved value. For either external route, run preflight, block on unavailability or active-orchestrator mismatch, pass the prompt through a secure temporary file, and always remove the file. All routes use the same production-only blocking boundary. There is no fallback before or after execution; a non-zero exit, timeout, permission failure, runtime mismatch, packet-integrity failure, or malformed output blocks review;
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

After current track-specific assurance evidence passes:

1. for standard, confirm testing matches the current implementation revision and whole-implementation fingerprint and its production fingerprint exactly matches the new or preserved clean review; for fast, confirm current `PASSED` orchestrator assurance exactly matches the whole-implementation fingerprint and eligibility revalidation;
2. transition the TASK to `AWAITING USER ACCEPTANCE`;
3. record the track-appropriate compact evidence summary: Review/Test summaries for standard or Fast Assurance Summary for fast, including acceptance traceability, exact selected commands, exit results, skipped checks, selection rationale, and accepted execution exceptions;
4. report the delivered behavior, verification evidence, limitations, and manual steps;
5. wait without timeout for user validation.

User-requested fixes return this same TASK to `IN PROGRESS` and invalidate affected evidence. On standard, production changes repeat strong review and testing while supporting-only changes preserve a matching clean production review and repeat testing without another reviewer invocation. On fast, every implementation change invalidates fast assurance and requires full revalidation; any failed eligibility or verification escalates to standard. New scope requires Replan. Do not mark the TASK `DONE`, commit, or start the next TASK in this skill.
