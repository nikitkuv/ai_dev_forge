# Design: Intent Records

## Context

Forge already has two durable evidence patterns this change builds on: `INV-NNNN` investigations (standalone narrative records with outcomes and reference linking) and the optional Backlog column pattern (`Sources`, `Research`) that migrated in without backfill. Intake skills (`forge-intake-feature`, `forge-intake-external-work`) already run a discovery interview; today its narrative is discarded — only a one-line Backlog row and an optional SPEC diff survive. `forge.py` already allocates monotonic IDs (`next-id`) and structurally validates evidence records (`INV`, mutation registry). The framework is versioned (v4.9.0) with a lock/hash mechanism and a separate migration workflow.

## Goals / Non-Goals

**Goals:**

- Make the request narrative durable from the first minutes of intake (session-death safe).
- Reuse the INV pattern so INT needs no new state machinery, gates, or skills.
- Keep SPEC/plan/INT ownership boundaries disjoint so records stay bounded.
- Retain rejected/deferred requests cheaply for dedup and decision history.

**Non-Goals:**

- Capturing the initial bootstrap product interview (it produces a full SPEC once).
- Intent records for bugs (Defect Queue rows + INV already cover them).
- Deleting or archiving intent records; any archive mechanism is a future migration.
- Any automated/CI intent generation or INT-driven lifecycle automation.

## Decisions

### D1: INT mirrors the INV pattern exactly

`intents/INT-NNNN-<short-name>.md`, project-owned, monotonic global IDs reserved via `forge.py next-id`, one current `outcome` plus dated outcome history, optional `research_refs` to `INV-NNNN`. Alternative — embedding the narrative inside the Epic workspace under `execution/planned/` — rejected: the narrative must exist before any Epic exists (OUTLINE ideas, rejected requests have no Epic) and must survive without execution state.

### D2: INT creation is a phase of existing intake skills, not a new skill

`forge-intake-feature` and `forge-intake-external-work` gain an early "record the intent" phase: reserve ID → fill template by proportionate interview → user confirms the assembled record → existing gates proceed unchanged (retention approval → SPEC diff → OUTLINE/READY). Alternative — a separate `forge-intake-intent` skill — rejected: it would add a skill and a hand-off without adding a gate or authority, and the interview already lives in intake. The confirmation of the finalized INT is a content check ("this is what I meant"), not a new lifecycle gate.

### D3: Direct file creation, no journal transaction

Unlike `inv-create`, INT files are created by direct orchestrator write after `next-id`: an INT is a new standalone file that mutates no shared canonical state (no Backlog/execution edits ride on it). Structural correctness is enforced by `validate`, not by a transaction. If INTs ever participate in combined canonical updates, a transactional helper can be added then.

### D4: Bounded template with disjoint ownership

`.ai/templates/INTENT.md` (framework-owned) fixes the section list — problem/motivation, proposed outcome, affected users/systems, constraints, considered alternatives, open questions, outcome history — and targets one page. Ownership rule: approved criteria exist only in `SPEC.md`, implementation strategy only in `plan.md`; the INT references (`FR-*` IDs, `promoted_to`) instead of copying. This rule is what keeps the folder from growing into a shadow SPEC; `validate` warns on oversized records as an advisory finding.

### D5: Outcomes and retention

`draft → accepted → promoted` plus terminal-ish `rejected` / `deferred` / `superseded`, transitions kept in outcome history (INV-style). Records are never deleted; `rejected` requires a one-line rationale. The bar for creating an INT at all is "material": a request that could affect SPEC, ARCHITECTURE, or Epic scope — the same trigger that already routes a request into `forge-intake-feature`; trivial conversational asks do not get records.

### D6: Optional `Intent` Backlog column, no backfill

Same migration pattern as `Sources`/`Research`: column optional, existing Backlogs valid, backfill unnecessary. `forge-prepare-epic` treats the linked INT as a primary input; `OUTLINE → READY` additionally requires no material open questions in the linked record.

### D7: Tooling scope

`next-id` gains the `int` type (4-digit, `INT-0001`). `validate` checks INT structure: required frontmatter, allowed outcome values, existing `promoted_to` target, resolvable `research_refs`, template section presence. Findings are advisory; Python never mutates records.

### D8: Versioning

Manifest bumps to `4.10.0`; `MIGRATION.md` documents the optional folder/column. `forge-migrate-framework` upgrade does not create `intents/` or modify existing Backlogs.

## Risks / Trade-offs

- [INT grows into a parallel SPEC] → D4 ownership rule + oversized-record advisory in `validate` + skill text explicitly forbidding criteria duplication.
- [Ceremony overhead on small requests] → D5 materiality bar; proportionate interview; well-specified requests need only confirmation.
- [Rejected-record accumulation feels like clutter] → records are kilobytes; dedup value is the payoff; archive can be a later migration (non-goal now).
- [Interview duplicates what external-work intake already asks] → the normalized-ticket evidence fills template sections first; the interview asks only what the ticket and repository cannot resolve.

## Migration Plan

Pure addition; no rollback complexity. Consumers on v4.9 keep working untouched (no `intents/`, no column). Rollback = removing the folder/column; nothing else references INTs except optional links.

## Open Questions

- Whether a future `int-create` transactional helper is warranted (only if INTs join combined canonical updates) — deferrable, does not affect specs or tasks.
