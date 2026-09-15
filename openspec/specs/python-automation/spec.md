# Python automation and bounded context

## Purpose

Optional deterministic local tooling that performs mechanical repository operations for Forge projects without model calls, keeping judgment with the orchestrator and approval with the user.

## Requirements

### Requirement: Deterministic operations do not require model inference

Forge SHALL ship optional project-local Python 3.11+ helpers inside the framework-owned `.ai/tools/` bundle. Helpers SHALL perform metadata inventory, Markdown section extraction, explicit file fingerprints, structural validation, deterministic adapter rendering, approved command execution and usage aggregation without model calls. Only an explicit external `role` command may call a model runtime. Absent Python SHALL preserve the manual workflows without implicit installation.

#### Scenario: Ordinary recovery
- **WHEN** the orchestrator resumes a consumer project
- **THEN** it inventories all planned/active/paused metadata, reads Backlog and selected current evidence, and loads other bodies only for relevant questions
- **AND** it invokes context-collector only for unresolved interpretation
- **AND** pagination, unreadable files and missing Git evidence remain visible.

### Requirement: Helpers preserve semantic authority

Python output SHALL declare its mechanical coverage and limitations. It SHALL NOT establish user approval, choose affected scope, prove test integrity, invent lifecycle transitions or replace independent review. Fast/standard delivery tracks and Epic Validation/fuzzing retain their assurance requirements.

#### Scenario: Verdicts keep judgment fields separate
- **WHEN** the evidence helper reports a fresh fingerprint match
- **THEN** the output still names review protocol, test integrity, and coverage quality as requiring judgment
- **AND** no mechanical result is presented as approval or acceptance.

### Requirement: Adapter changes are previewed and recoverable

The renderer SHALL validate enabled model mappings and rendered YAML/TOML, preserve neutral instructions, copy skill resources, preserve unlisted files and bind the preview token to inputs, existing outputs, candidate outputs and lock. Same-ID collisions require explicit authorization. Apply SHALL reject stale previews, keep backup journals, update the lock last and roll back caught failures. Crash recovery SHALL refuse subsequent user edits. Retired outputs SHALL be preserved for reviewed migration.

#### Scenario: Concurrent edit
- **WHEN** a managed file changes after preview
- **THEN** apply fails before replacing it and the user edit is preserved.

### Requirement: Command reuse is opt-in evidence reuse

Checks SHALL use explicit argv arrays, cwd, finite timeout and an explicit file input set. Reuse requires approved complete deterministic inputs, unchanged fingerprints/commands/runtime/environment and intact passing logs. Failures SHALL NOT be cached; commands SHALL NOT be retried until green. Modified inputs during execution invalidate the result. External mutable state and incomplete closure disallow reuse. Epic checks SHALL always execute regardless of reuse flags.

#### Scenario: Supporting test change
- **WHEN** an input test file changes
- **THEN** its command cache entry is inapplicable even if production code is unchanged
- **AND** the existing production-only review reuse contract remains independent.

### Requirement: Bounded Task Start grants do not imply acceptance

Strict authorization SHALL remain the default. A user may explicitly record a bounded Task Start grant containing a decision reference, approver, future expiry, exact Task paths and definition fingerprints. The helper SHALL reject changed/expired/non-approved definitions. Ordinary start preconditions still apply. Such a grant SHALL NOT grant acceptance, commit, Replan, Epic Start or scope expansion.

#### Scenario: Expired grant rejected
- **WHEN** a Task Start references a bounded grant whose expiry date has passed
- **THEN** the helper refuses the grant and requires a fresh explicit decision
- **AND** acceptance and commit authorization remain separate regardless of the grant.

### Requirement: Measurement distinguishes observations from estimates

Local metrics SHALL preserve unknown usage as unknown. Context budgets SHALL label characters-based token estimates as heuristics. Synthetic context-size benchmarks SHALL NOT claim measured end-to-end model savings or equivalent quality. Raw logs/cache/metrics are project-owned, disposable and excluded from generated adapter inputs; canonical evidence remains in TASK/plan.

#### Scenario: Unknown usage is not zero-filled
- **WHEN** a metrics report covers a period with no recorded usage
- **THEN** the report shows those values as unknown instead of substituting zeros
- **AND** token estimates remain labeled as heuristic estimates.


### Requirement: Identifier allocation is mechanical and monotonic

The helper SHALL compute the next identifier for each kind — project-global `TASK`, `BUG`, `INV`, `INT`, `EPIC`, `ADR`, and `MUT` — as max-plus-one over the canonical locations that declare that kind, without filling gaps and without reusing retired identifiers. The result SHALL list the scanned sources and the current maximum so the allocation is auditable.

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
