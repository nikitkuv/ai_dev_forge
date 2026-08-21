## Purpose

Defines deterministic, read-only routing from Claude Code orchestration to Codex for Epic planning and independent Task review, with the existing native Claude role subagents retained as a preflight fallback.

## ADDED Requirements

### Requirement: Claude routes selected roles to Codex
When the active orchestrator is Claude Code and preflight establishes that the `openai/codex-plugin-cc` runtime and its prerequisites are available, the system SHALL execute `epic-planner` and `reviewer` assignments as Codex tasks rather than invoking native Claude subagents. The Codex adapter SHALL continue to invoke its native generated agents, and Claude SHALL continue to use native agents for every other role.

#### Scenario: Epic planning in Claude Code
- **WHEN** a Claude Code orchestrator reaches the planning step of `forge-prepare-epic`
- **THEN** it runs preflight and starts a Codex-backed `epic-planner` task when the integration is available

#### Scenario: Task review in Claude Code
- **WHEN** a Claude Code orchestrator reaches the review step of `forge-run-task`
- **THEN** it runs preflight and starts a Codex-backed `reviewer` task when the integration is available

#### Scenario: Native Codex execution remains unchanged
- **WHEN** the active orchestrator is Codex
- **THEN** `epic-planner` and `reviewer` continue to run through their generated Codex agent definitions

### Requirement: Delegated assignments preserve role contracts
Each Codex-backed call SHALL receive the complete current neutral role instructions for the selected role plus the same assignment evidence that the orchestrator would have supplied to the corresponding native subagent. The call SHALL preserve the Epic planning input or exact Review Packet without silently dropping, summarizing, or weakening constraints.

#### Scenario: Planner receives canonical evidence
- **WHEN** Claude delegates an Epic planning assignment
- **THEN** the Codex prompt contains the complete `epic-planner` contract and the selected Epic's canonical, repository, CI, quality, convention, contract, and template evidence required by `forge-prepare-epic`

#### Scenario: Reviewer receives the exact packet
- **WHEN** Claude delegates a Task review assignment
- **THEN** the Codex prompt contains the complete `reviewer` contract and the exact Review Packet for the current implementation revision and fingerprint

### Requirement: Codex runtime is deterministic and read-only
Every Claude-originated planner or reviewer call SHALL start a fresh foreground Codex task with model `gpt-5.6-sol`, reasoning effort `high`, and read-only filesystem behavior. It SHALL NOT request write mode, resume an earlier Codex task, enable network access beyond existing role policy, or allow the delegated task to invoke additional agents.

#### Scenario: Explicit runtime selection
- **WHEN** either selected role is delegated from Claude Code
- **THEN** the effective Codex run reports model `gpt-5.6-sol`, reasoning effort `high`, a fresh thread, and read-only execution

#### Scenario: Project model overrides exist
- **WHEN** `.ai/project.yaml` maps Claude or Codex strong tier to another model or effort
- **THEN** the Claude-originated planner and reviewer calls still use `gpt-5.6-sol` with `high` reasoning

### Requirement: Orchestrator owns result handling
The Claude orchestrator SHALL wait for the Codex result, validate it against the existing planner or reviewer output contract, and remain the sole owner of lifecycle transitions, approvals, canonical writes, and routing of findings. Codex output SHALL NOT be treated as approval or completion merely because the process exits successfully.

#### Scenario: Clean reviewer output
- **WHEN** Codex returns a protocol-complete review with no actionable findings
- **THEN** the orchestrator may continue to the existing testing gate only after validating packet integrity, acceptance traceability, protocol coverage, and the `CLEAN` outcome

#### Scenario: Reviewer findings
- **WHEN** Codex returns actionable review findings
- **THEN** the orchestrator returns the Task to the existing remediation loop and never lets Codex route findings directly to the implementer

#### Scenario: Planner proposal
- **WHEN** Codex returns an Epic planning proposal
- **THEN** the orchestrator independently verifies it and retains the existing Plan Approval and Epic Start gates

### Requirement: Unavailable Codex integration falls back before execution
Before either selected stage runs, the Claude orchestrator SHALL verify that the Codex plugin runtime, supported Node.js runtime, Codex CLI, and Codex authentication are available. If preflight cannot establish availability, the orchestrator SHALL execute the same assignment through the existing native Claude `epic-planner` or `reviewer` subagent and SHALL report that fallback was used. The fallback SHALL preserve the same neutral role contract, evidence, lifecycle gates, and result validation.

#### Scenario: Planner prerequisite is missing
- **WHEN** the Codex plugin, Node.js, Codex CLI, or authentication is unavailable
- **THEN** Epic planning runs through the native Claude `epic-planner` subagent and the orchestrator reports the unavailable prerequisite

#### Scenario: Reviewer prerequisite is missing
- **WHEN** the Codex plugin, Node.js, Codex CLI, or authentication is unavailable at the Task review stage
- **THEN** review runs through the native Claude `reviewer` subagent with the exact current Review Packet and the orchestrator reports the unavailable prerequisite

### Requirement: Started Codex failures fail closed
A non-zero process exit, timeout, malformed output, or runtime/model mismatch after a Codex task has started SHALL block the stage with actionable diagnostics. The orchestrator SHALL NOT rerun that assignment through a native Claude subagent, because doing so would hide an execution failure and mix evidence providers for the same attempt.

#### Scenario: Delegated run fails
- **WHEN** the Codex task exits non-zero, times out, or returns an invalid role result
- **THEN** the orchestrator records no successful planning or review evidence, reports the failure, and does not invoke a Claude fallback subagent

### Requirement: Generated adapters expose the correct platform surface
Adapter generation SHALL retain the neutral `epic-planner` and `reviewer` definitions and generate both their Codex agent files and their native Claude agent files. Generated Claude guidance SHALL declare the preferred plugin route, its preflight boundary, and the native fallback behavior. Validation SHALL verify role contract parity across the neutral definitions, Codex agents, Claude agents, and Claude Codex-routing prompts.

#### Scenario: Fresh Claude adapter generation
- **WHEN** platform adapters are generated or synchronized
- **THEN** the Claude adapter contains managed native agent files for `epic-planner` and `reviewer` plus deterministic instructions for both preferred Codex-backed routes

#### Scenario: Plugin is not installed during generation
- **WHEN** adapter generation cannot verify a local plugin installation
- **THEN** it still generates valid native Claude fallback agents and records the Codex path as unavailable without failing adapter generation
