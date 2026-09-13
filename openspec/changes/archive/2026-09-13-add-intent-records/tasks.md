# Tasks: Add Intent Records

## 1. Contract, template, and manifest

- [x] 1.1 Create `.ai/templates/INTENT.md` with the bounded one-page template (frontmatter: `document_type`, `id`, `created_at`, `author`, `origin`, `outcome`, `promoted_to`, `research_refs`; sections: problem/motivation, proposed outcome, affected users/systems, constraints, considered alternatives, open questions, outcome history) and verify it matches design D4 section-for-section
- [x] 1.2 Add the intent contract to `.ai/framework/contracts.yaml` (outcome values, evidence-only boundaries, materiality bar), add `intents/` to project-owned paths and `INTENT.md` to framework templates in `.ai/framework/manifest.yaml`, bump version to `4.10.0`, and add `INT-NNNN` to the identifier list in `.ai/CONVENTIONS.md`; verify `.forge-venv/Scripts/python .ai/tools/forge.py validate` passes
- [x] 1.3 Add the optional `Intent` column to `.ai/templates/BACKLOG.md` (documented with the same backward-compatibility note as `Sources`/`Research`) and verify the Backlog structural checks in `forge.py validate` still pass on the updated template

## 2. Local tooling

- [x] 2.1 Extend `forge.py next-id` with the `int` identifier type (`INT-0001`, monotonic, never reused) and verify a new unittest allocates increasing IDs across repeated calls and refuses reuse
- [x] 2.2 Add INT structural validation to `forge.py validate` (required frontmatter, allowed outcome values, `promoted_to` target exists when set, `research_refs` resolve to existing investigations, required sections present, advisory warning on oversized records) and verify new unittests cover each malformed-record case from the spec scenarios
- [x] 2.3 Run the full Python suite (`.forge-venv/Scripts/python -m unittest discover -s tests -p "test_*.py" -v`) and verify all existing and new tests pass

## 3. Skills

- [x] 3.1 Update `forge-intake-feature` SKILL.md: add the intent phase (reserve `INT-NNNN` as the first durable action, fill the template through a proportionate interview, present the finalized record for confirmation), record `rejected`/`deferred` outcomes with rationale without creating an Epic, add the `Intent` column to Epic-row creation, require resolved open questions for `OUTLINE → READY`, and amend the "parallel design artifact" wording to permit the bounded INT; verify `.forge-venv/Scripts/python .ai/tools/forge.py validate` conformance checks pass
- [x] 3.2 Update `forge-intake-external-work` SKILL.md: create an INT for every product-change candidate (retained or rejected) before canonical changes, populate sections from normalized ticket evidence first, preserve provider-neutral source keys in the record, and link `promoted_to` for approved Epics; verify skill text covers all three spec scenarios (promoted, rejected, underspecified ticket)
- [x] 3.3 Update `forge-prepare-epic` SKILL.md: read the linked INT as a primary planning input alongside SPEC, use its motivation/constraints/alternatives, and block readiness advancement while material open questions remain; verify the change is limited to input gathering and the READY condition
- [x] 3.4 Verify no other skill needs changes by grepping neutral sources for intake/prepare references (`grep -rn "intake\|prepare-epic" .ai/framework/skills/`) and reviewing each hit against the new INT flow

## 4. Documentation and scenarios

- [x] 4.1 Update `FRAMEWORK.md`: add `intents/` to the consumer project structure, add the sources-of-truth row ("история продуктовых запросов и их исходов — соответствующий INT"), add `INT-NNNN` to the identifier list, and extend the skills summary; verify every claim matches the implemented contract
- [x] 4.2 Update `README.md` and `RUNBOOK.md`: describe INT capture in the intake flow (sections 4 and 94 of the runbook respectively for feature intake), retention of rejected intents, and the `Intent` column; verify the described flow matches the updated skills
- [x] 4.3 Add the v4.9 → v4.10 entry to `MIGRATION.md` (optional `intents/` folder, optional Backlog column, no backfill, upgrade does not create the folder); verify the entry follows the existing migration-entry format
- [x] 4.4 Update the relevant `scenarios/` intake walkthrough to show the INT interview step, rejected-intent retention, and the linked Backlog row; verify the scenario stays consistent with RUNBOOK and skill text

## 5. Final validation

- [x] 5.1 Run the complete local verification (Python unittest suite, `node --test tests/*.test.mjs`, `forge.py validate`) and verify everything is green
- [x] 5.2 Cross-check every requirement in `specs/intent-records/spec.md` and `specs/external-work-intake/spec.md` against the implemented tasks and verify each scenario is covered by a skill instruction, validation rule, or documented flow
