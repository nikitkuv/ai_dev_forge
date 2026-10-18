## MODIFIED Requirements

### Requirement: Epic workspace moves are atomic logical transitions

Epic activation and completion SHALL execute as one logical operation: move the workspace directory between `execution/` states, update the Epic's Backlog row, and re-run structural validation. Epic completion and cancellation SHALL additionally move the Backlog row into `BACKLOG-ARCHIVE.md` — creating the archive file if absent — inside the same logical operation, so the live Backlog never retains a terminal Epic row after apply. Any failure during the operation SHALL restore the complete prior state — directory location, Backlog row, and archive file. A crashed partial operation SHALL be recoverable and recovery SHALL refuse to overwrite subsequent user edits.

#### Scenario: Epic Start happy path
- **WHEN** Epic Start is applied for an eligible `PLANNED + READY` Epic with satisfied dependencies
- **THEN** the workspace moves to `execution/active/`, the Backlog row becomes `ACTIVE`, and validation passes as one reported transition

#### Scenario: Completion archives the row as part of the transition
- **WHEN** Epic Acceptance is applied and the Epic becomes `COMPLETED`
- **THEN** the workspace moves to `execution/completed/` and the Backlog row moves to `BACKLOG-ARCHIVE.md` in one reported transition
- **AND** the live `BACKLOG.md` contains no `COMPLETED` row for that Epic

#### Scenario: Validation failure rolls back
- **WHEN** structural validation fails after the directory move and archive append
- **THEN** the workspace returns to its prior `execution/` location, the Backlog row returns to its prior live state, and the archive returns to its prior content

## ADDED Requirements

### Requirement: Terminal Backlog transitions archive their row in the same mutation

Any reviewed mutation that sets a Backlog row to a terminal status — any terminal Bug status, Epic `CANCELLED` without a workspace move — SHALL include the row's move to `BACKLOG-ARCHIVE.md` in the same preview and apply. The preview SHALL show the exact live Backlog and archive edits together; the apply token SHALL bind to both files, so a change to either after preview invalidates the token before any write. Rollback and journal rules apply to both files as one unit.

#### Scenario: Bug resolution archives atomically
- **WHEN** an approved edit sets `BUG-012` to a terminal status and the token is applied
- **THEN** the live Defect Queue loses the row and the archive gains it in one applied mutation

#### Scenario: Archive change invalidates a pending preview
- **WHEN** `BACKLOG-ARCHIVE.md` changes between preview and apply of a Bug resolution
- **THEN** apply fails without writing and reports the changed input
