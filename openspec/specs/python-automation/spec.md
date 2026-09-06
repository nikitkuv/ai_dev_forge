# Python automation and bounded context

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

### Requirement: Measurement distinguishes observations from estimates

Local metrics SHALL preserve unknown usage as unknown. Context budgets SHALL label characters-based token estimates as heuristics. Synthetic context-size benchmarks SHALL NOT claim measured end-to-end model savings or equivalent quality. Raw logs/cache/metrics are project-owned, disposable and excluded from generated adapter inputs; canonical evidence remains in TASK/plan.
