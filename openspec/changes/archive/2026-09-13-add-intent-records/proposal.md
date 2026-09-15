# Add Intent Records (INT-NNNN)

## Why

Feature and product-change requests arriving during ongoing development lose their narrative. The intake conversation — motivation, constraints, considered alternatives, open questions — lives only in the chat session. `SPEC.md` records terse approved criteria (`FR-*`/`NFR-*`/`BR-*`), and a Backlog row records one line of intended outcome. When a session dies mid-intake, or when `forge-prepare-epic` runs months later, the planner must re-derive or re-ask context that was already discussed. Rejected and deferred ideas leave no durable trace, so the same request can be re-discussed from scratch.

## What Changes

- New project-owned evidence artifact `intents/INT-NNNN-<short-name>.md` following a bounded one-page template: problem/motivation in the user's words, proposed observable outcome, affected users/systems, constraints, considered alternatives, open questions, outcome history.
- `forge-intake-feature` and `forge-intake-external-work` record an INT as the first durable output of intake: the ID is reserved immediately, the template is filled through a proportionate interview, and the finalized INT is confirmed by the user before Backlog retention.
- Rejected, deferred, and superseded requests are retained as INT records with a short rationale; no Epic is created for them.
- The Backlog Epic Roadmap gains an optional `Intent` column linking `INT-NNNN` (backward compatible, same pattern as `Sources` and `Research`).
- `forge-prepare-epic` reads the linked INT as a primary planning input alongside `SPEC.md`.
- `forge.py next-id` allocates `int` IDs; `validate` checks INT structure and reference integrity (`promoted_to`, `research_refs`).
- INT is evidence only: it never controls lifecycle state, priority, readiness, or acceptance. Approved criteria remain only in `SPEC.md`; implementation strategy remains only in `plan.md`.
- Bug intake and bootstrap are unchanged. Migration from v4.9 requires no backfill.

## Capabilities

### New Capabilities

- `intent-records`: capture, structure, outcomes, retention, and boundaries of intent records; how intake skills create them through interview; how planning consumes them; how rejected requests are retained for dedup and history.

### Modified Capabilities

- `external-work-intake`: external-work intake now records an INT for each product-change candidate (retained or rejected) before any canonical changes.

## Impact

- Framework bundle: new `.ai/templates/INTENT.md`; `manifest.yaml` (ownership, template list); `contracts.yaml` (intent contract); skills `forge-intake-feature`, `forge-intake-external-work`, `forge-prepare-epic`; `.ai/tools/forge.py` (`next-id int`, INT structural validation) and its unit tests.
- Consumer project layout: new optional project-owned `intents/` folder; optional Backlog `Intent` column.
- Documentation: `FRAMEWORK.md` (project structure, sources of truth, skills), `README.md`, `RUNBOOK.md` (intake scenario), `MIGRATION.md` (v4.9 → v4.10), `scenarios/`.
- No breaking changes: existing projects without an `intents/` folder or `Intent` column remain valid.
