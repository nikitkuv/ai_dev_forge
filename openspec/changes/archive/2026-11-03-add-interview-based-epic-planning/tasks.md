# Tasks — add-interview-based-epic-planning

## 1. Interview flow (epic-planning-interview)

- [x] 1.1 Rework `.ai/framework/skills/forge-prepare-epic/SKILL.md` into the four staged interview stages (objective and expected outcome, interface design, risks and critical paths, decomposition skeleton) with per-stage user confirmation and a stage-collapse path requiring recorded rationale; verify a contract test asserts the stage gating and `python .ai/tools/forge.py validate` exits 0.
- [x] 1.2 Add the `Interface Delta` subsection to the Implementation Strategy section of `.ai/templates/plan.md` and record interview stage confirmations as rows in Epic User Validation History; verify template contract tests pass via `node --test tests/*.test.mjs`.
- [x] 1.3 Make skeleton-first ordering normative in `.ai/framework/agents/epic-planner.yaml` — the assignment input is the confirmed skeleton plus Interface Delta, and no test cases, change maps, or fuzz detail are produced before skeleton confirmation; verify `node --test tests/role-execution-matrix.test.mjs` passes.
- [x] 1.4 Implement the Plan Approval consistency check so interface or scope changes absent from the confirmed interview return the plan to the interview stages, recorded in `.ai/framework/contracts.yaml`; verify a contract test covers the return path and the consistent-plan path.

## 2. Contract sketch (task-contract-sketch)

- [x] 2.1 Add the `Contract Sketch` section to `.ai/templates/TASK.md` (required when affected contracts include public interfaces, explicit none otherwise) and a `contract_sketch` contract to `.ai/framework/contracts.yaml` (prepared before Plan Approval, Replan on shape change); verify `forge.py validate` exits 0 and Python unit tests pass.
- [x] 2.2 Carry sketches in the Review Packet and add a per-contract sketch-conformance step to `.ai/framework/agents/reviewer.yaml` inside acceptance traceability, with unapproved shape differences reported as production findings; verify reviewer contract tests and role-runner tests pass.
- [x] 2.3 Bind approved sketches as boundary constraints at Task Start in `.ai/framework/skills/forge-run-task/SKILL.md` and `.ai/framework/agents/implementer.yaml`, routing shape changes through Replan; verify a contract test asserts the binding and the Replan route.
- [x] 2.4 Verify legacy tolerance: a TASK without a sketch follows the existing affected-contracts flow and is never blocked by the sketch requirement; verify via a fixture-based test in `tests/`.

## 3. Documentation and integration

- [x] 3.1 Update `FRAMEWORK.md`, `README.md`, and `RUNBOOK.md` for the interview flow and contract sketches, including migration notes for in-flight epics; verify `forge.py validate` exits 0 and documentation references resolve.
- [x] 3.2 Run the full verification suite (`python .ai/tools/forge.py validate`, `python -m unittest discover -s tests -p "test_*.py" -v`, `node --test tests/*.test.mjs`) plus a `forge-check-framework` style conformance pass; verify everything is green.
