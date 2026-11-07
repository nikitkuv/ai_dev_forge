# Process Fix Follow-up Specification

## Purpose

Turns delivery failures into durable process fixes by requiring a root-cause classification and a routed disposition at acceptance, so the same mistake does not recur.

## Requirements

### Requirement: Missed goals despite passing checks require a recorded follow-up

When a delivery misses its goal despite green checks — the user requests changes at Task or Epic Acceptance because the delivered behavior is wrong while verification passed — the acceptance record SHALL include a process follow-up before the work item reaches its terminal state. The follow-up SHALL record a root-cause category from a defined set: task ambiguity, missing repository context, missing acceptance criterion, weak test oracle, rule drift, or other.

#### Scenario: Wrong behavior despite green tests
- **WHEN** the user rejects acceptance because the delivered behavior missed the goal while selected checks passed
- **THEN** the acceptance record gains a process follow-up with a root-cause category before the Task can reach `DONE`

#### Scenario: Successful delivery records no follow-up
- **WHEN** the user accepts the delivery with no process miss
- **THEN** the acceptance record may state that no follow-up is needed and acceptance is not delayed

### Requirement: Follow-ups route their fix to an owned process target

Each recorded follow-up SHALL name where the fix belongs from a defined set: a skill, a template field, a contract, a neutral instruction, a regression test, or no process change with rationale. Mechanical error classes SHALL prefer a deterministic helper plus regression test; judgment error classes SHALL prefer a focused neutral-instruction correction. Applying the fix is a separate authorized change and SHALL NOT occur automatically during acceptance.

#### Scenario: Mechanical error routed to a regression test
- **WHEN** the root cause is a mechanical error a helper could have caught
- **THEN** the follow-up routes to a deterministic helper plus regression test and names them as the fix target

#### Scenario: Judgment error routed to a neutral instruction
- **WHEN** the root cause is a recurring judgment error by the agent
- **THEN** the follow-up routes to a focused neutral-instruction correction and names the instruction to change

#### Scenario: Fix applied as a separate change
- **WHEN** a follow-up names its fix target
- **THEN** the fix is applied only through an explicit user-authorized change outside the acceptance mutation

### Requirement: Follow-ups remain visible until applied or declined

Recorded follow-ups SHALL remain visible in the work item's acceptance history with their disposition state. An unapplied follow-up SHALL be surfaced by framework conformance checking as an advisory item, never as a lifecycle failure.

#### Scenario: Unapplied follow-up surfaced
- **WHEN** a recorded follow-up has no applied fix and no decline rationale
- **THEN** the conformance check lists it as an advisory pending item without blocking any gate

### Requirement: Legacy acceptance records stay valid

Acceptance records created before this capability existed SHALL remain valid without backfill. A missing follow-up field SHALL NOT block acceptance, commit, or completion transitions.

#### Scenario: Legacy task accepted without follow-up
- **WHEN** a Task created before this capability reaches acceptance with no follow-up field
- **THEN** acceptance proceeds and no follow-up is inferred
