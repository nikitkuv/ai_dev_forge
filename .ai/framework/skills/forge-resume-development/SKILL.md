---
name: forge-resume-development
description: Recover the durable development state of an initialized Forge project after interruption or in a new session. Use before continuing work when the active Epic, current TASK, pending gate, agent evidence, or uncommitted changes must be reconstructed.
---

# Resume Development

## Reconstruct state from durable evidence

1. Ask `context-collector` to read `BACKLOG.md`, execution directories, the active or paused Epic plan, every TASK in that Epic, relevant ADRs, and Git status and diff.
2. Treat session history as optional context, never as the source of truth.
3. Determine:
   - the active or paused Epic and whether its Backlog status matches its directory;
   - ordered Tasks and their sole lifecycle statuses;
   - dependencies and blockers;
   - the current gate from TASK Workflow State and Epic state;
   - implementation revision and fingerprint;
   - current review, testing, fuzzing, and user-validation evidence;
   - staged, unstaged, and untracked changes relevant to the work.
4. Report duplicate active Epics, invalid transitions, mismatched directories, stale fingerprints, broken links, or conflicting canonical facts before continuing.

## Determine the safe continuation point

- Treat an agent stage as incomplete when its result was not persisted into the applicable TASK or Epic plan.
- Rerun review or testing when evidence is missing, refers to another revision/fingerprint, or code changed afterward.
- Rerun fuzzing when Epic code changed after the recorded fuzzing result.
- Keep a TASK at `AWAITING USER ACCEPTANCE` while the user is still validating; no timeout applies.
- Require explicit user authorization before resuming a `PAUSED` Epic or TASK, starting a `TODO` TASK, accepting work, replanning, or crossing another gate.
- Do not infer acceptance or completion from a clean Git tree, a prior chat message, or an agent invocation alone.

Present a compact recovery summary with canonical paths, current state, inconsistencies, unfinished changes, evidence that remains valid, evidence that must be rerun, and the next required user decision.

Do not modify canonical status merely to make files consistent. Apply corrections only through the appropriate lifecycle or Replan gate. Create no recovery or progress report file.
