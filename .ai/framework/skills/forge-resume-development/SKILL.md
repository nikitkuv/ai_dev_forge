---
name: forge-resume-development
description: Recover planned, active, or paused Forge development state after interruption or in a new session, including the queued planned workspaces, current gate, evidence, and uncommitted changes.
---

# Resume Development

## Reconstruct state from durable evidence

1. Ask `context-collector` to read `BACKLOG.md`, all execution directories, every planned workspace, the active or paused Epic plan and TASK files, relevant ADRs, optional `.ai/integrations/` definitions/state, and Git status and diff.
2. Treat session history as optional context, never as the source of truth.
3. Determine:
   - every queued planned workspace in Backlog priority and row order, whether it is still `PLANNED + READY`, and its Epic Start dependencies and blockers;
   - the active or paused Epic and whether its Backlog status matches its directory;
   - ordered Tasks and their sole lifecycle statuses;
   - each approved delivery track, rationale, fast eligibility/disqualifier evidence, escalation history, and legacy missing-track interpretation as standard;
   - dependencies and blockers;
   - the current gate from TASK Workflow State and Epic state;
   - implementation revision, whole-implementation fingerprint, production-surface fingerprint, path classification, and any ambiguous-path rationale;
   - current Fast Assurance Summary or standard Review Packet, structured review and selected Task-testing, plus Epic Validation, fuzzing, and user-validation evidence;
   - selected quality profiles, Task verification selections, Epic Verification Plan, Epic Fuzzing Plan, every final Task fuzzing impact and smoke result, and any unresolved command configuration;
   - staged, unstaged, and untracked changes relevant to the work.
   - for configured `work_source` integrations, linked source keys, per-TASK coverage, uncovered source slices, last reviewed source versions, and forward/reverse mapping integrity.
4. Report duplicate Epic workspaces, planned directories without `PLANNED + READY` Backlog entries, planned workspaces with non-approved definitions, duplicate active Epics, invalid transitions, mismatched directories, stale fingerprints, broken links, contradictory source mappings, or conflicting canonical facts before continuing. An unavailable or invalid integration blocks only work that consumes it; absence of `.ai/integrations/` is the clean baseline.

## Determine the safe continuation point

- Treat an agent stage as incomplete when its result was not persisted into the applicable TASK or Epic plan.
- Treat a legacy TASK without `delivery_track` as standard. Never synthesize fast eligibility or assurance from prior implementation, review, testing, risk labels, or session history.
- Treat an approved `execution/planned/` workspace as pending Epic Start, not as active work. Never start its first Task directly.
- Re-evaluate dependencies and `Blocked by` before offering Epic Start; Backlog order, not filesystem order, determines the next queued candidate.
- Rerun structured review when it is missing, packet integrity is incomplete, legacy evidence lacks a production fingerprint, or the production-surface fingerprint changed. Preserve a protocol-complete clean review across supporting-only revisions with the same production fingerprint; invalidate affected testing and rerun selected Task testing without another strong-review invocation. Testing must always match the current implementation revision and whole-implementation fingerprint.
- For fast, repeat eligibility validation and orchestrator assurance when either is missing, stale, incomplete, or bound to another whole-implementation fingerprint. Any disqualifier, unexpected affected surface, unexplained check failure, missing test integrity, or unresolved verification escalates fast to standard and invalidates fast assurance. Unchanged-scope escalation needs no Replan; scope changes do. Standard to fast after Task Start is forbidden.
- Rerun Epic Validation when aggregate evidence is missing, commands or profile gates are unresolved, the fingerprint changed, or a migrated pre-v4 plan lacks the required verification contract.
- Never enter or resume the fuzzing gate without current passing Epic Validation evidence on the same aggregate fingerprint. For approved `not applicable`, reconstruct the skip conditions from final Task impacts, actual affected surfaces, alternative coverage, and fingerprint; invoke the fuzzer if any condition is missing, stale, unresolved, applicable, or contradictory. Rerun Epic Validation and the fuzzing gate when Epic code changed after either result.
- Keep a TASK at `AWAITING USER ACCEPTANCE` while the user is still validating only while its track-specific evidence remains current; no timeout applies.
- Require explicit user authorization before resuming a `PAUSED` Epic or TASK, starting a `TODO` TASK, accepting work, replanning, or crossing another gate.
- Do not infer acceptance or completion from a clean Git tree, a prior chat message, or an agent invocation alone.
- Do not infer Forge lifecycle state from an external item. Canonical Backlog, plan, and TASK state wins; relationship repair or changed source coverage requires an explicit intake/Replan reconciliation.

Present a compact recovery summary with canonical paths, the ordered planned queue and eligibility, current active/paused state, inconsistencies, unfinished changes, evidence that remains valid, evidence that must be rerun, and the next required user decision.

Do not modify canonical status merely to make files consistent. Apply corrections only through the appropriate lifecycle or Replan gate. Create no recovery or progress report file.
