# Lifecycle Scripting Specification

## Purpose

Deterministic local execution of already-approved Forge lifecycle mutations: status transitions in TASK files and the Backlog, Epic workspace moves, acceptance recording, and scoped commits. Scripts execute explicit user/orchestrator decisions through preview/apply; they never authorize, infer, or decide a transition.

## Requirements

### Requirement: Lifecycle mutations execute only reviewed previews

Every mutating helper command SHALL first produce a preview containing the exact planned file edits, the mechanically checked preconditions, and a token bound to the current inputs and planned outputs. Applying SHALL require that exact token. A change to any referenced input after preview SHALL invalidate the token and fail the apply before any write. Previews SHALL perform no writes.

#### Scenario: Task transition applied
- **WHEN** the orchestrator previews a TASK transition to `IN PROGRESS` and applies the returned token
- **THEN** only that TASK's frontmatter and recorded gate fields change, and the result reports the new status and recorded fields

#### Scenario: Stale preview rejected
- **WHEN** the TASK file changes between preview and apply
- **THEN** apply fails without writing and reports which input changed

### Requirement: Transition preconditions are checked mechanically

The helper SHALL verify, before applying a transition: the target status is a legal enum value, the current status matches the transition's declared source, single-writer invariants hold (at most one code-writing TASK `IN PROGRESS`, at most one nonterminal active-work Epic), and Backlog/workspace consistency remains valid after the edit. Violations SHALL fail the preview with the exact violated invariant. The helper SHALL NOT evaluate semantic gates — review protocol completeness, test integrity, evidence quality, or user authorization — which remain orchestrator and user judgments.

#### Scenario: Illegal target rejected
- **WHEN** a transition requests a status outside the contract enums
- **THEN** the preview fails and names the invalid status

#### Scenario: Second concurrent writer rejected
- **WHEN** a Task transition to `IN PROGRESS` is requested while another code-writing TASK is already `IN PROGRESS`
- **THEN** the preview fails with the single-writer invariant and the conflicting TASK path

### Requirement: Epic workspace moves are atomic logical transitions

Epic activation and completion SHALL execute as one logical operation: move the workspace directory between `execution/` states, update the Epic's Backlog row to the matching status, and re-run structural validation. Any failure during the operation SHALL restore the complete prior state — directory location and Backlog row. A crashed partial operation SHALL be recoverable and recovery SHALL refuse to overwrite subsequent user edits.

#### Scenario: Epic Start happy path
- **WHEN** Epic Start is applied for an eligible `PLANNED + READY` Epic with satisfied dependencies
- **THEN** the workspace moves to `execution/active/`, the Backlog row becomes `ACTIVE`, and validation passes as one reported transition

#### Scenario: Validation failure rolls back
- **WHEN** structural validation fails after the directory move
- **THEN** the workspace returns to `execution/planned/`, the Backlog row returns to `PLANNED`, and the failure is reported

### Requirement: Acceptance recording never infers the decision

The acceptance helper SHALL append the user-supplied acceptance record — accepting user or role, decision reference, date, notes, final revision/fingerprint — to the TASK's acceptance history and transition only that TASK to `DONE`. It SHALL accept these facts as explicit inputs and SHALL NOT derive acceptance from passing checks, fingerprints, or evidence. Resolving a linked `SCHEDULED` Bug SHALL be an explicit input, never a side effect.

#### Scenario: Acceptance recorded from explicit decision
- **WHEN** the user explicitly accepts a TASK and the orchestrator passes the decision facts to the helper
- **THEN** the TASK records the acceptance and becomes `DONE`, and unrelated Bugs are unchanged

#### Scenario: Missing explicit decision facts rejected
- **WHEN** acceptance inputs lack an accepting user or decision reference
- **THEN** the helper refuses to record acceptance and reports the missing fields

### Requirement: Scoped commits exclude unrelated changes

The scoped-commit helper SHALL stage exactly the paths recorded as the accepted TASK's scope (or an explicit path list for a direct-fix investigation), verify the staged set contains no unrelated tracked changes, and commit only under the configured Git policy with its required preconditions. Under a `manual` policy or without the required authorization inputs it SHALL perform no commit and report the exact staged set it would have committed.

#### Scenario: Unrelated dirty file excluded
- **WHEN** the working tree contains an unrelated modified file outside the TASK's recorded scope
- **THEN** the commit includes only the recorded scoped paths and reports the excluded change

#### Scenario: Manual policy performs no commit
- **WHEN** the configured Git policy is `manual`
- **THEN** the helper stages nothing, commits nothing, and reports the scoped paths for the user's separate commit decision

### Requirement: Every mutation leaves a recovery journal

Each applied mutation SHALL write a backup journal under `.ai/local/` before editing and clear it after a fully confirmed transition. A caught failure SHALL roll back written files from the journal. An interrupted operation SHALL leave the journal for explicit recovery, and recovery SHALL refuse to overwrite files modified after the crash.

#### Scenario: Rollback on caught failure
- **WHEN** a mutation fails partway through its planned writes
- **THEN** already written files are restored from the journal and the failure names the failed step

#### Scenario: Recovery respects later edits
- **WHEN** recovery finds a file changed after a crash
- **THEN** recovery stops and reports the conflict instead of overwriting the newer content
