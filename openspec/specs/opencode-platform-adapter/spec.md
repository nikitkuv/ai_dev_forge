# OpenCode Platform Adapter Specification

## Purpose

Defines how AI Development Forge generates, validates, migrates, and operates a native OpenCode adapter while preserving shared routing, portable skills, neutral role boundaries, and project-owned OpenCode configuration.

## Requirements

### Requirement: OpenCode is a first-class platform adapter
Forge SHALL support `opencode` as a platform alongside `codex` and `claude`. When OpenCode is enabled for a project, bootstrap, adapter synchronization, migration, framework locking, and final validation SHALL include the OpenCode adapter in the same atomic operation as every other enabled adapter.

#### Scenario: New project enables all platforms
- **WHEN** bootstrap completes with Codex, Claude Code, and OpenCode enabled
- **THEN** the project contains conforming generated outputs for all three platforms and one lock records their managed membership and hashes

#### Scenario: One staged adapter fails validation
- **WHEN** any enabled Codex, Claude, or OpenCode staged output fails pre-replacement validation
- **THEN** Forge replaces none of the enabled adapter sets and reports the failing platform and invariant

### Requirement: OpenCode reuses the single root router and portable skills
Forge SHALL use root `AGENTS.md` as the complete OpenCode project router and SHALL expose every manifest-declared skill to OpenCode through `.agents/skills/<id>/SKILL.md`. Forge SHALL NOT generate an OpenCode-only router, duplicate Forge skills into `.opencode/skills/`, or require `CLAUDE.md` fallback for OpenCode routing.

#### Scenario: OpenCode starts in a generated project
- **WHEN** OpenCode loads the project root
- **THEN** it receives the complete Forge router from `AGENTS.md` and discovers every manifest skill from `.agents/skills/`

#### Scenario: Project has OpenCode-owned skills
- **WHEN** `.opencode/skills/` contains project-owned definitions
- **THEN** adapter generation preserves them unchanged and excludes them from Forge parity counts and managed ownership

### Requirement: Every neutral subagent has a native OpenCode definition
For every subagent ID declared by the framework manifest, Forge SHALL generate `.opencode/agents/<id>.md` as UTF-8 without BOM. Each definition SHALL begin with valid YAML frontmatter containing the neutral description, `mode: subagent`, a resolved tier model, and permissions that do not exceed the neutral write, network, execution, or spawn policies. The body SHALL contain the same English role contract rendered for the other platforms.

#### Scenario: Read-only reviewer is rendered
- **WHEN** Forge renders the `reviewer` OpenCode agent
- **THEN** the definition denies editing, network access, external-directory access, and nested task invocation while retaining only the local read and command capabilities required by the neutral reviewer contract

#### Scenario: Implementer is rendered
- **WHEN** Forge renders the `implementer` OpenCode agent
- **THEN** the definition allows local editing and required local command execution, denies unassigned network and nested task invocation, and retains the neutral assigned-scope constraints in its body

#### Scenario: Documentation researcher is rendered
- **WHEN** Forge renders the `documentation-researcher` OpenCode agent
- **THEN** the definition denies editing and nested task invocation, permits documentation research tools, and retains the neutral assigned-research and primary-source restrictions

#### Scenario: Agent file has a BOM
- **WHEN** a generated OpenCode agent does not start at byte zero with the first `-` of `---`
- **THEN** adapter validation fails before any enabled adapter output is replaced

### Requirement: OpenCode model tiers are explicit and provider-qualified
An enabled OpenCode platform SHALL have non-empty `strong`, `balanced`, and `fast` model mappings in `.ai/project.yaml`. Every mapping SHALL use OpenCode's `provider/model-id` form and SHALL be selected from local evidence or explicit user input. Forge SHALL NOT invent a provider or model, silently inherit the orchestrator model for all tiers, install a provider, authenticate an account, or store credentials.

#### Scenario: Model mappings are resolved
- **WHEN** all three OpenCode tiers contain explicit provider-qualified model IDs
- **THEN** every generated OpenCode agent receives the concrete model for its neutral tier

#### Scenario: A tier is unresolved or malformed
- **WHEN** OpenCode is enabled and any tier is null, empty, or lacks the provider/model separator
- **THEN** OpenCode adapter generation is blocked with the exact unresolved tier and no adapter set is replaced

#### Scenario: OpenCode is disabled during migration
- **WHEN** an existing project explicitly keeps OpenCode disabled
- **THEN** migration preserves that decision, does not require OpenCode model resolution, and does not create Forge-managed OpenCode agents

### Requirement: OpenCode defaults to the existing native subagent route without adding modes
When bootstrap or migration configures an OpenCode-led workflow and no approved route exists, Forge SHALL propose the existing `native_subagents` value by default for both `epic-planner` and `reviewer`. Forge SHALL NOT add an OpenCode-specific route mode or extend the `role_execution.mode` enum. The selected value SHALL still pass the normal explicit approval gate and be recorded in `.ai/project.yaml`; an already approved route SHALL be preserved until the user explicitly changes it. The `claude_with_codex` and `codex_with_claude` modes SHALL retain their Claude Code and Codex orchestrator requirements. An active-orchestrator mismatch SHALL block only the selected planner or reviewer stage and SHALL NOT fall back to native OpenCode agents or another route.

#### Scenario: OpenCode-led bootstrap has no prior route
- **WHEN** bootstrap is configuring OpenCode as the operating platform and `role_execution.mode` has not been approved
- **THEN** Forge proposes `native_subagents` as the default choice for both managed roles and records it only after the normal explicit user approval

#### Scenario: Native OpenCode planning is selected
- **WHEN** the active orchestrator is OpenCode and `role_execution.mode` is `native_subagents`
- **THEN** the orchestrator invokes the generated OpenCode `epic-planner` without an external runtime preflight

#### Scenario: Migration already has an approved route
- **WHEN** an existing project enables OpenCode but already has an approved `role_execution.mode`
- **THEN** migration preserves that value and reports any OpenCode orchestrator mismatch instead of silently rewriting it to `native_subagents`

#### Scenario: Cross-runtime route mismatches OpenCode
- **WHEN** the active orchestrator is OpenCode and a cross-runtime mode requiring Claude Code or Codex is selected
- **THEN** the selected planner or reviewer stage is blocked with an orchestrator-mismatch result and no fallback occurs

### Requirement: Project-owned OpenCode configuration is preserved
Forge SHALL manage only manifest-declared `.opencode/agents/<id>.md` entries. It SHALL preserve `opencode.json`, `.opencode/commands/`, `.opencode/plugins/`, `.opencode/skills/`, unlisted `.opencode/agents/`, provider configuration, credentials, policies, hooks, and MCP definitions as project-owned content. Adapter generation SHALL NOT create or modify those files.

#### Scenario: Existing OpenCode project content is present
- **WHEN** adapter synchronization finds an existing `opencode.json`, custom command, plugin, skill, or unlisted agent
- **THEN** it leaves the content unchanged and records preserved unlisted paths without claiming their content as Forge-owned

#### Scenario: Managed agent has a manual edit
- **WHEN** an existing manifest-declared OpenCode agent differs from its lock hash
- **THEN** Forge reports the exact collision and requires explicit confirmation before overwriting it

### Requirement: Cross-platform parity includes OpenCode
Forge validation SHALL compare every manifest-declared Codex, Claude, and enabled OpenCode agent for ID, description, model tier, neutral role body, write/network/spawn boundary, and effective tool permissions. Platform syntax differences SHALL NOT weaken a neutral policy. Root router and portable skill validation SHALL account for their intentional sharing by Codex and OpenCode.

#### Scenario: OpenCode permission exceeds the neutral policy
- **WHEN** a generated OpenCode subagent permits editing, network access, external-directory access, or nested task invocation beyond its neutral definition
- **THEN** parity validation fails and reports the agent, permission, and neutral policy mismatch

#### Scenario: All three adapters are equivalent
- **WHEN** every platform-specific representation preserves the same neutral agent contracts and resolved tier mappings
- **THEN** parity validation passes despite TOML, Claude Markdown, and OpenCode Markdown syntax differences
