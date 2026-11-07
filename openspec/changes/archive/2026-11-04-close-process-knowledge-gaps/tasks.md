# Tasks — close-process-knowledge-gaps

## 1. Shared contracts and template fields

- [x] 1.1 Add process follow-up enums (root causes `task_ambiguity`, `missing_repo_context`, `missing_acceptance_criterion`, `weak_test_oracle`, `rule_drift`, `other`; fix targets `skill`, `template_field`, `contract`, `neutral_instruction`, `regression_test`, `no_process_change`; disposition states) and the rule-declaration shape (`id`, `statement`, `pattern`, `scope`, `exclusions`, `kind`) to `.ai/framework/contracts.yaml`; verify `python .ai/tools/forge.py validate` exits 0 and `python -m unittest discover -s tests -p "test_*.py"` passes.
- [x] 1.2 Add the `Process Follow-up` block to `.ai/templates/TASK.md` and follow-up facts to the Epic User Validation History in `.ai/templates/plan.md`, defaulting to empty; verify `forge.py validate` exits 0 and existing contract tests still pass on legacy fixtures.

## 2. Rule drift detection

- [x] 2.1 Create `.ai/templates/rules.yaml` template and record `.ai/custom/rules.yaml` as project-owned in `.ai/CONVENTIONS.md` ownership notes; verify `forge.py validate` accepts a project carrying the template and `forge migrate` preview lists it as additive.
- [x] 2.2 Implement a read-only `forge.py` rules check (pattern vs scoped paths: match count, violating paths, `exclusions` honored, pattern-less rules reported as judgment; no writes, no model calls) per `specs/rule-drift-detection/spec.md`; verify new cases in `tests/test_python_tools.py` pass via `python -m unittest discover -s tests -p "test_*.py"`.
- [x] 2.3 Render the compact "Project Rules" statement block from `rules.yaml` into `.ai/custom/router-shared.md` handling in adapter templates and sync, keeping patterns out of the router and respecting the line budget; verify `node --test tests/*.test.mjs` passes, including adapter parity.
- [x] 2.4 Include the drift report in `forge-check-framework` conformance coverage with judgment fields preserved and detect divergence between router statements and `rules.yaml` entries; verify a contract test asserts the drift coverage the way `tests/test-integrity-contract.test.mjs` asserts invariants.

## 3. Process fix follow-up

- [x] 3.1 Extend `.ai/framework/skills/forge-complete-task/SKILL.md` so a rejected or corrected delivery must record a follow-up (root cause, fix target, rationale) before `DONE`, while successful acceptance may record `no_process_change`; verify transition unit tests cover both paths.
- [x] 3.2 Extend `.ai/framework/skills/forge-complete-epic/SKILL.md` and `plan.md` handling so the same facts are recorded in Epic User Validation History before `COMPLETED`; verify the epic completion flow tests pass.
- [x] 3.3 Surface unapplied follow-ups (no applied fix, no decline rationale) as advisory items in `forge-check-framework` and the Python conformance output; verify a unit test covers the advisory case and confirms it never blocks a gate.

## 4. Human review focus

- [x] 4.1 Add a `Critical Surfaces` section to `.ai/templates/ARCHITECTURE.md` and teach `epic-planner` to fold intersecting surfaces into Task Review Focus (recording explicitly when none intersect) per `specs/human-review-focus/spec.md`; verify a role contract test asserts the folding behavior.
- [x] 4.2 Group Manual Verification and acceptance presentation by touched critical surfaces in `.ai/framework/skills/forge-run-task/SKILL.md` and `forge-complete-task/SKILL.md`, presented first, without changing any assurance scope; verify contract tests assert grouping and unchanged gating.

## 5. Integration and documentation

- [x] 5.1 Update `FRAMEWORK.md`, `README.md`, and `RUNBOOK.md` for rule declarations, follow-up fields, and critical surfaces; verify `forge.py validate` exits 0 and documentation references resolve.
- [x] 5.2 Run the full verification suite (`python .ai/tools/forge.py validate`, `python -m unittest discover -s tests -p "test_*.py" -v`, `node --test tests/*.test.mjs`) plus a `forge-check-framework` style conformance pass; verify everything is green and the conformance output includes drift coverage and pending follow-ups.
