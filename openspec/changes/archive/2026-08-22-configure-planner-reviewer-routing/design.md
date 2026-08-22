## Context

Forge renders the same neutral roles into both Codex and Claude native agents. Release 4.2 additionally routes Claude-originated `epic-planner` and `reviewer` assignments through `codex-plugin-cc` when available and otherwise falls back to the native Claude agents. The provider choice is not project configuration, and there is no reciprocal Codex-to-Claude route.

Claude Code provides an official non-interactive CLI surface: `claude -p`, JSON output, explicit model and effort selection, `--permission-mode plan`, tool restriction, and non-persistent sessions. This is sufficient for a managed transport without a separate plugin. Plan mode is explicitly designed to research and run exploratory commands without editing source; the launcher must also remove editing, agent, connector, and browser surfaces and must never enable bypass permissions.

## Goals / Non-Goals

**Goals:**

- Give the user one explicit project-level choice for how both strong read-only roles execute.
- Support symmetric external delegation from Claude to Codex and from Codex to Claude.
- Preserve native subagents as a first-class selected mode rather than an implicit fallback.
- Keep role instructions, assignment evidence, lifecycle ownership, and result validation provider-neutral.
- Fail deterministically when selected prerequisites or the expected orchestrator are unavailable.

**Non-Goals:**

- Configuring the two roles independently.
- Routing implementer, tester, validator, fuzzer, security, research, or context roles across providers.
- Installing, updating, authenticating, or silently selecting Codex/Claude tooling.
- Resuming external sessions, enabling write mode, nested agents, network tools, plugins, MCP, Chrome, or automatic provider fallback.
- Changing model-tier mappings for native subagents.

## Decisions

### 1. Use one required execution-mode enum

Add the following project-owned configuration:

```yaml
role_execution:
  mode: claude_with_codex
```

Valid values are `claude_with_codex`, `codex_with_claude`, and `native_subagents`. The choice applies atomically to both `epic-planner` and `reviewer`; partial, per-role, or unknown values are invalid. Both platform adapters continue to be generated, but the two cross-provider modes also declare the expected active orchestrator. Reaching either role from the other orchestrator blocks with a configuration-mismatch diagnostic instead of inventing a route.

The template leaves the value unresolved until bootstrap obtains explicit approval. Migration offers `claude_with_codex` for existing 4.2 projects because it preserves their effective preferred route, but it does not silently write that value. Until migration resolves the field, only workflows that need these two roles are blocked.

### 2. Make provider selection explicit and remove fallback

The orchestrator reads `role_execution.mode` immediately before each planning or review assignment:

- `claude_with_codex`: Claude runs the existing managed Codex launcher.
- `codex_with_claude`: Codex runs the new managed Claude launcher.
- `native_subagents`: the active platform invokes its generated native role agent directly and performs no external-runtime preflight.

An unavailable selected external runtime blocks before task creation with exact missing-prerequisite diagnostics. A started external runtime failure, timeout, malformed result, or runtime mismatch also blocks. Neither case switches provider automatically. Changing modes requires an explicit user-approved `.ai/project.yaml` update and adapter synchronization; it does not retry the already failed attempt.

### 3. Add a Codex-side headless Claude launcher

Add a framework-owned launcher template rendered as `.codex/forge/claude-role-runner.mjs`. It discovers an installed Claude Code executable without installing it, verifies a supported version and authentication through non-mutating preflight, accepts the role and prompt through argument-safe file/stdin handling, and starts a fresh foreground process equivalent to:

```text
claude -p --output-format json --model <configured-claude-strong-model> --effort <configured-claude-strong-effort> --permission-mode plan --no-session-persistence ...
```

The launcher restricts built-in tools to the neutral role's read-oriented tool set, explicitly removes edit/write/notebook, Agent/Task/team, web/Chrome, and MCP surfaces, never passes bypass/accept-edits/auto modes, and does not load a fallback model. It preserves read-only Bash diagnostics permitted by the role contract; commands rejected by plan mode in headless execution become explicit blocked diagnostics rather than permission broadening. It captures stdout, stderr, exit status, effective model/effort/mode metadata, and a start boundary so preflight unavailability and post-start failure remain distinguishable.

The launcher uses a temporary prompt file only when required for platform-safe multiline input, removes it in all exit paths, never persists the Claude session, and does not treat process success as role-contract success.

### 4. Preserve neutral contracts and orchestrator ownership

Both external launchers receive the complete current `.ai/framework/agents/<role>.yaml` instructions followed by the same current assignment that a native subagent receives. Reviewer input remains the exact fingerprint-bound Review Packet. The calling orchestrator validates packet integrity, required output sections, runtime metadata, and role outcome before any transition. External providers never contact the user, write canonical state, approve work, route remediation, or spawn agents.

### 5. Render both transports and all native agents

The manifest describes the three modes and both external routes. Adapter generation always retains all nine native agents on both platforms and both launcher templates, independent of the selected mode or local prerequisite availability. Project configuration selects the runtime path; generation does not install, authenticate, or invoke either external provider.

Root routers remain byte-identical and describe the mode matrix. Validation checks configuration validity, route/role parity, launcher safety flags, native inventories, and preservation of unrelated platform settings. The project configuration hash remains a framework-lock render input because changing the mode changes generated operational guidance.

## Risks / Trade-offs

- [Claude Code CLI behavior changes across versions] -> Centralize invocation, require a tested minimum version, statically validate supported flags, and report upgrade guidance on incompatibility.
- [Claude plan mode is a permission boundary rather than Codex's filesystem sandbox] -> Combine plan mode with a narrow tool surface and explicit deny rules, prohibit bypass-capable startup, and fail when a required diagnostic is not permitted instead of widening authority.
- [Headless authentication diagnostics may vary by installation type] -> Keep preflight non-mutating, distinguish executable/version/auth failures, and provide manual setup instructions without parsing credentials.
- [A project is opened in an orchestrator that conflicts with its cross-provider mode] -> Block only planner/reviewer invocation and report the configured mode and required orchestrator.
- [Removing automatic fallback reduces availability] -> Make native execution an explicit, dependency-free mode and explain mode changes; never override the user's provider selection for convenience.
- [Large Review Packets exceed command-line limits] -> Use stdin or secure temporary files and argument arrays, never concatenated shell commands.
- [The two roles may eventually need different providers] -> Keep the schema deliberately atomic for this request; a future version can add per-role overrides through an explicit schema migration.

## Migration Plan

1. Increment the framework and project configuration schema versions and add the unresolved `role_execution.mode` template field plus enum validation.
2. During bootstrap require one of the three choices. During migration show the current effective behavior and offer `claude_with_codex` as the compatibility-preserving value, then write only the approved selection.
3. Add bidirectional route metadata and the managed Codex-side Claude launcher while retaining the existing Claude-side Codex launcher and every native agent.
4. Update workflow skills, routers, generation/sync/validation, lock handling, documentation, and scenarios around the explicit mode matrix.
5. Regenerate adapters atomically after mode approval and verify that only the selected path is invoked at runtime.
6. Roll back by restoring the prior framework files, adapters, and lock together; preserve the project-owned mode value for forward recovery or remove it only with explicit approval when returning to a schema that cannot represent it.

## Open Questions

- The exact minimum Claude Code version should be selected during implementation from the oldest version that supports every launcher flag used by the final command and covered by contract tests.
