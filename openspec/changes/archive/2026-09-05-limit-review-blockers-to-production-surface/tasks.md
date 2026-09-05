## 1. Review Boundary and Evidence Model

- [x] 1.1 Add production/supporting path classification and separate whole-implementation and production-surface fingerprints to the framework contracts and TASK template; require rationale for ambiguous artifacts and legacy-review refresh when the production fingerprint is absent.
- [x] 1.2 Update the neutral reviewer contract to inspect production paths in context, use tests and non-production files only as supporting evidence, emit outcome-affecting production findings separately from advisory non-production observations, and allow `CLEAN` with observations while preserving packet-integrity blockers.

## 2. Token-Bounded Review Orchestration

- [x] 2.1 Update `forge-run-task` so only production findings return `IN REVIEW` to `IN PROGRESS`, non-production observations flow into the tester packet, and a supporting-only correction after clean review proceeds directly to testing.
- [x] 2.2 Change evidence invalidation rules so a production fingerprint change invalidates review and testing, while a test-only or other supporting-only change preserves current clean review and invalidates only affected testing evidence; retain tester failure and remediation gates.
- [x] 2.3 Update completion, resume, adapter-generation, and final-validation guidance wherever review currency or the implementation fingerprint is assumed to require a repeated strong review after every file change.

## 3. Documentation and Regression Coverage

- [x] 3.1 Update `README.md`, `FRAMEWORK.md`, `RUNBOOK.md`, and the development-pipeline scenario to define the production surface, show `CLEAN` with advisory observations, and document direct tester reruns for supporting-only remediation.
- [x] 3.2 Add contract tests covering production-affecting configuration/schema/migration/build paths, non-blocking test/dev-only observations, production-fingerprint review reuse, tester ownership, legacy evidence, and packet-integrity blocking; update the framework version assertion as required.
- [x] 3.3 Run `npm.cmd test` and strict OpenSpec validation when the CLI is available, then reconcile all maintained sources and generated adapter expectations.
