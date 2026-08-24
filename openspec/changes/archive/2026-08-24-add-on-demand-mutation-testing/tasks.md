## 1. Neutral Contracts and Project-Owned Records

- [x] 1.1 Extend the neutral manifest and lifecycle-independent contracts with `forge-mutation-test`, `mutation-runner`, `mutation-analyzer`, mutation outcomes/analysis states, and the optional project-owned `quality/mutation-testing/` path; verify contract and manifest schema tests pass without adding a development transition or gate.
- [x] 1.2 Add templates and validation rules for `quality/mutation-testing/registry.yaml` and `runs/MUT-NNNN.yaml`, including unsuccessful attempts, exact fingerprints, metrics-only state, conditional/partial analysis, artifact retention, and optional dispositions; verify representative valid and invalid records in focused tests.
- [x] 1.3 Add an empty optional backend-neutral mutation configuration to the project template and preserve absence as a valid setup; verify bootstrap and migration fixtures do not install tools or create mutation history by default.

## 2. Agent Roles and On-Demand Skill

- [x] 2.1 Add the fast `mutation-runner` neutral agent contract with exact packet validation, baseline-first execution, bounded backend invocation, fingerprint freshness checks, normalized runtime artifacts, `SETUP REQUIRED` handling, and prohibitions on tracked edits, installation, lifecycle mutation, remediation, and agent spawning; verify role-policy tests.
- [x] 2.2 Add the strong `mutation-analyzer` neutral agent contract with explicit authorization, current-artifact checks, bounded candidate prioritization, evidence-backed classifications, partial-analysis reporting, and prohibitions on remediation, lifecycle mutation, installation, and agent spawning; verify role-policy tests.
- [x] 2.3 Add `forge-mutation-test` with metrics-only default, immediate `--analyze` behavior, deferred `MUT-NNNN` analysis, analyzer skip conditions, atomic record allocation/update, compact summaries, and separate user-approved disposition routing; verify workflow contract tests cover all runner and analyzer branches.

## 3. Dual-Platform Generation and Migration

- [x] 3.1 Extend generator ownership and adapter rendering for the new skill and both agents, preserving their fast/strong tiers and runtime-artifact policies on Codex and Claude; regenerate adapters and verify source-hash and cross-platform parity tests.
- [x] 3.2 Update framework migration and collision handling so newly managed adapter files are installed while pre-existing project-owned files and `quality/mutation-testing/` history are preserved; verify migration and repair tests.

## 4. Conformance and Behavioral Verification

- [x] 4.1 Extend framework conformance checks to validate optional mutation configuration, registry/run schemas, agent and skill presence, packet/fingerprint invariants, analyzer authorization and skip rules, and the absence of mutation-driven lifecycle effects; verify focused conformance tests.
- [x] 4.2 Add end-to-end fixture scenarios for metrics-only success, all-mutants-killed analysis skip, authorized survivor analysis, deferred analysis reuse, setup-required, baseline failure, stale fingerprint, bounded partial analysis, and explicit later disposition; verify the scenario suite passes without a real mutation dependency.
- [x] 4.3 Run the complete framework verification, adapter parity, migration, and documentation test suites and resolve every regression attributable to this change.

## 5. Documentation

- [x] 5.1 Update `FRAMEWORK.md`, `README.md`, `RUNBOOK.md`, and migration guidance to explain the standalone mutation workflow, fast runner versus conditional strong analyzer, durable `MUT-*` history, backend-neutral setup, cost controls, and strict non-interference with Epic/TASK lifecycle; verify documentation consistency checks.
