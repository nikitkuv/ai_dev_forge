## Purpose

Keeps the live `BACKLOG.md` bounded to the active horizon by mechanically moving terminal rows into an append-only, year-sectioned `BACKLOG-ARCHIVE.md`, without deleting records, breaking identifier monotonicity, or turning archival into a separate user ritual.

## ADDED Requirements

### Requirement: Terminal rows leave the live Backlog on the terminal transition

When a Backlog row reaches a terminal status — Epic `COMPLETED` or `CANCELLED`; Bug `RESOLVED`, `REJECTED`, `DUPLICATE`, or `WONT_FIX` — through an approved transition, the row SHALL be removed from the live `BACKLOG.md` and present in `BACKLOG-ARCHIVE.md` as part of that same transition. Archival SHALL NOT be a separately scheduled compaction step: no approved terminal transition may leave a terminal row in the live file. Terminal rows that predate this behavior (legacy state) remain in the live file until explicitly backfilled.

#### Scenario: Epic completion compacts the live Backlog
- **WHEN** Epic Acceptance completes `EPIC-004` and the transition is applied
- **THEN** no `EPIC-004` row remains in `BACKLOG.md`
- **AND** the row is present under the current year section of `BACKLOG-ARCHIVE.md`

#### Scenario: Bug resolution compacts the live Backlog
- **WHEN** `BUG-012` reaches a terminal status through an approved Backlog edit
- **THEN** the live Defect Queue no longer contains `BUG-012`
- **AND** the row is present in `BACKLOG-ARCHIVE.md`

### Requirement: The archive is append-only and format-preserving

`BACKLOG-ARCHIVE.md` SHALL use the same table columns as the corresponding live Backlog section, split into one section per year. A moved row SHALL be copied verbatim without content transformation. The archive SHALL only ever gain rows; structural validation SHALL report edited or removed archived rows as conformance violations. Rows are never deleted: Git keeps file history and the archive keeps the record surface.

#### Scenario: Row lands verbatim in the current year section
- **WHEN** a terminal row is archived
- **THEN** the appended row matches the prior live row column-for-column under the current year heading

#### Scenario: Archive tampering detected
- **WHEN** validation finds an archived row modified or absent relative to the journal record
- **THEN** validation reports the archive path and the violated rule

### Requirement: Manual backfill moves legacy terminal rows one at a time

An explicit preview/apply mutation SHALL move a specified terminal row from the live Backlog to the archive. It SHALL refuse non-terminal rows, name the exact row and target section in the preview, and follow the standard stale-preview and journal rules.

#### Scenario: Legacy completed row backfilled
- **WHEN** the user backfills a legacy `COMPLETED` Epic row via the explicit mutation
- **THEN** the preview shows the row move from `BACKLOG.md` to `BACKLOG-ARCHIVE.md` and apply performs exactly that edit

#### Scenario: Non-terminal row refused
- **WHEN** backfill is requested for a row with status `OPEN`
- **THEN** the mutation refuses and reports that only terminal rows can be archived

### Requirement: Legacy terminal rows backfill in one batch mutation

A batch backfill mutation SHALL move every terminal row in the live Backlog to `BACKLOG-ARCHIVE.md` as one preview/apply transaction: the preview lists every row move and both file edits, the apply token binds the whole set, and rollback restores both files together. Non-terminal rows SHALL remain untouched. When the live Backlog contains no terminal rows, the batch SHALL report that without producing a mutation.

#### Scenario: One apply clears all legacy terminal rows
- **WHEN** the live Backlog holds two terminal Epic rows and one terminal Bug row and the batch is applied
- **THEN** all three rows move in one transaction and the live file keeps only non-terminal rows

#### Scenario: Nothing to archive is a report, not a mutation
- **WHEN** the live Backlog contains no terminal rows
- **THEN** the batch reports zero candidates and writes nothing

#### Scenario: Stale batch preview rejected
- **WHEN** either `BACKLOG.md` or `BACKLOG-ARCHIVE.md` changes between batch preview and apply
- **THEN** apply fails without writing

### Requirement: Staleness is reported mechanically from Git row history

A read-only helper SHALL report live non-terminal rows whose last change in the Git history of `BACKLOG.md` is older than an explicit per-call threshold, keyed by the exact row identity so one identifier never matches another's history. Rows without Git history SHALL be listed separately as unknown instead of being judged stale or fresh. The report SHALL change nothing: it names candidates with the observed last-change date and age, and closing any row remains an explicit approved transition requested by the user.

#### Scenario: Old row reported with its evidence
- **WHEN** a live row was last changed in Git 120 days ago and the threshold is 90 days
- **THEN** the report lists that row with its last-change date and age, and the row itself is unchanged

#### Scenario: Uncommitted row stays unknown
- **WHEN** a live row has no Git history
- **THEN** the report lists it under unknown rather than counting it as stale or fresh

### Requirement: Stale-row surfacing is suggestion-only

Backlog review workflows MAY report live `OPEN` or `PAUSED` rows that look stale as candidates for cancellation, with the observed inactivity. Such reporting SHALL NOT change any row, status, or priority; closing a row remains an explicit approved transition initiated by the user.

#### Scenario: Stale candidate reported without side effects
- **WHEN** a review workflow lists stale candidates
- **THEN** the reported rows keep their current status and position until the user explicitly approves a transition

#### Scenario: Reprioritization order untouched
- **WHEN** stale candidates are reported during reprioritization
- **THEN** live Backlog ordering and priorities change only through the user's explicit approved edits
