# Bootstrap Step 06 — Final Validation

## Purpose

Perform a read-only final conformance check and prove that a new orchestrator can recover the project state without session history.

Do not redesign, implement, silently repair canonical state, or create a validation report file.

## Required Inputs

Read the framework manifest and contracts, project configuration and lock, canonical documents, ADRs, execution tree, neutral sources, both generated adapter sets, custom overlays, and Git state.

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
- Each plan owns Epic strategy and Task order but no Task lifecycle state.
- Each TASK owns its lifecycle and compact implementation, review, testing, and user-validation evidence.
- No separate framework-generated progress, checkpoint, review, testing, fuzzing, security, recovery, or validation Markdown report exists.

## Validate IDs, References, and Decisions

- `EPIC-*`, `TASK-*`, `BUG-*`, and `ADR-*` IDs are globally unique by type, zero-padded, allocated from the prior maximum, and never reused.
- TASK numbering does not restart per Epic.
- Every requirement, Epic, Task, Bug, ADR, architecture component, plan, and canonical path reference resolves or is explicitly marked as an approved external reference.
- Every ADR index row points to one ADR and every ADR appears once in the generated index.
- Accepted ADRs are not rewritten to change decisions; supersession links are consistent.

## Validate Lifecycle and Execution

- Every enum and transition matches `.ai/framework/contracts.yaml`.
- Blocking is stored in `Blocked by` or `blocked_by`, never as a lifecycle status.
- At most one Epic is `ACTIVE` and at most one code-writing TASK is `IN PROGRESS`.
- Backlog Epic status matches its directory under `execution/active`, `execution/paused`, or `execution/completed`.
- The active plan's ordered Task list exactly matches its TASK files and dependencies contain no cycle.
- Review and testing revision/fingerprint evidence matches current implementation; code changes invalidate older evidence.
- Fuzzing evidence is absent before required, or current for the accepted Epic revision.
- Task Acceptance, next Task Start, Epic Start, Replan, ADR Approval, and Epic Acceptance remain separate explicit gates.

If no Epic was activated, report that bootstrap is planning-ready but paused before Epic Start. Do not claim development readiness.

## Validate Ownership and Migration State

- Framework-owned, project-owned, and generated paths match `.ai/framework/manifest.yaml`.
- `.ai/project.yaml`, `.ai/framework.lock`, `.ai/custom/`, canonical documents, ADRs, and execution state were not overwritten as framework release content.
- Lock source hashes match the current neutral sources, renderers, configuration, and custom overlays.
- Generated adapter hashes match current outputs or the collision is explicitly reported.
- Obsolete framework-owned files, including the former Step 05, are absent.

## Validate Both Platform Adapters

- Root `AGENTS.md` and `CLAUDE.md` both exist, act only as lifecycle routers, and are each no more than 150 lines.
- Codex contains seven `.codex/agents/*.toml` files and fourteen `.agents/skills/*/SKILL.md` files.
- Claude contains seven `.claude/agents/*.md` files and fourteen `.claude/skills/*/SKILL.md` files.
- All rendered agents contain concrete tier mappings; Codex also contains reasoning effort.
- IDs, descriptions, tiers, role instructions, permission boundaries, and portable skill bodies have cross-platform parity.
- No unresolved renderer placeholder remains.
- Both routers state that Forge lifecycle behavior comes only from bundled Forge skills, canonical contracts, and generated agent definitions; external process skills cannot add lifecycle gates, artifacts, transitions, agent routing, or Git actions.
- The framework generated no hooks, MCP configuration, or CLI dependency. Preserve separately recorded project-owned hooks or MCP without treating them as framework output.

## Simulate Recovery

Ignore conversation history and reconstruct:

1. project language and configuration from `.ai/project.yaml`;
2. target behavior from `SPEC.md`;
3. target architecture and decisions from `ARCHITECTURE.md` and ADRs;
4. priority, readiness, Epic state, and defects from `BACKLOG.md`;
5. active or paused Epic strategy and Task order from `plan.md`;
6. current TASK and pending gate from TASK statuses and Workflow State;
7. unfinished changes from Git status and diff;
8. adapter provenance from `.ai/framework.lock`.

The same repository state must yield the same current gate. Missing persisted agent evidence means that stage must be rerun.

## Completion

Return a concise pass/fail result in the conversation with exact paths and violated invariants for any failure. Do not create a Markdown report.

When every check passes:

- mark no additional lifecycle state;
- state that bootstrap is complete;
- identify the first eligible TASK, which must remain `TODO`;
- ask for a separate explicit Task Start authorization.

Do not start implementation, invoke the implementer, or commit automatically.
