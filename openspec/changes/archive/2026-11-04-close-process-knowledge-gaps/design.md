# Design — close-process-knowledge-gaps

## Context

See proposal.md for motivation. Conventions that shape this design: framework-owned vs project-owned ownership split (`.ai/custom/` is project-owned and survives updates); generated adapters are never hand-edited; deterministic helpers report mechanical coverage and leave judgment to the orchestrator; authorization and acceptance always stay with the user; the generated router has a hard line budget; "do not create an automatic growing memory"; legacy records tolerate missing new fields (the `delivery_track` precedent: absent → conservative default, no bulk rewriting of accepted history).

## Goals / Non-Goals

**Goals:**
- Stated rules and actual code cannot silently disagree.
- A missed goal despite green checks always produces a durable process fix or a recorded refusal.
- Human acceptance attention is directed at project-declared critical surfaces.

**Non-Goals:**
- No automatic memory, telemetry-driven learning, or self-modifying instructions.
- No new mandatory human gate on successful work paths (the rituals fire on demand or on failure).
- No semantic/ML-based rule checking — patterns only; interpretation stays with the orchestrator.
- No changes to delivery tracks, review gating scope, or any existing assurance requirement.
- No automatic edits to canonical documents or skills during acceptance.

## Decisions

### D1: Rules are declared in `.ai/custom/rules.yaml`, statements live in the router overlay

Each rule entry has `id`, `statement`, optional `pattern` (Python `re`), `scope` (path globs), optional `exclusions`, and a `kind` of `code` or `process`. Rule statements render as a compact "Project Rules" block in `.ai/custom/router-shared.md` (agents see them within the line budget); patterns and scopes stay in `rules.yaml` (machine-checkable). The drift check cross-links statement and pattern by `id`, and conformance reports when the router block and `rules.yaml` diverge.

*Alternatives:* rules inline in the router overlay only (rejected — not machine-checkable and budget-hostile); rules in framework-owned `CONVENTIONS.md` (rejected — project rules are project-owned); pattern-first rules with generated statements (rejected — statements must be human-authored for judgment quality).

### D2: The drift check is a model-free helper in the structural-validation family

A `forge.py` read-only subcommand compares patterns against scoped paths and reports per rule: matches, violation count, violating paths, and unverifiable rules as `judgment`. It writes nothing, performs no model calls, and changes no lifecycle state — the same discipline as mutation testing. `forge-check-framework` includes the drift report in its conformance coverage.

*Alternatives:* CI-only checking (rejected — local-first tooling; CI is optional consumer infrastructure); a standalone script outside `.ai/tools/` (rejected — bundle cohesion and shared fingerprint/index utilities).

### D3: Process follow-up is a structured acceptance field with routed dispositions

`TASK.md` gains a `Process Follow-up` block (root-cause category, fix target, disposition state, rationale) next to User Validation; `plan.md` gains the same facts in Epic User Validation History. Enums live in `contracts.yaml`: root causes `task_ambiguity`, `missing_repo_context`, `missing_acceptance_criterion`, `weak_test_oracle`, `rule_drift`, `other`; fix targets `skill`, `template_field`, `contract`, `neutral_instruction`, `regression_test`, `no_process_change`. `forge-complete-task` / `forge-complete-epic` require a recorded follow-up before `DONE` / `COMPLETED` only when the user rejected or corrected the delivery; successful acceptance may record `no_process_change`. Fix application is always a separate authorized change. The mechanical-vs-judgment routing rule from `forge-check-framework` (helper plus regression test vs neutral-instruction correction) becomes normative here.

*Alternatives:* a separate retrospective document (rejected — unbounded memory pattern); auto-applying skill fixes during acceptance (rejected — breaks the authorization model); a free-text notes line (rejected — unqueryable, and the conformance check needs structured dispositions to surface pending ones).

### D4: Critical surfaces are a section of `ARCHITECTURE.md`

A "Critical Surfaces" section lists named areas (architecture boundaries, billing, data model, …) each with a reference to its canonical architecture section. `epic-planner` folds intersecting surfaces into Task Review Focus; `forge-run-task` / `forge-complete-task` group Manual Verification and acceptance presentation by touched surfaces, presenting them first. This is deliberately distinct from the per-Epic "critical user or system paths" already in `plan.md`: those are epic-scoped validation targets; these are stable, project-scoped human attention targets.

*Alternatives:* `.ai/project.yaml` (rejected — it owns execution config; critical surfaces are architecture knowledge with prose references and belong in the ownership table under ARCHITECTURE); a standalone file (rejected — no ownership slot in the sources-of-truth table, and one more file to drift).

### D5: All additions are optional and legacy-tolerant

Empty or absent declarations behave exactly like today: no rules → drift check reports "no declared rules"; no critical surfaces → current Review Focus and presentation flows; no follow-up on a legacy TASK → acceptance proceeds. No backfill of accepted history.

## Risks / Trade-offs

- [Ritual overhead grows] → nothing is added to the per-TASK success path except the follow-up field, which is empty when nothing failed.
- [`rules.yaml` becomes a junk drawer] → the no-growing-memory principle applies to rules; the budget helper detects router growth; every violated rule forces a disposition, so unused rules get amended or removed rather than accumulating.
- [Regex false positives erode trust in the drift check] → report-only output, `exclusions` per rule, judgment fields preserved; no gate blocks on raw pattern matches.
- [Follow-ups recorded but never applied] → conformance reports pending follow-ups as advisory; disposition state (`applied` / `declined`) is part of the record.
- [Critical surfaces go stale or too broad] → they are a small maintained section of an already-maintained document; the empty-declaration fallback keeps the feature safely inert.
- [Router budget pressure from rule statements] → statements are single short lines; patterns never render into the router; the budget helper flags growth before it becomes a problem.

## Migration Plan

1. Ship the framework bundle (skills, templates, contracts, tools, docs) as a normal framework release; consumer projects pick it up through the existing `MIGRATE.md` preview/apply flow, which adds new sections and fields additively with backup journals.
2. Run adapter sync so the router overlay section and lock hashes regenerate.
3. Rollback: the additions are additive and optional — removing the updated bundle restores prior behavior with no data repair; migration journals already cover the file set.
