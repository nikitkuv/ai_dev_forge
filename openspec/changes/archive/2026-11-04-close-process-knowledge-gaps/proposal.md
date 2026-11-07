# Proposal — close-process-knowledge-gaps

## Why

The 2026-11-03 workflow audit against published AI-coding pain points found that Forge already externalizes execution state, pre-code decisions, and independent verification far beyond the baseline practice, yet three "the process lives in the head" gaps remain: documented rules can silently contradict code, delivery failures do not feed back into skills and contracts, and the human's residual acceptance effort has no project-declared focus. These gaps map onto the recurring pains the framework exists to remove — review fatigue and green tests without a solved task.

## What Changes

- **Rule-drift detection** — project rules are declared with checkable patterns and scopes in a project-owned declaration; a deterministic helper reports code that contradicts stated rules; agents read the rules; drift is resolved by fixing the code or amending the rule, never ignored.
- **Process-fix follow-up** — when delivery missed the goal despite green checks, Task/Epic Acceptance records a process follow-up: a root-cause category and a disposition (skill, template field, contract, neutral instruction, or regression test) applied as a separate authorized change.
- **Human review focus** — the project declares its critical surfaces (architecture, billing, data model, and similar); the epic planner folds them into Task Review Focus and the orchestrator groups Manual Verification and acceptance presentation by them, so the human spot-checks only the places that matter.

## Capabilities

### New Capabilities

- `rule-drift-detection`: Project-owned declaration of checkable rules with patterns and scopes, deterministic drift reporting between stated rules and code, and remediation discipline.
- `process-fix-followup`: Root-cause classification and process disposition when a delivery misses its goal despite passing checks, recorded at acceptance and applied to framework/process sources.
- `human-review-focus`: Project-owned critical-surfaces declaration, its use in planning Review Focus, and grouping of manual verification and acceptance presentation around it.

### Modified Capabilities

(none — existing capability requirements are unchanged; implementation touchpoints live in design.md)

## Impact

- **Framework bundle**: `contracts.yaml` additions; template fields in `TASK.md` and `plan.md`; router guidance in `.ai/templates/adapters/codex/AGENTS.md` and `.ai/custom/` conventions; new deterministic checks in `.ai/tools/` (Python, model-free); `RUNBOOK.md` and `FRAMEWORK.md` documentation.
- **Generated adapters**: consumer projects pick the changes up through adapter sync; `.ai/framework.lock` is recomputed. No manual editing of generated files.
- **Existing consumer projects**: new fields default conservatively (absent follow-up/focus data must not block acceptance), following the established legacy-task pattern — no bulk rewriting of accepted history.
- **Tests**: Python unit tests and Node contract tests covering the new helpers and template contracts, matching the existing `tests/` layout.
