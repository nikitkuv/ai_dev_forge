---
name: forge-resume-development
description: Recover planned, active, or paused Forge development state after interruption or in a new session, including the queued planned workspaces, current gate, evidence, and uncommitted changes.
---

# Resume Development

## Reconstruct state from durable evidence

1. Ask `context-collector` to read `BACKLOG.md`, all execution directories, every planned workspace, the active or paused Epic plan and TASK files, relevant ADRs, and Git status and diff.
2. Treat session history as optional context, never as the source of truth.
3. Determine:
   - every queued planned workspace in Backlog priority and row order, whether it is still `PLANNED + READY`, and its Epic Start dependencies and blockers;
   - the active or paused Epic and whether its Backlog status matches its directory;
   - ordered Tasks and their sole lifecycle statuses;
   - dependencies and blockers;
   - the current gate from TASK Workflow State and Epic state;
   - implementation revision and fingerprint;
   - current Review Packet, structured review, selected Task-testing, Epic Validation, fuzzing, and user-validation evidence;
   - selected quality profiles, Task verification selections, Epic Verification Plan, and any unresolved command configuration;
   - staged, unstaged, and untracked changes relevant to the work.
4. Report duplicate Epic workspaces, planned directories without `PLANNED + READY` Backlog entries, planned workspaces with non-approved definitions, duplicate active Epics, invalid transitions, mismatched directories, stale fingerprints, broken links, or conflicting canonical facts before continuing.

## Determine the safe continuation point

- Treat an agent stage as incomplete when its result was not persisted into the applicable TASK or Epic plan.
- Treat an approved `execution/planned/` workspace as pending Epic Start, not as active work. Never start its first Task directly.
- Re-evaluate dependencies and `Blocked by` before offering Epic Start; Backlog order, not filesystem order, determines the next queued candidate.
- Rerun structured review or selected Task testing when evidence is missing, refers to another revision/fingerprint, or affected code changed afterward.
- Rerun Epic Validation when aggregate evidence is missing, commands or profile gates are unresolved, the fingerprint changed, or a migrated pre-v4 plan lacks the required verification contract.
- Never enter or resume fuzzing without current passing Epic Validation evidence on the same aggregate fingerprint. Rerun Epic Validation and fuzzing when Epic code changed after either result.
- Keep a TASK at `AWAITING USER ACCEPTANCE` while the user is still validating; no timeout applies.
- Require explicit user authorization before resuming a `PAUSED` Epic or TASK, starting a `TODO` TASK, accepting work, replanning, or crossing another gate.
- Do not infer acceptance or completion from a clean Git tree, a prior chat message, or an agent invocation alone.

Present a compact recovery summary with canonical paths, the ordered planned queue and eligibility, current active/paused state, inconsistencies, unfinished changes, evidence that remains valid, evidence that must be rerun, and the next required user decision.

Do not modify canonical status merely to make files consistent. Apply corrections only through the appropriate lifecycle or Replan gate. Create no recovery or progress report file.
