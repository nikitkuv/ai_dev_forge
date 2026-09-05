## 1. Canonical Track and Evidence Model

- [x] 1.1 Extend `.ai/framework/contracts.yaml` with exactly `fast` and `standard` delivery tracks, the guarded fast transition, track-specific quality/commit predicates, eligibility disqualifiers, monotonic escalation, legacy-standard defaulting, and unchanged Epic gates; verify new contract tests parse and assert every rule.
- [x] 1.2 Add `delivery_track: standard`, track rationale/eligibility/disqualifier fields, escalation history, and a fingerprint-bound Fast Assurance Summary to the TASK template while keeping standard Review/Test summaries; verify template contract tests distinguish the two evidence sets.
- [x] 1.3 Update the Epic-plan template and planning preparation contract so every proposed TASK has an approved track and criterion-level rationale, and verify low-risk metadata alone cannot satisfy fast selection.

## 2. Agent and TASK Workflow Routing

- [x] 2.1 Update the epic-planner contract to propose fast only from complete positive eligibility evidence, otherwise standard, and update the implementer contract to consume the approved track without weakening TDD, path classification, or implementation evidence; verify agent-contract tests cover eligible, disqualified, and uncertain examples.
- [x] 2.2 Refactor `forge-run-task` into explicit fast and standard branches: both invoke implementer, fast performs reproducible orchestrator assurance with no reviewer/tester, standard preserves the current reviewer/tester route, and any fast mismatch escalates before acceptance; verify routing tests assert exact agent invocations and evidence freshness.
- [x] 2.3 Update task completion and Git gates to accept current fast assurance or current standard review/testing according to the recorded track while always requiring explicit user acceptance; verify neither track can commit early or reuse stale evidence.
- [x] 2.4 Update resume, pause, replan, and remediation rules so missing legacy track means standard, fast-to-standard escalation is recorded without weakening gates, standard-to-fast after start is forbidden, and scope changes still require Replan; verify restart scenarios reconstruct the correct next gate without session history.

## 3. Framework Lifecycle, Migration, and Distribution

- [x] 3.1 Update bootstrap, migration, framework-check, and final-validation instructions to install and validate the new fields and transitions, preserve project-owned data, default legacy TASKs to standard, and never synthesize fast evidence; verify migration fixtures cover planned, active, reviewed, testing, and awaiting-acceptance legacy TASKs.
- [x] 3.2 Update neutral adapter templates and generation/synchronization rules with track-aware routing while leaving model mappings and external reviewer-provider routing unchanged; regenerate adapters and verify Codex/Claude parity tests pass.
- [x] 3.3 Increment the framework version and update manifest/version assertions only after every managed source and generated adapter is synchronized; verify framework integrity detects a stale pre-track bundle.

## 4. Documentation and Scenarios

- [x] 4.1 Update `README.md`, `FRAMEWORK.md`, and `RUNBOOK.md` to distinguish delivery track, model tier, and risk level; document the fail-closed eligibility matrix, both complete flows, evidence requirements, and escalation semantics; verify maintained-documentation tests find the normative terms consistently.
- [x] 4.2 Update the development-pipeline scenario and diagram with fast, standard, and fast-to-standard branches, including examples for documentation, small internal logic, public contracts, migrations, and failed verification; verify rendered/source scenario checks contain no route that bypasses user or Epic gates.

## 5. Contract Coverage and Validation

- [x] 5.1 Add focused contract tests proving eligible fast work skips reviewer/tester but retains implementer, TDD when applicable, orchestrator reruns, current fingerprints, and Task Acceptance; run the new test file and confirm it fails against the old framework and passes after implementation.
- [x] 5.2 Add negative contract tests for every fast disqualifier, missing evidence, unexpected affected surface, failed checks, stale assurance, forbidden late downgrade, and direct-transition misuse; run them to verify fail-closed escalation to standard.
- [x] 5.3 Extend production-review, test-integrity, lifecycle, resume, migration, adapter-parity, Epic Validation, and fuzzing contracts to prove standard behavior and aggregate Epic assurance remain unchanged; run the affected test selection and record exact commands/results.
- [x] 5.4 Run the repository suite with `node --test tests/*.test.mjs` (this framework source has no `package.json`), the framework contract checks, adapter parity/generation checks, and `openspec validate add-fast-standard-delivery-tracks --strict`; reconcile all failures and record final passing evidence before implementation handoff.
