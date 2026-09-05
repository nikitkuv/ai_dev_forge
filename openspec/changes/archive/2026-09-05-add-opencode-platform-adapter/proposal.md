## Why

AI Development Forge currently generates native adapters only for Codex CLI and Claude Code CLI. OpenCode can read the generated root `AGENTS.md` and portable `.agents/skills/*/SKILL.md` files, but it cannot discover the Forge subagents because they are emitted only in Codex TOML and Claude Markdown formats. As a result, opening a Forge-managed project in OpenCode provides partial instructions but not the orchestrated planner, implementer, reviewer, tester, validation, fuzzing, security, and mutation workflows.

## What Changes

- Add OpenCode as a third supported platform and generated adapter target.
- Reuse the single generated root `AGENTS.md` as OpenCode's native project router and reuse `.agents/skills/` through OpenCode's documented agent-compatible skill discovery.
- Generate all manifest-declared Forge subagents as native `.opencode/agents/*.md` files with `mode: subagent`, explicit provider-qualified model mappings, and permissions derived from each neutral role boundary.
- Extend project configuration, bootstrap, synchronization, migration, lock ownership, parity validation, and final validation to cover Codex, Claude Code, and OpenCode atomically.
- Make the existing `native_subagents` value the default proposed planner/reviewer route when OpenCode is the selected operating platform, without adding any new route mode; preserve the active-orchestrator restrictions and no-fallback behavior of the two cross-runtime routes.
- Preserve project-owned `opencode.json`, OpenCode commands, plugins, MCP, provider credentials, and other unlisted `.opencode/` content.
- Update maintained documentation, scenarios, framework versioning, and automated contract coverage for the third platform.

## Capabilities

### New Capabilities

- `opencode-platform-adapter`: Defines native OpenCode routing, subagent generation, model and permission mapping, ownership, migration, and cross-platform parity requirements.

### Modified Capabilities

None.

## Impact

- Affects the framework manifest and version, project configuration template, platform-adapter templates, bootstrap and migration workflows, generated-output ownership and lock data, maintained user documentation, scenarios, and contract tests.
- Adds `.opencode/agents/*.md` as Forge-managed generated files while continuing to share `AGENTS.md` and `.agents/skills/` across platforms.
- Requires a project enabling OpenCode to select three provider-qualified OpenCode model IDs; Forge does not install OpenCode, configure providers, authenticate accounts, or select paid services.
- Keeps the existing `role_execution.mode` enum unchanged. Bootstrap or migration proposes `native_subagents` by default for an OpenCode-led workflow but still records an explicit approved value and preserves an already approved project choice until the user changes it.
- Does not generate `opencode.json`, duplicate skills into `.opencode/skills/`, add OpenCode command aliases, or change product and execution lifecycle semantics.
