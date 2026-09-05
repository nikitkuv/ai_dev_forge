# Bootstrap Step 06 — Final Validation

## Purpose

Perform a read-only final conformance check and prove that a new orchestrator can recover the project and ad hoc investigation state without session history.

Do not redesign, implement, silently repair canonical state, or create a validation report file.

## Required Inputs

Read the framework manifest and lifecycle/investigation/integration/mutation-testing contracts, project configuration and lock, canonical documents, ADRs, execution tree, neutral sources, all enabled generated adapter sets, custom overlays, optional project-owned investigations, integration definitions/state, mutation history, and Git state. Do not invoke local connectors, OpenCode providers, or mutation backends.

If an earlier step is incomplete, return to that step and its approval gate.

## Validate Canonical Documents

- Required root files exist for the completed bootstrap stage.
- Root `README.md` contains confirmed setup/run/test orientation and links to canonical documents plus the shared Codex/OpenCode router and Claude import, without becoming a source of product, architecture, or execution truth.
- SPEC, ARCHITECTURE, BACKLOG, and plan frontmatter has valid `document_status`, language, dates, and approval metadata.
- TASK frontmatter separates `definition_status` from lifecycle `status`.
- ADR status uses the decision lifecycle and `DECISIONS.md` exactly reflects ADR frontmatter.
- Approved documents contain no unresolved template placeholders.
- Canonical documents use the project documentation language; technical IDs, statuses, paths, commands, and model IDs remain English.
- SPEC owns target product behavior and contains no architecture, Tasks, or implementation status.
- ARCHITECTURE owns target architecture and contains no task-level execution steps.
- BACKLOG owns Epic priority/readiness/status and defect state, with no Task list or execution summaries.
- Each plan owns Epic strategy, Task order, requirement coverage, selected quality profiles, Epic Verification Plan, Epic Validation evidence, fuzzing and user validation, but no Task lifecycle state.
- Each TASK owns its lifecycle, affected surface, production/supporting path classification, whole-implementation and production-surface fingerprints, risk flags, approved delivery track and rationale, review focus, selected Verification Plan, and compact implementation, track-specific assurance, and user-validation evidence.
- No separate framework-generated progress, checkpoint, review, testing, fuzzing, security, recovery, or validation Markdown report exists.

## Validate IDs, References, and Decisions

- `EPIC-*`, `TASK-*`, `BUG-*`, `ADR-*`, and `INV-*` IDs are globally unique by type, zero-padded, allocated from the prior maximum, and never reused.
- TASK numbering does not restart per Epic.
- Every requirement, Epic, Task, Bug, ADR, architecture component, plan, and canonical path reference resolves or is explicitly marked as an approved external reference.
- When work-source references exist, every Backlog `Sources`, TASK `external_sources`, plan coverage, and reverse provenance mapping agrees; non-work profiles require no Epic or Task links.
- Every ADR index row points to one ADR and every ADR appears once in the generated index.
- Accepted ADRs are not rewritten to change decisions; supersession links are consistent.
- Every `INV-NNNN` path matches its ID and contains the required question, scope, investigation, evidence, causes, conclusion, next action, linked work, and outcome history. Its outcome is `no_action`, `promoted`, `fixed_directly`, or `unresolved`; promoted work has reciprocal references, and direct fixes have a complete path-level ledger, verification, risks, and final revision/commit/scoped-diff reference.

## Validate Lifecycle and Execution

- Every enum and transition matches `.ai/framework/contracts.yaml`.
- Blocking is stored in `Blocked by` or `blocked_by`, never as a lifecycle status.
- At most one nonterminal active-work Epic is `ACTIVE`, `VALIDATING`, `FUZZING`, or `AWAITING EPIC ACCEPTANCE`, and at most one code-writing TASK is `IN PROGRESS`.
- Every `execution/planned/` workspace maps to one `PLANNED + READY` Backlog Epic, approved plan, approved `TODO` TASK definitions, unique IDs, and no duplicate execution directory.
- Multiple planned workspaces are allowed and ordered only by Backlog priority and row order.
- Non-planned Backlog Epic status matches its directory under `execution/active`, `execution/paused`, or `execution/completed`.
- The active plan's ordered Task list exactly matches its TASK files and dependencies contain no cycle.
- Every TASK has exactly one `fast` or `standard` delivery track independently from model tier and risk level. Missing legacy track means standard. Fast has complete positive eligibility/disqualifier evidence and current orchestrator assurance on the exact whole-implementation fingerprint; standard has current Review Packet, clean structured review, and selected Task testing. Standard-to-fast after Task Start is forbidden and any fast eligibility failure is recorded as escalation to standard.
- Standard Review Packet path classification is complete and production-effect based. Clean structured review matches the current production-surface fingerprint; legacy review without that fingerprint is stale. Supporting-only changes preserve clean production review but invalidate affected testing, while production changes invalidate both. Selected Task-testing evidence matches the current implementation revision and whole-implementation fingerprint. Any fast implementation change invalidates its entire Fast Assurance Summary.
- Task evidence contains no mandatory full project suite or unscoped project-wide check unless an explicit early-run request is recorded.
- Epic Validation evidence is absent before `VALIDATING`, or current for the exact aggregate fingerprint and contains the full suite, project-wide checks, critical paths, requirement coverage, and applicable quality profiles.
- Fuzzing evidence is absent before passing Epic Validation, or current for the same validated Epic fingerprint. A `NOT APPLICABLE` result without a fuzzer invocation requires an approved `not applicable` plan, all final Task fuzzing impacts `none`, matching affected surfaces, passing alternative coverage, and recorded orchestrator freshness evidence; every `applicable`, `unresolved`, or contradictory case requires fuzzer evidence.
- Task Acceptance, next Task Start, Epic Start, Replan, ADR Approval, and Epic Acceptance remain separate explicit gates.

If no Epic was activated, report all approved planned workspaces in Backlog order, their Epic Start eligibility or blockers, and that no Task may start before one planned workspace passes Epic Start. Do not claim active development.

## Validate Ownership State

- Framework-owned, project-owned, and generated paths match `.ai/framework/manifest.yaml`.
- `.ai/project.yaml`, `.ai/framework.lock`, `.ai/custom/`, optional `investigations/`, optional `.ai/integrations/`, optional `quality/mutation-testing/`, canonical documents, ADRs, and execution state were not overwritten as framework release content.
- Lock source hashes match actual managed-output inputs: neutral sources, renderers, configuration, and custom overlays. Local integration definitions/state are validated separately and do not create framework drift.
- Generated adapter hashes match current outputs or the collision is explicitly reported.
- Obsolete framework-owned files, including the former Step 05, are absent.

## Validate Platform Adapters

- Root `AGENTS.md` and `CLAUDE.md` both exist. `AGENTS.md` is the complete lifecycle router and is no more than 150 lines; `CLAUDE.md` contains exactly `@AGENTS.md`.
- Codex contains every manifest-declared agent under `.codex/agents/` and every manifest-declared skill under `.agents/skills/`.
- Claude contains every manifest-declared agent under `.claude/agents/` and every manifest-declared skill under `.claude/skills/`.
- Enabled OpenCode contains every manifest-declared agent under `.opencode/agents/`, uses root `AGENTS.md`, and discovers every manifest-declared skill under `.agents/skills/`; Forge generated no duplicate `.opencode/skills/`.
- Every Forge-managed `.claude/agents/*.md` and `.opencode/agents/*.md` is UTF-8 without BOM and begins at byte zero with `---`, so the platform can parse its YAML frontmatter.
- Additional project-owned agents and skills are allowed, excluded from Forge parity counts, and unchanged.
- Unlisted platform configuration, settings, commands, hooks, `opencode.json`, OpenCode plugins/skills, and unlisted OpenCode agents are preserved and remain outside Forge ownership.
- All rendered agents contain concrete tier mappings; Codex and Claude also contain applicable effort. Enabled OpenCode tiers are non-empty provider-qualified `provider/model-id` values.
- `.ai/project.yaml` contains exactly one supported `role_execution.mode` applying to both roles; active-orchestrator requirements agree with cross-provider modes.
- Claude contains `.claude/forge/codex-role-runner.mjs`; Codex contains `.codex/forge/claude-role-runner.mjs`; both launchers match their templates, preserve complete neutral prompts, and expose fresh/read-only runtime metadata.
- The Claude-to-Codex route pins `gpt-5.6-sol/medium`; the Codex-to-Claude route uses the configured Claude strong mapping, plan mode, restricted tools, no session persistence, and no nested agents; native mode supports Codex, Claude Code, and OpenCode and performs no external preflight. OpenCode-led setup proposes this existing mode by default only when no approved route exists and records it only after approval.
- Missing selected prerequisites and all post-start failures block the stage. No route implicitly falls back or switches provider.
- The generated set contains `epic-planner` and `epic-validator`; Task `tester` does not require the full project suite, and fuzzer requires current Epic Validation evidence plus planned `applicable`, `unresolved`, or contradictory final evidence.
- IDs, descriptions, tiers, role instructions, permission boundaries, and portable skill bodies have cross-platform parity. Only OpenCode implementer permits edits; command/research access follows neutral capability, and every OpenCode subagent denies external-directory and nested task access.
- No unresolved renderer placeholder remains; the shared project overlay appears once in `AGENTS.md` and is available to Claude through the import.
- The imported router states that Forge lifecycle behavior comes only from bundled Forge skills, canonical contracts, and generated agent definitions; external process skills cannot add lifecycle gates, artifacts, transitions, agent routing, or Git actions.
- The imported router contains the complete Common Engineering Prohibitions without missing or weakened entries.
- The framework generated no hooks, MCP configuration, or mandatory CLI dependency. Cross-provider modes use user-installed runtimes only when selected; native mode requires neither. Preserve separately recorded project-owned hooks or MCP without treating them as framework output.
- A clean project has no `.ai/integrations/` and passes without connector preflight. Supported, custom, malformed, future-version, or offline integrations remain project-owned; only their consumers are blocked unless an ownership/safety collision exists.
- A clean project has no `quality/mutation-testing/` and passes without a mutation backend or preflight. When history exists, registry and `MUT-NNNN` records pass the independent schema, identity, fingerprint, metrics, artifact, analysis-authorization and disposition checks; their outcomes have no lifecycle or gate effect.
- The generated set contains fast `mutation-runner`, strong `mutation-analyzer`, and discoverable `forge-mutation-test` on every enabled platform. Metrics-only is the default, strong analysis requires explicit authorization plus current candidates and budget, and neither role may install tools, edit tracked files, remediate, change lifecycle state, or spawn agents.
- The generated skill set contains `forge-investigate` on every enabled platform. It is a main-agent workflow, invokes no generated subagent, stores one project-owned INV record, and never changes Epic/TASK state or authorizes a commit implicitly.

## Simulate Recovery

Ignore conversation history and reconstruct:

1. project language and configuration from `.ai/project.yaml`;
2. target behavior from `SPEC.md`;
3. target architecture and decisions from `ARCHITECTURE.md` and ADRs;
4. priority, readiness, Epic state, and defects from `BACKLOG.md`;
5. the ordered queued Epic set from `execution/planned/` reconciled with Backlog priority, readiness, dependencies and blockers;
6. active or paused Epic strategy and Task order from `plan.md`;
7. current TASK and pending gate from TASK statuses and Workflow State;
8. current Review Packet with production/supporting classification and both fingerprints, separate production findings and non-production observations, selected Task checks, Epic Verification Plan, quality profiles, Epic Validation and fuzzing evidence;
9. unfinished changes from Git status and diff;
10. adapter provenance from `.ai/framework.lock`.
11. optional integration compatibility and work-source relationships from project-owned `.ai/integrations/`, without using them as lifecycle authority;
12. optional mutation history from `quality/mutation-testing/`, without using it as lifecycle or development evidence authority.
13. optional ad hoc investigations from `investigations/`, including unresolved work, direct changes, reciprocal planning references, and any lifecycle evidence made stale by those changes.

The same repository state must yield the same current gate. Missing persisted agent evidence means that stage must be rerun.

## Completion

Return a concise pass/fail result in the conversation with exact paths and violated invariants for any failure. Do not create a Markdown report.

When every check passes:

- mark no additional lifecycle state;
- state that bootstrap is complete;
- identify the first eligible TASK, which must remain `TODO`;
- ask for a separate explicit Task Start authorization.

Do not start implementation, invoke the implementer, or commit automatically.
