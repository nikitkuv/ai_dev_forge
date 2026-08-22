## 1. Generic integration schema and ownership

- [x] 1.1 Increment the framework version and extend the manifest/conventions with optional project-owned `.ai/integrations/`, generic capability profiles/consumers, and the external-intake skill ID; verify existing hooks/MCP/CLI remain non-generated, both platform inventories match, and a clean project gains no integration files.
- [x] 1.2 Define and document the versioned generic integration schema, including stable ID, profile/version, resource scope, semantic operation allowlist, access/data policy, allowed consumers, and per-platform bindings; verify fixtures cover knowledge/data/analysis/custom profiles and reject ambiguous IDs, missing scope, unauthorized consumers, and secret-bearing fields.
- [x] 1.3 Define the versioned `work_source` profile with read-only listing/detail operations, field mapping, candidate filters, and label hints; verify Kaiten-like and non-Kaiten fixtures bind through the profile while provider names remain absent from the framework core.
- [x] 1.4 Define the versioned `.ai/integrations/work-items.yaml` provenance schema only for `work_source` integrations and the provider-neutral source-key format for many-to-many `external item <-> EPIC/BUG/TASK` mappings; verify non-work profiles need no ledger and work-source fixtures cover split/combine, dispositions, duplicates, and invalid references.
- [x] 1.5 Define explicit framework/project-owned consumer contracts and unknown-profile preservation; verify a registered integration cannot be invoked without a selected compatible consumer and a project-owned custom profile/skill survives generation unchanged.
- [x] 1.6 Update project/template guidance so the registry is opt-in and absent by default; verify bootstrap, validation, adapter sync, migration, and lifecycle outputs for a zero-integration fixture match the clean Forge baseline.

## 2. External work intake workflow

- [x] 2.1 Add the neutral `forge-intake-external-work` consumer for the `work_source` profile with explicit-record and configured-queue retrieval, active-platform preflight, bounded pagination, partial-result reporting, and source-neutral normalization; verify scripted scenarios cover absent integrations, wrong profile, unavailable binding/connector, one ticket, a filtered queue, and incomplete retrieval.
- [x] 2.2 Implement the skill's trust boundary and least-privilege rules so only declared read operations and mapped fields are used and external instructions remain data; verify adversarial fixtures cannot trigger commands, lifecycle approvals, secret persistence, or connector mutation.
- [x] 2.3 Add repository/canonical investigation and intent/granularity classification that distinguishes defects, investigations, product changes, duplicates, and unresolved candidates; verify the small area-cutoff example can route to bug/existing-Epic/new-Epic decisions without directly creating a TASK.
- [x] 2.4 Add reviewable split/combine proposals that map every selected source record to disposition, requirements, areas, assumptions, dependencies, and resulting Epic candidates; verify the drilling-recommendations example supports multiple Epics and related-card fixtures support one combined Epic without losing source coverage.
- [x] 2.5 Compose approved classifications with `forge-intake-feature`, `forge-intake-bug`, and Replan/Plan Approval rules instead of duplicating their mutations; verify retrieval or a board status never bypasses canonical approval, Epic Start, or Task Start.
- [x] 2.6 Add current-snapshot revalidation and atomic intake/provenance update rules; verify changed, unavailable, or partially persisted source records invalidate the proposal and leave no partial Forge IDs or misleading retained mappings.

## 3. Canonical ticket relationships

- [x] 3.1 Extend the Backlog template and contract with compact `Sources` references for Epics and Bugs, including migration-compatible handling of existing tables; verify external references do not replace requirement, priority, readiness, dependency, or lifecycle ownership.
- [x] 3.2 Extend TASK frontmatter and Epic plan templates with `external_sources` and a source-to-TASK coverage matrix; verify approved planning can map one ticket to several Tasks and one Task to several tickets while preserving unique Forge IDs.
- [x] 3.3 Update Epic preparation and Replan guidance to create or revise canonical source references and reverse-ledger mappings in one logical transition; verify split, combine, add, and remove coverage cases preserve historical source identity and reject stale source evidence.
- [x] 3.4 Update resume, Task execution/completion, Epic validation/completion, and framework-check guidance to load and reconcile ticket relationships; verify status reports include linked tickets, per-TASK coverage, uncovered sources, and broken or contradictory mappings before relationship-dependent gates proceed.
- [x] 3.5 Add deterministic reconciliation rules that keep canonical Forge lifecycle state authoritative while repairing only explicitly approved provenance/reference drift; verify no reconciliation infers external acceptance, priority, readiness, or completion.

## 4. Adapters and clean-project behavior

- [x] 4.1 Add external-work-intake routing to the byte-identical Codex and Claude root-router templates and generate the portable skill for both platforms; verify adapter membership/parity tests pass and local connector names or credentials never enter generated routers.
- [x] 4.2 Update bootstrap and final validation to recognize optional generic definitions and profile-specific state without invoking live connectors; verify a clean project succeeds unchanged and invalid integrations block only their consumers.
- [x] 4.3 Update adapter sync so managed outputs contain generic profile/consumer routing but never local integration content; verify arbitrary project integration edits do not require regeneration and unrelated platform MCP/settings files remain preserved.
- [x] 4.4 Scope framework-lock hashes to actual managed-output inputs and validate integrations separately as project state; verify changing a board, knowledge-source, or analysis-service scope is not reported as framework drift.

## 5. Upgrade and integration-schema migration

- [x] 5.1 Add an offline compatibility scan that classifies each integration/state file as absent, current-supported, older-migratable, malformed, unsupported-future, custom-profile, or colliding; verify it performs no connector/MCP/API/CLI invocation.
- [x] 5.2 Update framework migration to stage managed release files separately and preserve `.ai/integrations/`, custom consumers, MCP files, canonical documents, and execution state byte-for-byte; verify upgrades succeed for no-integration, supported, malformed, future-schema, and unknown-profile fixtures unless a true ownership collision exists.
- [x] 5.3 Implement the separately approved integration-schema migration contract with exact diff, recoverable backup, staged structural/referential validation, and atomic apply; verify old supported schemas migrate without changing credentials or lifecycle state.
- [x] 5.4 Add failure isolation and rollback rules so a failed integration migration restores project-owned state without corrupting the installed framework, and framework rollback retains or restores a mutually compatible integration representation; verify active ticket-to-work relationships survive both paths.
- [x] 5.5 Add compatibility tests across consecutive supported schema/framework versions, including partial platform bindings and multiple integrations where only one is invalid; verify unrelated Forge lifecycle and valid consumers remain operational.

## 6. Documentation and examples

- [x] 6.1 Update `README.md`, `FRAMEWORK.md`, and `RUNBOOK.md` with the generic local-integration model, explicit consumers, zero-integration default, upgrade compatibility, external-board intake, relationship model, offline behavior, and read-only work-source limitation; verify docs never imply every integration is a board.
- [x] 6.2 Add sanitized examples for a knowledge source and a project-defined analysis capability, plus a Kaiten/MCP `work_source` example for `oilgas_reserves_calculation` with the requested label mappings; verify examples contain no credentials, user-specific path dependency, or provider logic in framework-owned contracts.
- [x] 6.3 Extend scenarios with a clean project, custom non-board integration, framework upgrade compatibility matrix, integration rollback, explicit-ticket, next-candidate, split/combine, duplicate, source-update, Replan, and resume flows; verify every flow preserves ownership and lifecycle gates.

## 7. End-to-end verification

- [x] 7.1 Add contract tests for generic schemas, consumer authorization, unknown-profile preservation, work-source normalization, read-only allowlists, prompt-injection handling, provenance, bidirectional references, upgrade isolation, and platform parity; run `node --test tests/*.test.mjs` and verify all tests pass.
- [x] 7.2 Exercise a zero-integration fixture through bootstrap, adapter sync, development resume, framework upgrade, validation, and rollback; verify its behavior and generated output remain the clean Forge baseline with no connector preflight.
- [x] 7.3 Exercise a mixed fixture with a custom non-board integration and Kaiten-like work source through upgrade, approved Backlog links, Epic planning, TASK coverage, resume, duplicate fetch, source update, and rollback; verify both generic capability use and `ticket <-> EPIC/BUG/TASK` traversal survive without external mutation.
- [x] 7.4 Run repository documentation/framework validation and `openspec validate add-project-local-work-integrations --strict`; verify all checks pass and record live connector availability as an environment-specific manual check rather than fabricated evidence.
