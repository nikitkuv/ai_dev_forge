---
name: forge-check-framework
description: Use after bootstrap, resume, adapter synchronization, framework upgrade, or suspected lifecycle and ownership inconsistencies in an initialized Forge project.
---

# Check Framework Conformance

## Read authoritative inputs

Read the manifest, lifecycle, integration and mutation-testing contracts, project configuration, framework lock, custom overlays, optional project-owned integration definitions/state, optional project-owned mutation registry/run records, canonical documents, ADRs, execution tree, neutral agent and skill sources, generated adapters, and Git state. Never invoke a local connector or mutation backend during conformance checking.

Do not repair files during this check.

## Validate structure and ownership

- Verify required framework-owned files and project-owned state exist.
- Detect obsolete framework-owned paths, unexpected overwrites, generated adapter edits, and ownership collisions.
- Verify all enabled platform adapters were generated from the same source hashes and project configuration.
- Verify every manifest-declared agent and skill exists on Codex and Claude with matching IDs, tiers, role boundaries, and concrete model mappings; verify enabled OpenCode has every agent and discovers the same skills from `.agents/skills/`.
- Verify `role_execution.mode` remains one of the same three supported atomic values for both roles; verify both managed launchers and every route reuse the matching neutral role contract, enforce the expected orchestrator, model and permission boundary, request fresh execution, and prohibit fallback. Native mode must support Codex, Claude Code, and OpenCode with no external preflight. An OpenCode-led setup with no approved route proposes existing `native_subagents` by default but still requires approval and never rewrites an approved value.
- Verify every Forge-managed `.claude/agents/*.md` and `.opencode/agents/*.md` file is UTF-8 without BOM and starts at byte zero with the `---` YAML frontmatter delimiter.
- Verify enabled OpenCode model tiers are explicit non-empty `provider/model-id` values; only implementer permits edits, command and documentation-research permissions do not exceed neutral policy, and every OpenCode subagent denies external-directory and nested task access.
- Permit additional project-owned agents and skills; verify they and other unlisted platform files are excluded from Forge ownership and remain unchanged.
- Verify the shared router overlay renders once into `AGENTS.md` without copying legacy framework instructions.
- Verify root `AGENTS.md` is the complete router and no more than 150 lines, while root `CLAUDE.md` contains exactly `@AGENTS.md`.
- Verify the framework did not create default hooks, MCP configuration, mandatory CLI dependencies, `opencode.json`, or duplicate `.opencode/skills/` during generation. Preserve OpenCode commands, plugins, skills, provider configuration, and unlisted agents as project-owned content. External prerequisites are required only when their mode is selected; `native_subagents` remains dependency-free.
- Verify `.ai/integrations/` is optional and absent in a clean project; when present, it is project-owned, excluded from managed-output hashes, and never embedded in generated adapters.
- Verify `quality/mutation-testing/` is optional and absent in a clean project; when present, it is project-owned, excluded from managed-output hashes and adapter render inputs, and preserved by migration and synchronization.
- Verify optional `mutation_testing` configuration is absent, null, or backed by confirmed repository/build/CI evidence. A configured backend requires exact version, baseline, mutation and result-adapter commands plus explicit budgets and constraints; missing setup blocks only a requested mutation run and never bootstrap or development.
- Verify `mutation-runner` is fast, baseline-first, fingerprinted before/during/after execution, runtime-artifacts-only, network-disabled, and prohibited from installation, tracked edits, remediation, lifecycle changes and spawning. Verify `mutation-analyzer` is strong, explicitly authorized, candidate- and budget-gated, runtime-artifacts-only, network-disabled, and prohibited from remediation, lifecycle changes and spawning. Verify both roles and `forge-mutation-test` have generated parity on every enabled platform, with OpenCode using the shared skill copy.
- Classify each integration definition/state file as current-supported, older-migratable, malformed, unsupported-future, custom-profile, or ownership collision. Preserve unknown profiles. Treat only ownership collisions and repository-safety violations as global blockers; other findings block only consuming skills.
- Verify every invocation-capable integration has an explicit compatible consumer, operation intersection, scope, access policy, and active-platform binding. Do not require live availability for structural conformance.

## Validate canonical and lifecycle state

- Check required frontmatter, approved-document placeholders, global unique IDs, max-plus-one allocation, links, and ADR index parity.
- Check all enum values and transitions against `.ai/framework/contracts.yaml`.
- Check at most one nonterminal active-work Epic across `ACTIVE`, `VALIDATING`, `FUZZING`, and `AWAITING EPIC ACCEPTANCE`, and one code-writing TASK in progress.
- Check each `execution/planned/` directory maps to exactly one `PLANNED + READY` Backlog Epic with an approved plan and approved `TODO` TASK definitions.
- Allow multiple planned workspaces, verify their priority comes only from Backlog order, and reject duplicate workspaces for one Epic.
- Check non-planned Backlog Epic state matches `execution/active`, `paused`, or `completed` and no Epic exists in more than one execution directory.
- Check Task state exists only in its TASK file and Epic priority/readiness/status only in `BACKLOG.md`.
- Check plan Task order matches existing TASK files without storing Task status.
- Check SPEC and ARCHITECTURE contain target state, not execution tracking.
- Check every Review Packet classifies production and supporting paths by shipped-behavior effect, records rationale for ambiguous paths, and carries both whole-implementation and production-surface fingerprints. Require clean structured review to match the current production fingerprint and selected Task testing to match the current implementation revision and whole-implementation fingerprint. Treat legacy review without a production fingerprint as stale.
- Check every approved TASK has exactly one delivery track independent from model tier and risk level. Treat a missing legacy track as standard. For fast, require complete eligibility/disqualifier evidence and a current Fast Assurance Summary matching the whole-implementation fingerprint; forbid reviewer/tester invocation claims and direct acceptance with stale evidence. For standard, retain current Review Packet, clean review, and tester requirements. Report any standard-to-fast transition after Task Start and any unrecorded fast-to-standard escalation.
- Check Task verification does not require a full project suite or unscoped global command without an explicit early-run request.
- Check the approved Epic Verification Plan, Epic Fuzzing Plan, selected quality profiles, full-suite/project-wide Epic Validation evidence, and aggregate fingerprint are current before the fuzzing gate.
- Check every TASK records final `Fuzzing impact` and `Task fuzz smoke` evidence. A skipped fuzzer invocation is valid only for approved `not applicable` with all final impacts `none`, matching actual affected surfaces, passing alternative risk coverage, and the same aggregate fingerprint; `applicable`, `unresolved`, or contradictory evidence must show a fuzzer invocation.
- Check production-surface changes invalidate Task review and testing plus aggregate Epic Validation and fuzzing evidence. Check supporting-only changes preserve a matching clean production review, invalidate affected Task testing plus aggregate Epic Validation and fuzzing evidence, and never cause another strong-review invocation by themselves.
- Check no Task commit predates explicit Task Acceptance and transition to `DONE`.
- Check the current gate can be reconstructed without session history.
- Check Epic Start always consumes one approved planned workspace through an atomic planned-to-active move plus Backlog transition.
- For configured `work_source` integrations, check Backlog `Sources`, TASK `external_sources`, Epic source coverage, and `.ai/integrations/work-items.yaml` in both directions. Canonical lifecycle state remains authoritative; non-work profiles require no work-item mapping.

## Validate independent mutation history

- When mutation history is absent, require no directory, registry, backend, preflight, agent invocation or blocker.
- When present, require `quality/mutation-testing/registry.yaml`, a supported `schema_version`, unique monotonically allocated `MUT-NNNN` identities, `next_id` greater than every retained identity, and one matching `runs/MUT-NNNN.yaml` path for every registry entry. Reject reused, duplicate, path-mismatched, or dangling identities.
- For every run attempt, require timestamps, run outcome/reason, exact production/test scope and exclusions, base revision plus scoped diff/tree fingerprint and dependency inputs, backend/version/commands/constraints, finite budgets, baseline outcome, normalized result counts, artifact retention with paths/checksums when retained, analysis authorization/status/budget/counts/findings, and disposition. Counts must be non-negative and candidate/analysis totals internally consistent.
- Permit unsuccessful, partial, cancelled, metrics-only and setup-required records. Require metrics-only records to use `analysis.authorized: false` and `analysis.status: not_requested`. Require `skipped_no_candidates` only when authorization exists and no configured candidate exists. Require completed or partial analysis to have explicit authorization, a current matching source fingerprint, a current normalized artifact checksum, positive budget, and candidate evidence; partial analysis must record a positive remaining count.
- Reject analysis after baseline failure, setup-required, cancellation, unusable/stale artifacts, zero budget, or no candidates. Deferred analysis must update the same run identity and must not claim a repeated campaign unless the user requested a new run.
- Verify mutation outcomes and dispositions do not appear as Epic, TASK, Bug or ADR transitions; do not satisfy quality gates; do not invalidate review/testing/validation/fuzzing evidence; and do not create or schedule development work without a separately recorded user decision through an existing workflow.

## Report

Return a concise pass/fail summary and actionable findings with severity, exact paths, violated invariant, and safe next gate. Distinguish blockers from warnings.

Create no conformance or validation report file, change no status, regenerate no adapter, and delete nothing. Route repairs through the relevant skill and explicit user approval.
