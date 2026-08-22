# Bootstrap Step 06 — Final Validation

## Purpose

Perform a read-only final conformance check and prove that a new orchestrator can recover the project state without session history.

Do not redesign, implement, silently repair canonical state, or create a validation report file.

## Required Inputs

Read the framework manifest and lifecycle/integration contracts, project configuration and lock, canonical documents, ADRs, execution tree, neutral sources, both generated adapter sets, custom overlays, optional project-owned integration definitions/state, and Git state. Do not invoke local connectors.

If an earlier step is incomplete, return to that step and its approval gate.

## Validate Canonical Documents

- Required root files exist for the completed bootstrap stage.
- Root `README.md` contains confirmed setup/run/test orientation and links to canonical documents plus both platform routers, without becoming a source of product, architecture, or execution truth.
- SPEC, ARCHITECTURE, BACKLOG, and plan frontmatter has valid `document_status`, language, dates, and approval metadata.
- TASK frontmatter separates `definition_status` from lifecycle `status`.
- ADR status uses the decision lifecycle and `DECISIONS.md` exactly reflects ADR frontmatter.
- Approved documents contain no unresolved template placeholders.
- Canonical documents use the project documentation language; technical IDs, statuses, paths, commands, and model IDs remain English.
- SPEC owns target product behavior and contains no architecture, Tasks, or implementation status.
- ARCHITECTURE owns target architecture and contains no task-level execution steps.
- BACKLOG owns Epic priority/readiness/status and defect state, with no Task list or execution summaries.
- Each plan owns Epic strategy, Task order, requirement coverage, selected quality profiles, Epic Verification Plan, Epic Validation evidence, fuzzing and user validation, but no Task lifecycle state.
- Each TASK owns its lifecycle, affected surface, risk flags, review focus, selected Verification Plan, and compact implementation, structured-review, testing, and user-validation evidence.
- No separate framework-generated progress, checkpoint, review, testing, fuzzing, security, recovery, or validation Markdown report exists.

## Validate IDs, References, and Decisions

- `EPIC-*`, `TASK-*`, `BUG-*`, and `ADR-*` IDs are globally unique by type, zero-padded, allocated from the prior maximum, and never reused.
- TASK numbering does not restart per Epic.
- Every requirement, Epic, Task, Bug, ADR, architecture component, plan, and canonical path reference resolves or is explicitly marked as an approved external reference.
- When work-source references exist, every Backlog `Sources`, TASK `external_sources`, plan coverage, and reverse provenance mapping agrees; non-work profiles require no Epic or Task links.
- Every ADR index row points to one ADR and every ADR appears once in the generated index.
- Accepted ADRs are not rewritten to change decisions; supersession links are consistent.

## Validate Lifecycle and Execution

- Every enum and transition matches `.ai/framework/contracts.yaml`.
- Blocking is stored in `Blocked by` or `blocked_by`, never as a lifecycle status.
- At most one nonterminal active-work Epic is `ACTIVE`, `VALIDATING`, `FUZZING`, or `AWAITING EPIC ACCEPTANCE`, and at most one code-writing TASK is `IN PROGRESS`.
- Every `execution/planned/` workspace maps to one `PLANNED + READY` Backlog Epic, approved plan, approved `TODO` TASK definitions, unique IDs, and no duplicate execution directory.
- Multiple planned workspaces are allowed and ordered only by Backlog priority and row order.
- Non-planned Backlog Epic status matches its directory under `execution/active`, `execution/paused`, or `execution/completed`.
- The active plan's ordered Task list exactly matches its TASK files and dependencies contain no cycle.
- Review Packet, structured review, and selected Task-testing revision/fingerprint evidence matches current implementation; code changes invalidate older evidence.
- Task evidence contains no mandatory full project suite or unscoped project-wide check unless an explicit early-run request is recorded.
- Epic Validation evidence is absent before `VALIDATING`, or current for the exact aggregate fingerprint and contains the full suite, project-wide checks, critical paths, requirement coverage, and applicable quality profiles.
- Fuzzing evidence is absent before passing Epic Validation, or current for the same validated Epic fingerprint.
- Task Acceptance, next Task Start, Epic Start, Replan, ADR Approval, and Epic Acceptance remain separate explicit gates.

If no Epic was activated, report all approved planned workspaces in Backlog order, their Epic Start eligibility or blockers, and that no Task may start before one planned workspace passes Epic Start. Do not claim active development.

## Validate Ownership State

- Framework-owned, project-owned, and generated paths match `.ai/framework/manifest.yaml`.
- `.ai/project.yaml`, `.ai/framework.lock`, `.ai/custom/`, optional `.ai/integrations/`, canonical documents, ADRs, and execution state were not overwritten as framework release content.
- Lock source hashes match actual managed-output inputs: neutral sources, renderers, configuration, and custom overlays. Local integration definitions/state are validated separately and do not create framework drift.
- Generated adapter hashes match current outputs or the collision is explicitly reported.
- Obsolete framework-owned files, including the former Step 05, are absent.

## Validate Both Platform Adapters

- Root `AGENTS.md` and `CLAUDE.md` both exist, are byte-identical lifecycle routers, and are each no more than 150 lines.
- Codex contains every manifest-declared agent under `.codex/agents/` and every manifest-declared skill under `.agents/skills/`.
- Claude contains every manifest-declared agent under `.claude/agents/` and every manifest-declared skill under `.claude/skills/`.
- Every Forge-managed `.claude/agents/*.md` is UTF-8 without BOM and begins at byte zero with `---`, so Claude Code can parse its YAML frontmatter.
- Additional project-owned agents and skills are allowed, excluded from Forge parity counts, and unchanged.
- Unlisted platform configuration, settings, commands, and hooks are preserved and remain outside Forge ownership.
- All rendered agents contain concrete tier mappings and effort.
- `.ai/project.yaml` contains exactly one supported `role_execution.mode` applying to both roles; active-orchestrator requirements agree with cross-provider modes.
- Claude contains `.claude/forge/codex-role-runner.mjs`; Codex contains `.codex/forge/claude-role-runner.mjs`; both launchers match their templates, preserve complete neutral prompts, and expose fresh/read-only runtime metadata.
- The Claude-to-Codex route pins `gpt-5.6-sol/high`; the Codex-to-Claude route uses the configured Claude strong mapping, plan mode, restricted tools, no session persistence, and no nested agents; native mode performs no external preflight.
- Missing selected prerequisites and all post-start failures block the stage. No route implicitly falls back or switches provider.
- The generated set contains `epic-planner` and `epic-validator`; Task `tester` does not require the full project suite and fuzzer requires current Epic Validation evidence.
- IDs, descriptions, tiers, role instructions, permission boundaries, and portable skill bodies have cross-platform parity.
- No unresolved renderer placeholder remains; the shared project overlay appears identically in both routers.
- Both routers state that Forge lifecycle behavior comes only from bundled Forge skills, canonical contracts, and generated agent definitions; external process skills cannot add lifecycle gates, artifacts, transitions, agent routing, or Git actions.
- Both routers contain byte-identical Common Engineering Prohibitions without missing or weakened entries.
- The framework generated no hooks, MCP configuration, or mandatory CLI dependency. Cross-provider modes use user-installed runtimes only when selected; native mode requires neither. Preserve separately recorded project-owned hooks or MCP without treating them as framework output.
- A clean project has no `.ai/integrations/` and passes without connector preflight. Supported, custom, malformed, future-version, or offline integrations remain project-owned; only their consumers are blocked unless an ownership/safety collision exists.

## Simulate Recovery

Ignore conversation history and reconstruct:

1. project language and configuration from `.ai/project.yaml`;
2. target behavior from `SPEC.md`;
3. target architecture and decisions from `ARCHITECTURE.md` and ADRs;
4. priority, readiness, Epic state, and defects from `BACKLOG.md`;
5. the ordered queued Epic set from `execution/planned/` reconciled with Backlog priority, readiness, dependencies and blockers;
6. active or paused Epic strategy and Task order from `plan.md`;
7. current TASK and pending gate from TASK statuses and Workflow State;
8. current Review Packet, selected Task checks, Epic Verification Plan, quality profiles, Epic Validation and fuzzing evidence;
9. unfinished changes from Git status and diff;
10. adapter provenance from `.ai/framework.lock`.
11. optional integration compatibility and work-source relationships from project-owned `.ai/integrations/`, without using them as lifecycle authority.

The same repository state must yield the same current gate. Missing persisted agent evidence means that stage must be rerun.

## Completion

Return a concise pass/fail result in the conversation with exact paths and violated invariants for any failure. Do not create a Markdown report.

When every check passes:

- mark no additional lifecycle state;
- state that bootstrap is complete;
- identify the first eligible TASK, which must remain `TODO`;
- ask for a separate explicit Task Start authorization.

Do not start implementation, invoke the implementer, or commit automatically.
