## Why

Review of the current Forge bundle and its last two commits found seven reproducible defects or workflow contradictions: upgrades from 4.12.0 are blocked, scoped commits can include unrelated staged work and reject legitimate deletions, bootstrap bypasses the planning interview, acceptance mistakes template text for rejection, removed rules escape conformance, and staged rendering reads old rule contracts. Fix these before consumers adopt the new processes.

## What Changes

- Ship a consistent 4.13.0 bundle with migration coverage using the actual shipped target version.
- Refuse scoped commits with unrelated staged changes before touching the index; accept tracked deletions while rejecting missing unknown paths.
- Route bootstrap preparation through the same interview and confirmation sequence as normal Epic preparation.
- Recognize actual rejection results rather than placeholder text during acceptance.
- Detect stale router rules after the last declaration is removed, including removal of the declaration file.
- Validate project rules with the rendering bundle's contracts and fingerprint that input.
- Add behavioral regression tests and focused workflow consistency checks.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `framework-migration`: coherent release metadata and staged-bundle rule validation.
- `lifecycle-scripting`: pre-staged isolation and tracked deletion handling for scoped commits.
- `epic-planning-interview`: identical interview ordering at bootstrap entry points.
- `process-fix-followup`: placeholders never constitute rejection evidence.
- `rule-drift-detection`: declaration removal still detects stale router instructions.

## Impact

Framework Python helpers, release manifest/project template/migration notes, bootstrap planning instructions, helper usage documentation, and tests. No new dependencies, model calls, consumer-history backfill, or changes to approval authority. Main specs remain unchanged until an explicit sync/archive workflow.
