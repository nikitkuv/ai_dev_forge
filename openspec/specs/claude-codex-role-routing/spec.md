# Claude Codex Role Routing Specification

## Purpose

Defines deterministic, read-only routing from Claude Code orchestration to Codex for Epic planning and independent Task review, with the existing native Claude role subagents retained as a preflight fallback.


## Requirements

### Requirement: Project selects one role-execution mode

Forge SHALL require one project-owned `role_execution.mode` value applying together to `epic-planner` and `reviewer`. The supported values SHALL be `claude_with_codex`, `codex_with_claude`, and `native_subagents`; missing, unknown, or per-role mixed configuration SHALL block workflows that require either selected role without blocking unrelated lifecycle work.

#### Scenario: New project selects Claude with Codex
- **WHEN** bootstrap records the user's `claude_with_codex` choice
- **THEN** both selected roles are configured for Claude orchestration with Codex plugin execution

#### Scenario: New project selects Codex with Claude
- **WHEN** bootstrap records the user's `codex_with_claude` choice
- **THEN** both selected roles are configured for Codex orchestration with headless Claude Code execution

#### Scenario: New project selects native agents
- **WHEN** bootstrap records the user's `native_subagents` choice
- **THEN** both selected roles use the active platform's generated native subagents without external-runtime preflight

#### Scenario: Mode is unresolved
- **WHEN** either selected role is required and `role_execution.mode` is absent or invalid
- **THEN** Forge identifies the configuration problem and does not infer a provider

### Requirement: Claude-to-Codex mode uses the managed plugin route

When `role_execution.mode` is `claude_with_codex`, Forge SHALL require Claude Code as the active orchestrator and SHALL execute both selected roles through the managed `openai/codex-plugin-cc` runtime using a fresh foreground read-only Codex task pinned to `gpt-5.6-sol` with `medium` reasoning.

#### Scenario: Claude plans an Epic
- **WHEN** Claude Code reaches Epic planning in `claude_with_codex` mode and preflight succeeds
- **THEN** it sends the complete neutral planner contract and current planning evidence through the managed Codex launcher

#### Scenario: Claude reviews a Task
- **WHEN** Claude Code reaches Task review in `claude_with_codex` mode and preflight succeeds
- **THEN** it sends the complete neutral reviewer contract and exact current Review Packet through the managed Codex launcher

#### Scenario: Codex is the active orchestrator for this mode
- **WHEN** Codex reaches either selected role while the project is configured as `claude_with_codex`
- **THEN** the stage blocks with an active-orchestrator mismatch and does not invoke a native or external role

### Requirement: Codex-to-Claude mode uses headless Claude Code

When `role_execution.mode` is `codex_with_claude`, Forge SHALL require Codex CLI as the active orchestrator and SHALL execute both selected roles through a managed, fresh, foreground, non-persistent Claude Code `--print` process using the configured Claude strong model and effort. The process SHALL run in plan permission mode with a restricted read-oriented tool surface, SHALL NOT enable editing, bypass permissions, external connectors, browser tools, session resume, or nested agents, and SHALL return machine-parseable output and effective runtime metadata.

#### Scenario: Codex plans an Epic through Claude
- **WHEN** Codex reaches Epic planning in `codex_with_claude` mode and Claude preflight succeeds
- **THEN** it starts a fresh headless Claude Code planner call with the complete neutral planner contract and current planning evidence

#### Scenario: Codex reviews a Task through Claude
- **WHEN** Codex reaches Task review in `codex_with_claude` mode and Claude preflight succeeds
- **THEN** it starts a fresh headless Claude Code reviewer call with the complete neutral reviewer contract and exact current Review Packet

#### Scenario: Claude is the active orchestrator for this mode
- **WHEN** Claude Code reaches either selected role while the project is configured as `codex_with_claude`
- **THEN** the stage blocks with an active-orchestrator mismatch and does not invoke a native or external role

### Requirement: Native mode uses active-platform subagents

When `role_execution.mode` is `native_subagents`, Forge SHALL execute `epic-planner` and `reviewer` through the generated native subagent definitions of the active Codex or Claude orchestrator and SHALL NOT preflight or invoke the other provider. Every generated Claude Code native subagent SHALL use `high` reasoning effort in this mode; Codex native subagents SHALL retain their configured tier effort, and the Claude override SHALL NOT alter the configured effort used by `codex_with_claude`.

#### Scenario: Native execution in Codex
- **WHEN** Codex reaches either selected role in `native_subagents` mode
- **THEN** it invokes the matching generated Codex agent with the current assignment

#### Scenario: Native execution in Claude
- **WHEN** Claude Code reaches either selected role in `native_subagents` mode
- **THEN** it invokes the matching generated Claude agent with the current assignment and `high` reasoning effort

### Requirement: Explicit external selection has no provider fallback

Before an external role starts, the active orchestrator SHALL verify the prerequisites required by the selected mode. Missing plugin/runtime, executable, supported version, or authentication SHALL block that stage with actionable diagnostics. After external execution starts, a non-zero exit, timeout, malformed output, permission failure, or runtime/model/mode mismatch SHALL also block the stage. Forge SHALL NOT invoke a native subagent or the other external provider for the same attempt.

#### Scenario: Selected Codex route is unavailable
- **WHEN** `claude_with_codex` preflight cannot establish every prerequisite
- **THEN** planning or review blocks and reports the missing prerequisite without native Claude fallback

#### Scenario: Selected Claude route is unavailable
- **WHEN** `codex_with_claude` preflight cannot establish a supported authenticated Claude Code CLI
- **THEN** planning or review blocks and reports the missing prerequisite without native Codex fallback

#### Scenario: Started external run fails
- **WHEN** either external provider starts but fails or returns an invalid role result
- **THEN** no successful planning or review evidence is recorded and no alternate provider is invoked

### Requirement: Delegated assignments preserve role contracts and orchestration gates

Every native or external invocation SHALL receive the complete current neutral role instructions and the same assignment evidence for that attempt. The orchestrator SHALL validate the returned contract and remain the sole owner of lifecycle transitions, approvals, canonical writes, user communication, and remediation routing.

#### Scenario: Planner receives canonical evidence
- **WHEN** any configured route invokes `epic-planner`
- **THEN** the assignment preserves all canonical, repository, CI, quality, convention, contract, and template evidence required by `forge-prepare-epic`

#### Scenario: Reviewer receives exact packet
- **WHEN** any configured route invokes `reviewer`
- **THEN** the assignment preserves the exact current fingerprint-bound Review Packet required by `forge-run-task`

#### Scenario: Process exits successfully with malformed output
- **WHEN** a native or external role omits required result sections or mismatches the assignment fingerprint
- **THEN** the orchestrator blocks the stage rather than treating process success as approval

### Requirement: Bootstrap and migration preserve explicit user choice

Bootstrap SHALL ask the user to select one supported mode and persist it in `.ai/project.yaml`. Migration from a release without the field SHALL show the existing effective routing, offer a compatibility-preserving value, and require approval before writing the new setting. Changing the mode SHALL require explicit user approval and adapter synchronization.

#### Scenario: Existing preferred Claude-to-Codex project migrates
- **WHEN** a project using the previous implicit preferred route is migrated
- **THEN** Forge offers `claude_with_codex` as the compatibility-preserving selection but does not silently choose it

#### Scenario: User changes provider mode
- **WHEN** the user approves a different supported mode
- **THEN** Forge updates project configuration and atomically synchronizes both adapters before the new route is used

### Requirement: Generated adapters expose every configured route safely

Adapter generation SHALL retain all neutral role definitions and all native Codex and Claude agent files, generate both managed external launchers, render the complete three-mode router guidance once in root `AGENTS.md`, and render root `CLAUDE.md` as the exact `@AGENTS.md` import. Generation SHALL not install, authenticate, preflight, or invoke an external provider. Validation SHALL verify the import, role-contract parity, launcher permission boundaries, route metadata, configuration validity, and preservation of unrelated platform files.

#### Scenario: External prerequisites are absent during generation
- **WHEN** adapters are generated without Codex plugin or Claude Code runtime availability
- **THEN** generation succeeds with both launchers and every native agent because runtime availability is checked only when the selected role executes

#### Scenario: Route configuration changes
- **WHEN** the approved mode changes and adapters synchronize successfully
- **THEN** both generated platforms and the framework lock reflect the same selected mode without changing neutral role instructions
