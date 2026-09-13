## ADDED Requirements

### Requirement: Identifier allocation is mechanical and monotonic

The helper SHALL compute the next identifier for each kind — project-global `TASK`, `BUG`, `INV`, `EPIC`, `ADR`, and `MUT` — as max-plus-one over the canonical locations that declare that kind, without filling gaps and without reusing retired identifiers. The result SHALL list the scanned sources and the current maximum so the allocation is auditable.

#### Scenario: Allocate the next investigation
- **WHEN** `investigations/` contains `INV-0001` and `INV-0003`
- **THEN** the helper returns `INV-0004` and reports the scanned locations and maximum

#### Scenario: No existing identifiers
- **WHEN** the canonical location for a kind is empty or absent
- **THEN** the helper returns the first identifier of that kind and reports that no prior records were found

### Requirement: Evidence freshness verdicts are computed, not judged

The evidence helper SHALL read the fingerprints and path sets recorded in a TASK's evidence sections, recompute current fingerprints for those exact paths, and report per-check comparisons: Task acceptance eligibility (recorded assurance or testing fingerprint against the current whole-implementation set), review freshness (recorded clean-review production fingerprint against the current production set), and Epic gate readiness (all planned TASKs `DONE`, final fuzzing evidence present, aggregate fingerprint match). Missing or malformed recorded evidence SHALL be reported explicitly. The output SHALL mark review-protocol completeness, test integrity, and coverage quality as requiring judgment and SHALL NOT decide them.

#### Scenario: Supporting-only change keeps review fresh
- **WHEN** a test file in the supporting set changed but no recorded production path changed
- **THEN** review freshness reports the production fingerprint as matching and the whole-implementation fingerprint as changed

#### Scenario: Production change makes review stale
- **WHEN** a file in the recorded production review set changed
- **THEN** review freshness reports a fingerprint mismatch and names the changed paths

#### Scenario: Legacy evidence without fingerprints
- **WHEN** a TASK's recorded review evidence lacks a production fingerprint
- **THEN** the helper reports the evidence as insufficient for a freshness verdict instead of guessing

### Requirement: Structural conformance coverage includes framework shape checks

`validate --project --adapters` SHALL additionally verify, without a model: the root `AGENTS.md` router line budget and the exact `CLAUDE.md` import line; generated agent files are UTF-8 without BOM and begin the YAML frontmatter delimiter at byte zero; `DECISIONS.md` index parity with `decisions/ADR-*.md` files; plan Task order consistency with existing TASK files; required frontmatter and outcome enums of investigation records; and mutation-registry/run structural rules. The output SHALL keep separating mechanical coverage from the fields that require judgment.

#### Scenario: Unindexed ADR detected
- **WHEN** `decisions/` contains an ADR file absent from the `DECISIONS.md` index
- **THEN** validation reports the unindexed ADR path

#### Scenario: Malformed generated agent file detected
- **WHEN** a generated `.claude/agents/*.md` file starts with a UTF-8 BOM
- **THEN** validation reports the file and the violated rule

### Requirement: Review packets are assembled mechanically

The packet helper SHALL build a compact Review Packet for a TASK from its recorded data: the classified production and supporting path lists with their ambiguous-path rationales, recomputed whole-implementation and production-surface fingerprints, reproducible scoped Git diffs for both surfaces against the recorded base revision, referenced TASK/plan sections, and recorded evidence references. It SHALL use the path classification as recorded input and SHALL NOT classify paths, judge review focus, or validate review protocol — those remain orchestrator work. Missing recorded inputs SHALL fail with the exact missing field.

#### Scenario: Packet built from recorded classification
- **WHEN** a TASK records classified paths, base revision, and evidence references
- **THEN** the helper emits the packet with recomputed fingerprints and scoped diffs without re-reading the full TASK body into orchestrator context

#### Scenario: Recorded path missing on disk
- **WHEN** a recorded fingerprint input path no longer exists
- **THEN** the helper reports the missing path explicitly as a deletion or inconsistency instead of silently omitting it

### Requirement: Check packets are written from explicit inputs

The packet-writing helper SHALL create an approved-checks packet file from explicit argument arrays, an explicit input file set, stage, and cacheability flags, without shell interpolation of commands. The written packet SHALL satisfy the same schema the check executor consumes.

#### Scenario: Packet written for a focused test
- **WHEN** the orchestrator supplies argv, inputs, and stage `task`
- **THEN** the helper writes a valid packet file the existing check executor accepts unchanged

### Requirement: External role prompts embed the neutral contract without orchestrator echo

When invoked with an assignment file instead of a full prompt, the role helper SHALL read the complete neutral role contract from the framework source itself, concatenate it with the assignment exactly once, and pass it through a transient prompt file that is removed after use. The orchestrator SHALL NOT be required to read or reproduce the contract text. A missing, malformed, or ID-mismatched contract SHALL fail the call before any model invocation.

#### Scenario: External review without contract in context
- **WHEN** the orchestrator calls the role helper with only an assignment file
- **THEN** the external model receives the full neutral contract plus assignment, and the orchestrator context never contains the contract text

#### Scenario: Contract mismatch fails fast
- **WHEN** the framework contract file for the role is missing or malformed
- **THEN** the helper fails with the exact path and performs no model invocation

### Requirement: Record scaffolding instantiates templates deterministically

The scaffolding helpers SHALL create new records without model calls: the investigation helper allocates the next `INV` identifier, instantiates the investigation template, and records the baseline revision and working-tree disposition; the Backlog row helpers insert a Defect Queue row as `OPEN` with user-approved fields and update only explicitly named fields of an existing row, preserving unrelated rows and user-owned order. Every scaffolding write SHALL report the exact file diff it produced.

#### Scenario: Investigation record created
- **WHEN** the orchestrator scaffolds an investigation with subject and area
- **THEN** the helper creates `investigations/INV-NNNN-<short-name>.md` from the template with the current baseline recorded and reports the new path and identifier

#### Scenario: Backlog row updated only in named fields
- **WHEN** a row update names only `Priority` and `Blocked by`
- **THEN** the Backlog row changes only those cells and all other rows and columns remain byte-identical
