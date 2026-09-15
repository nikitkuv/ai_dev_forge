## 1. Shared transaction primitives

- [x] 1.1 Extract atomic `_replace`, guard-directory journal write, rollback, and recovery helpers from `forge_adapters.py` into `forge_core.py`; re-import them in `forge_adapters.py` with no behavior change and verify the full existing Python suite passes: `.forge-venv/Scripts/python -m unittest discover -s tests -p "test_*.py" -v`
- [x] 1.2 Parameterize the transaction helper on a guard-directory name and add unit tests covering caught-failure rollback and crash-journal recovery that refuses later edits, mirroring the existing adapter transaction tests

## 2. Read-only commands

- [x] 2.1 Implement `next-id --kind <task|bug|inv|epic|adr|mut>` scanning the canonical locations per design D8; verify with unit tests over fixtures covering gap-in-numbering (no fill), empty location, and registry-declared MUT ids
- [x] 2.2 Extend `validate --project`/`--adapters` with the D10 checks: root `AGENTS.md` line budget and exact `CLAUDE.md` import line, generated agent files UTF-8 no-BOM with frontmatter at byte zero, `DECISIONS.md`/`decisions/` ADR parity, plan Task order vs TASK files, Workflow State block presence/shape, INV record structure, mutation-registry structure; verify each check fires on a deliberately corrupted fixture and stays silent on a clean one
- [x] 2.3 Implement `evidence-check <task-path>` parsing the Workflow State YAML block and reporting acceptance-eligibility, review-freshness, and fast-assurance comparisons per design D5, treating placeholders as insufficient; verify with unit tests for supporting-only change (fresh review), production change (stale review), and legacy missing fingerprints
- [x] 2.4 Extend `evidence-check --epic <epic-id>` with Epic gate aggregation: all TASKs DONE, final fuzz impact/smoke evidence present, aggregate fingerprint over the union of recorded TASK surfaces; verify on a fixture Epic in both eligible and ineligible states
- [x] 2.5 Implement `review-packet <task-path>` emitting compact JSON with recomputed whole/production fingerprints and bounded scoped Git diffs for both surfaces against the recorded base revision (design D6); verify missing recorded inputs fail with the exact field and diffs match manual `git diff` on a fixture repository
- [x] 2.6 Implement `checks-new` writing a valid packet from explicit argv/inputs/stage/cacheability without shell interpolation; verify the written packet is accepted by the existing `checks` executor unchanged in a unit test
- [x] 2.7 Add `role --assignment-file <path>`: helper concatenates the neutral contract from `.ai/framework/agents/<role>.yaml` with the assignment into a transient in-project temp file removed after use (design D7); verify by unit test that the composed prompt contains the contract exactly once, the temp file is absent after the call, and a malformed contract fails before any subprocess launch

## 3. Scaffolding commands

- [x] 3.1 Implement `inv-create --subject <s> --area <a> [--paths ...]`: allocate the next INV id via `next-id`, instantiate `.ai/templates/INVESTIGATION.md` with baseline revision and dirty-tree disposition, preview/apply transactionally, and report the exact diff; verify a unit test creates the record from a fixture template and rejects a duplicate short-name path
- [x] 3.2 Extend backlog parsing to the Defect Queue table and implement `backlog add-bug` (insert one `OPEN` row) and `backlog update-row` (change only named cells) as preview/apply transactions per design D4; verify unit tests assert all unrelated rows and the header stay byte-identical and escaped pipes round-trip

## 4. Lifecycle mutations

- [x] 4.1 Implement `transition task <path> --to <status>` with mechanical preconditions (enum from `contracts.yaml`, source-status match, single-writer, Backlog consistency), Workflow State `current_gate`/timestamp updates per design D3, and preview/apply; verify unit tests cover legal transition, illegal enum, wrong source status, and second concurrent writer rejection
- [x] 4.2 Implement `transition epic <epic-id> --to <status>` editing exactly one Backlog Epic Roadmap row through the transaction; verify rollback restores the row byte-identically on induced validation failure
- [x] 4.3 Implement `epic-start` and `epic-complete` as atomic logical transitions: directory move + Backlog row + structural revalidation + rollback including the move-back, with a rename journal per design D2; verify unit tests on fixtures for the happy path and for a mid-transaction validation failure restoring both directory location and Backlog status
- [x] 4.4 Implement `accept-record <task-path>` appending the explicit acceptance facts to User Acceptance/Iteration History and transitioning only that TASK to DONE, with optional explicit `--resolve-bug` row update; verify missing accepting-user/decision-reference inputs are refused and unrelated Bugs stay unchanged in tests
- [x] 4.5 Implement `commit-scoped` per design D9: explicit path staging from recorded TASK scope or `--paths`, unrelated-change detection against `git status`, policy gate on `git.policy`, message template; verify tests on a fixture repository cover exclusion of unrelated dirty files, `manual` policy no-commit reporting, and the committed file list under `auto_commit_after_acceptance`

## 5. Skill and documentation updates

- [x] 5.1 Update `forge-run-task`, `forge-complete-task`, `forge-complete-epic`, `forge-prepare-epic`, `forge-intake-bug`, `forge-investigate`, `forge-reprioritize-backlog`, `forge-resume-development`, and `forge-check-framework` to route mechanical steps through the new helpers while preserving every semantic gate and authorization requirement; verify `node --test tests/*.test.mjs` passes including any updated contract tests
- [x] 5.2 Rewrite `.ai/tools/USAGE.md` sections for all new commands and the refined helper contract ("execute only explicitly requested transitions; never decide or infer"); verify README token-economy section, RUNBOOK scenarios, and FRAMEWORK.md wording mention the new commands consistently
- [x] 5.3 Run the complete verification: `.forge-venv/Scripts/python .ai/tools/forge.py validate` clean, full Python unittest suite, and `node --test tests/*.test.mjs` all green
