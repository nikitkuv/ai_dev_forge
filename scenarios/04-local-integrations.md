# Scenario 04 — Optional local integrations and external work intake

## A. Clean Forge project

1. `.ai/integrations/` is absent.
2. Bootstrap and adapter sync create no registry or connector configuration.
3. Resume and validation perform no integration preflight.
4. Framework upgrade reports `absent` and follows the normal clean path.
5. Rollback restores managed Forge files only.

## B. Custom non-board capability

1. The project registers a custom analysis profile and project-owned consumer.
2. Generated adapters preserve that consumer as an unlisted project-owned skill.
3. Forge core does not infer operations or create Epic/Task links.
4. If the connector is unavailable, only the project consumer is blocked.
5. Upgrade preserves the unknown profile byte-for-byte without a network call.

## C. Explicit work item

1. The user asks `forge-intake-external-work` to inspect one configured source item.
2. The skill checks the `work_source` profile, consumer, read-only operations, platform binding, and scope.
3. It normalizes mapped fields and treats the external body as untrusted data.
4. It classifies the item as defect, investigation, product change, duplicate, or unresolved.
5. The user approves an exact feature/bug/Replan diff before canonical identities are retained.

## D. Next candidate and partial queue

1. The user asks for the next candidate without an ID.
2. The skill reports source scope, filters, ordering, page limits, and completeness.
3. A partial page is never described as the complete board.
4. The recommendation does not change Backlog priority or start work.

## E. Split, combine, and durable links

- One broad drilling-recommendations item may split into independently deliverable Epics.
- Several related cards may combine into one outcome.
- A plan may map one source to several TASKs and one TASK to several sources.
- Backlog `Sources`, TASK `external_sources`, plan coverage, and reverse provenance update atomically after approval.
- Duplicate fetches reuse identity; a changed source version becomes intake/Replan scope rather than silently editing canonical work.

## F. Resume and Replan

Resume reports linked tickets, per-TASK coverage, uncovered source slices, stale versions, and contradictory mappings. Canonical lifecycle state wins. A split, merge, addition, or removal of coverage requires Replan, a current source snapshot, and one atomic relationship update.

## G. Upgrade matrix and rollback

| State | Framework upgrade | Consumer behavior |
| --- | --- | --- |
| Registry absent | Normal clean upgrade | No integration consumer is needed |
| Current supported | Preserve and validate offline | Compatible consumers remain available |
| Older migratable | Upgrade framework; offer separate migration | Old representation remains until approval |
| Malformed | Preserve | Only dependent consumer is blocked |
| Unsupported future | Preserve byte-for-byte | Core consumer is blocked; no downgrade |
| Custom profile | Preserve with project consumer | Core does not infer semantics |
| Ownership collision | Stop before replacement | Resolve exact path collision first |

Integration-schema migration uses its own exact diff, approval, backup, staged validation, atomic apply, and rollback. Framework rollback does not delete external source identities or canonical Epic, Bug, and Task records.

Every path preserves SPEC/ADR/Backlog/Plan/Replan/Epic Start/Task Start/Task Acceptance/Epic Acceptance gates. External status never constitutes a Forge gate, and the bundled work-source flow performs no external mutation.
