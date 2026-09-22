# Framework Migration Specification

## Purpose

Deterministic, prompt-free upgrade of a consumer repository from an active `.ai/` framework bundle to a staged `.ai-next/` bundle through one local command, with complete preview, explicit decisions, provenance-proven deletions, and transactional rollback.

## Requirements

### Requirement: Migration preview is read-only and complete

The migration command SHALL compute its entire result as a pure function of the repository state before any write. Preview SHALL report old and new framework versions, every framework-owned file replacement, obsolete-path deletions, preserved unknown files, rendered root routers and adapter outputs, the updated project configuration, offline integration classification, blocking and advisory findings, and a fingerprint of protected project paths — bound to a single preview token that changes when any input changes.

#### Scenario: Preview does not touch the working tree
- **WHEN** the user runs the migration preview against a staged bundle
- **THEN** no file in the repository is created, modified, or deleted
- **AND** the output ends with a preview token and the protected-path fingerprint.

#### Scenario: Stale preview is rejected
- **WHEN** any previewed input changes between preview and apply
- **THEN** apply fails before the first write and names the staleness.

### Requirement: Layout and version gates block unsafe migration

The command SHALL require an active `.ai/` bundle and a staged `.ai-next/` bundle that resolve to distinct paths, a structurally valid staged manifest, and that every staged file lies under a framework-owned path declared by that manifest. The staged framework version SHALL strictly exceed the active one; equal versions are a no-op finding and older staged versions are rejected as downgrades.

#### Scenario: Staged bundle older than active
- **WHEN** `.ai-next/` declares a framework version lower than the active `.ai/`
- **THEN** the command refuses with a downgrade finding and performs no writes.

#### Scenario: Extra content inside the staged bundle
- **WHEN** `.ai-next/` contains a file outside the staged manifest's framework-owned paths
- **THEN** the command reports the unexpected staged file and refuses to proceed.

### Requirement: Router migration uses the overlay without model judgment

The command SHALL render the new root `AGENTS.md` from the staged template plus the project's `.ai/custom/router-shared.md` preserved byte-for-byte, and `CLAUDE.md` as the exact `@AGENTS.md` import. When no shared overlay exists, migration SHALL block with a named `router_extraction_required` finding and accept a prepared overlay only through an explicit input path. Legacy platform-specific router overlays SHALL block until reconciled separately. The rendered router SHALL satisfy the router line budget before apply.

#### Scenario: Existing overlay carries forward
- **WHEN** the project already has `.ai/custom/router-shared.md`
- **THEN** the new `AGENTS.md` is the staged template rendered with that exact overlay and the preview shows the full router diff.

#### Scenario: Legacy project without an overlay
- **WHEN** the active project has project-specific router content but no shared overlay
- **THEN** preview blocks with `router_extraction_required`
- **AND** the migration completes only after a prepared overlay is supplied through the explicit input, whose content the preview shows in full.

### Requirement: Configuration changes are explicit and never inferred

The migration SHALL update the framework version field in project configuration deterministically as part of the approved change set. Any configuration key the version range declares as requiring a decision SHALL block apply until supplied through an explicit key-value override, and the preview SHALL show each blocked key with its recorded suggestion. Previously approved values, including the role execution mode and platform model mappings, SHALL be preserved unless explicitly overridden; the command SHALL NOT invent, default, or silently replace them.

#### Scenario: Missing role execution mode blocks apply
- **WHEN** the active configuration lacks a value the staged version range declares as decision-required
- **THEN** preview reports the key with its suggestion and apply refuses until an explicit override is supplied
- **AND** the applied configuration records exactly the supplied value.

#### Scenario: Approved mode survives the upgrade
- **WHEN** the project has an approved role execution mode and no override is passed
- **THEN** the migrated configuration keeps that mode byte-identically.

### Requirement: Obsolete deletion is provenance-proven

Deletion of a file under a framework-owned path of the active bundle SHALL happen only when the prior lock recorded that path's content hash and the file still matches it while being absent from the staged bundle. Any file inside framework-owned paths whose provenance cannot be proven — including the first migration without recorded bundle state — SHALL be preserved untouched and reported as an advisory finding. Runtime artifacts such as `__pycache__` SHALL be ignored rather than reported.

#### Scenario: Recorded obsolete file removed
- **WHEN** the prior lock records a framework-owned file that the staged bundle no longer ships and the on-disk bytes still match the record
- **THEN** apply removes the file and the journal can restore it.

#### Scenario: Unknown file preserved
- **WHEN** a file exists under a framework-owned path without a matching lock record
- **THEN** the migration preserves it byte-for-byte and reports it as preserved advisory content.

### Requirement: Project-owned and canonical state remain untouched

All project-owned and canonical paths — project configuration beyond the declared migration keys, custom overlays, local artifacts, integrations, investigations, intents, mutation history, canonical documents, decisions, execution state, code, tests, and unrelated configuration — SHALL pass through the migration byte-for-byte, verified by re-hashing after apply. Integration definitions SHALL be classified offline against the staged contracts and malformed, future-version, custom, or offline entries SHALL block only their consumers, never the framework transaction. Framework migration and integration-schema migration SHALL remain separate approvals.

#### Scenario: Protected path tampering fails apply
- **WHEN** a protected project path changes between preview and the post-apply verification
- **THEN** the migration reports the violation and rolls every framework change back to the pre-migration state.

#### Scenario: Older integration does not block the framework
- **WHEN** `.ai/integrations/` contains an older-migratable definition
- **THEN** the framework migration completes with the file preserved byte-for-byte and the compatibility finding offered as a separate later transaction.

### Requirement: Apply is atomic, validated, and recoverable

Apply SHALL execute as one logical operation under a claimed transaction guard: back up every affected file, recheck the preview token after backups, write the complete change set, run framework validation against the result, re-hash protected paths, and write or update the lock only after every check passes. The lock SHALL gain a bundle-state record of framework-owned file hashes while preserving unknown fields from the prior lock. On success the staging directory SHALL be removed; on any failure the command SHALL restore the pre-migration bundle, routers, adapters, configuration, and lock, and keep the staged bundle in place. An interrupted transaction SHALL remain recoverable through an explicit recovery operation that refuses to overwrite subsequent user edits. A dirty Git tree SHALL be reported as a warning before apply, with the recoverable baseline remaining the user's responsibility.

#### Scenario: Validation failure rolls back
- **WHEN** the candidate result fails validation after the writes began
- **THEN** the repository is restored to its pre-migration state and the failed stage is reported
- **AND** `.ai-next/` remains for a corrected retry.

#### Scenario: Success cleans staging
- **WHEN** apply completes with validation and re-hash passing
- **THEN** the lock contains the new bundle state and the staging directory is removed.

### Requirement: Version-specific migration semantics are computed from a contract

The staged bundle SHALL carry a structured migration contract declaring, per framework version, decision-required configuration keys with suggestions, breaking changes, and optional post-migration backfill commands. The command SHALL apply only the entries within the actual old-to-new version range and SHALL compute the corresponding findings mechanically, including checking live Backlog rows for terminal statuses with the available archive command. Human-readable migration notes SHALL remain documentation; the command SHALL NOT depend on them.

#### Scenario: Range filters contract entries
- **WHEN** the contract declares entries for versions below the active one
- **THEN** those entries produce no findings and no required decisions.

#### Scenario: Legacy terminal rows reported with remedy
- **WHEN** the live Backlog contains terminal rows and the crossed version range introduced automatic archiving
- **THEN** the preview reports the rows as an advisory finding together with the exact available backfill command.

### Requirement: The migration entry point is agent-first and needs no long prompt

A consumer SHALL be able to request the migration from either an agent session opened in the local Forge clone with a named consumer path, or an agent session opened in the consumer with a named Forge clone (or an explicitly approved remote release), without manually staging `.ai-next/`, copying a preview token, composing flags, or reading command JSON. Staging remains a documented copy or sparse-clone operation without network access inside the Python tools. The bundled migration skill SHALL act as a thin wrapper that stages the bundle, invokes the command, explains findings, collects the explicit decisions, retains the preview token as agent working data, applies the approved preview, and reports the result — performing judgment work only for legacy router extraction, configuration choices, and collision decisions. Projects without Python SHALL retain the documented manual agent-driven migration path.

#### Scenario: Local clone request drives the whole workflow
- **WHEN** the user asks an agent to update a consumer repository from a named local Forge clone
- **THEN** the agent stages that clone's release bundle, runs preview, asks only for unresolved decisions and final approval, and applies the reviewed token itself
- **AND** the user is not asked to copy a token or assemble a migration command.

#### Scenario: Skill drives the command
- **WHEN** the user invokes the bundled migration skill in a project with Python available
- **THEN** the skill stages the selected release when needed, runs the command's preview, surfaces its findings for decision, and applies with the returned token instead of performing the migration mechanics itself.

#### Scenario: No-Python fallback preserved
- **WHEN** the consumer project cannot run the Python tools
- **THEN** the manual agent-driven migration flow remains documented and available.
