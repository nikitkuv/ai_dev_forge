## MODIFIED Requirements

### Requirement: Identifier allocation is mechanical and monotonic

The helper SHALL compute the next identifier for each kind — project-global `TASK`, `BUG`, `INV`, `INT`, `EPIC`, `ADR`, and `MUT` — as max-plus-one over the canonical locations that declare that kind, without filling gaps and without reusing retired identifiers. For kinds declared by Backlog rows, the scanned locations SHALL include both the live `BACKLOG.md` and `BACKLOG-ARCHIVE.md`, so an archived maximum still bounds allocation. The result SHALL list the scanned sources and the current maximum so the allocation is auditable.

#### Scenario: Allocate the next investigation
- **WHEN** `investigations/` contains `INV-0001` and `INV-0003`
- **THEN** the helper returns `INV-0004` and reports the scanned locations and maximum

#### Scenario: Archived maximum bounds Bug allocation
- **WHEN** `BACKLOG-ARCHIVE.md` contains `BUG-0010`, the live Defect Queue's maximum is `BUG-0003`, and the next Bug identifier is requested
- **THEN** the helper returns `BUG-0011` and reports both scanned Backlog locations with the archive maximum

#### Scenario: No existing identifiers
- **WHEN** the canonical location for a kind is empty or absent
- **THEN** the helper returns the first identifier of that kind and reports that no prior records were found

### Requirement: Structural conformance coverage includes framework shape checks

`validate --project --adapters` SHALL additionally verify, without a model: the root `AGENTS.md` router line budget and the exact `CLAUDE.md` import line; generated agent files are UTF-8 without BOM and begin the YAML frontmatter delimiter at byte zero; `DECISIONS.md` index parity with `decisions/ADR-*.md` files; plan Task order consistency with existing TASK files; required frontmatter and outcome enums of investigation records; and mutation-registry/run structural rules. It SHALL also verify the Backlog archive invariant: the live `BACKLOG.md` contains no terminal rows (Epic `COMPLETED`/`CANCELLED`; Bug `RESOLVED`/`REJECTED`/`DUPLICATE`/`WONT_FIX`), and `BACKLOG-ARCHIVE.md` — when present — contains only terminal rows under well-formed year sections. The output SHALL keep separating mechanical coverage from the fields that require judgment.

#### Scenario: Unindexed ADR detected
- **WHEN** `decisions/` contains an ADR file absent from the `DECISIONS.md` index
- **THEN** validation reports the unindexed ADR path

#### Scenario: Terminal row left in the live Backlog
- **WHEN** the live `BACKLOG.md` contains a `COMPLETED` Epic row
- **THEN** validation reports the row, the violated invariant, and the backfill mutation as remediation

#### Scenario: Malformed generated agent file detected
- **WHEN** a generated `.claude/agents/*.md` file starts with a UTF-8 BOM
- **THEN** validation reports the file and the violated rule
