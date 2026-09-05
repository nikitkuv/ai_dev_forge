## 1. Minimal Canonical Model

- [x] 1.1 Extend `.ai/framework/contracts.yaml` with `INV-NNNN`, outcomes `no_action`, `promoted`, `fixed_directly`, and `unresolved`, required investigation fields, direct-fix evidence, planning references, lifecycle separation, and commit rules; verify focused contract tests parse and assert the complete minimal contract.
- [x] 1.2 Add `.ai/templates/INVESTIGATION.md` for one flat `investigations/INV-NNNN-<short-name>.md` record with question, scope, baseline, investigation, evidence, cause, conclusion, next action, linked work, and optional Direct Fix sections; verify the template has no TASK-like lifecycle or mandatory subagent fields.
- [x] 1.3 Update `.ai/CONVENTIONS.md` and `.ai/framework/manifest.yaml` with identity allocation, canonical path, ownership, collision handling, and research-reference conventions; verify framework checks accept an absent or empty `investigations/` directory and reject duplicate IDs.

## 2. Ad Hoc Workflow

- [x] 2.1 Add `.ai/framework/skills/forge-investigate/SKILL.md` so the main agent establishes scope, chooses its own investigation methods, records evidence and conclusions, never invokes generated subagents, and finishes as `no_action`, `promoted`, `fixed_directly`, or `unresolved`; verify skill tests cover every outcome.
- [x] 2.2 Add the direct-fix path with explicit user authorization, preserved unrelated changes, product/architecture decision handling, proportionate verification, and a path-level added/modified/removed change ledger tied to Git or a scoped diff; verify an investigation-and-fix request does not require Task Start or generated roles.
- [x] 2.3 Add promotion through existing Bug/Epic/Replan approval, reciprocal `research_refs`, and later disposition updates; verify investigation creation alone never modifies Backlog or execution state.

## 3. Reuse and Recovery

- [x] 3.1 Update feature intake, bug intake, Replan, `epic-planner`, and `forge-prepare-epic` to read explicit `research_refs`, search for obvious related records by subject/area/paths, confirm uncertain matches with the user, and reuse applicable cause, solution, risk, and verification context; verify planning does not repeat an applicable complete investigation.
- [x] 3.2 Update plan and TASK templates with optional compact `research_refs`, and record promoted work back in the INV; verify zero-reference legacy work remains valid.
- [x] 3.3 Update context collection and resume behavior to discover unfinished investigations and report when their direct edits make existing lifecycle evidence stale; verify recovery depends on canonical records and Git rather than chat history.

## 4. Distribution and Validation

- [x] 4.1 Update bootstrap, migration, framework check, and final validation to install the template and skill, preserve project-owned investigation files, validate required sections and change ledgers, and create no synthetic INV records; verify absent, valid, duplicate, malformed, and collision fixtures.
- [x] 4.2 Update the root-router template and adapter generation/synchronization guidance, regenerate managed outputs, and verify Codex/Claude/OpenCode parity plus the no-subagent investigation route.
- [x] 4.3 Update `README.md`, `FRAMEWORK.md`, and `RUNBOOK.md` and add an algorithm-performance scenario covering research-only, promotion, and direct-fix outcomes; verify maintained-documentation tests describe the same simple workflow.
- [x] 4.4 Add `tests/ad-hoc-investigation-contract.test.mjs`, run `node --test tests/*.test.mjs`, run adapter/framework consistency checks, and run strict OpenSpec validation; reconcile every failure before handoff.
- [x] 4.5 Increment the framework version only after contracts, templates, skills, documentation, tests, and generated adapters agree; verify no stale version or managed-output fingerprint remains.
