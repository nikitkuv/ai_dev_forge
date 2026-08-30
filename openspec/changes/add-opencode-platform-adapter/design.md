## Context

Forge is a documentation-first framework bundle rather than an executable CLI. Its neutral contracts live under `.ai/framework/`, and bootstrap or adapter synchronization renders platform-native router, subagent, and skill files. Today the manifest declares only `codex` and `claude`, Step 05 stages those two outputs atomically, and validation requires parity between them.

OpenCode already supports two Forge outputs without conversion: it loads a project-root `AGENTS.md` as project instructions and discovers `.agents/skills/<name>/SKILL.md` while walking the Git worktree. Its native project subagents, however, are Markdown files under `.opencode/agents/` with YAML frontmatter. OpenCode model identifiers use `provider/model-id`, and agent capabilities are controlled by `permission` rules rather than the Codex sandbox or Claude tool-list formats.

The design is based on the OpenCode documentation for [rules](https://opencode.ai/docs/rules/), [agents](https://opencode.ai/docs/agents/), [agent skills](https://opencode.ai/docs/skills/), [permissions](https://opencode.ai/docs/permissions/), and [configuration](https://opencode.ai/docs/config/), retrieved 2026-08-30.

## Goals / Non-Goals

**Goals:**

- Make a bootstrapped or migrated Forge project usable as a full orchestrated project in OpenCode.
- Preserve one neutral role contract and behavioral parity across all three platform adapters.
- Reuse OpenCode-compatible shared outputs instead of creating redundant copies.
- Keep provider selection and credentials project-owned while requiring deterministic model resolution before generation.
- Preserve atomic generation, drift detection, collision handling, and recovery guarantees with a third adapter set.

**Non-Goals:**

- Install, update, authenticate, or configure the OpenCode runtime or any model provider.
- Generate or modify `opencode.json`, commands, plugins, hooks, MCP servers, provider policies, or credentials.
- Add an OpenCode-specific lifecycle, weaken user approval gates, or change neutral agent responsibilities.
- Make `claude_with_codex` or `codex_with_claude` silently usable from an OpenCode orchestrator.
- Duplicate portable skills into `.opencode/skills/` or create a second OpenCode-only root router.

## Decisions

### Reuse `AGENTS.md` as the only complete router

OpenCode natively reads root `AGENTS.md`, so Forge will keep `AGENTS.md` as the single complete generated router shared by Codex and OpenCode. `CLAUDE.md` remains the Claude Code compatibility import containing only `@AGENTS.md`. The router language will describe all three platform boundaries and mappings without creating `OPENCODE.md` or copying the router into `.opencode/`.

This preserves the existing single-source rule and avoids three router documents drifting independently.

### Reuse `.agents/skills/` without an OpenCode copy

OpenCode's documented skill discovery includes project-local `.agents/skills/*/SKILL.md`. Forge will therefore keep one portable skill copy in `.agents/skills/` for Codex and OpenCode, plus the existing `.claude/skills/` copy required for Claude Code. Adapter generation and validation will prove that every manifest skill is discoverable by OpenCode through `.agents/skills/`; `.opencode/skills/` remains project-owned and ungenerated.

### Render native OpenCode subagents

Add `.ai/templates/adapters/opencode/agent.md` and render one `.opencode/agents/<id>.md` for every neutral subagent. Each file will:

- start at byte zero with UTF-8-without-BOM YAML frontmatter;
- set `description`, `mode: subagent`, and an explicit model from `models.opencode[agent.model_tier].model`;
- express tool boundaries with OpenCode `permission` keys;
- contain the same English role instructions used by the Codex and Claude adapters.

The renderer will derive permissions deterministically from neutral policies and validate the effective boundary. Read/search/list operations are allowed to every role. `edit` is allowed only to the implementer and denied to read-only or runtime-artifact-only roles. `bash` is allowed only when the neutral role has command-execution capability. `webfetch` and `websearch` are allowed only for the documentation researcher and remain subject to its assigned-research contract. `task` is denied to every generated subagent so subagents cannot coordinate or spawn other agents. `external_directory` is denied by default. The generated permissions are an enforcement layer in addition to, not a replacement for, the complete neutral role instructions.

### Require explicit provider-qualified OpenCode models

Extend `.ai/project.yaml` with `platforms.opencode.enabled` and three `models.opencode` tiers. Every enabled OpenCode tier must resolve to a non-empty `provider/model-id` accepted by the user's configured OpenCode installation. Bootstrap and migration ask the user to choose from locally evidenced output such as `opencode models` or from a provider/model value the user supplies; they never invent a provider, install one, or store credentials.

No universal bundled OpenCode model default is declared because available providers and model catalogs are user-specific. Optional provider-specific model options are out of scope for the initial adapter; tier differences are represented by the selected model IDs. Generation blocks only the OpenCode adapter stage when OpenCode is enabled and a mapping is unresolved or malformed.

### Default OpenCode to the existing `native_subagents` route

The existing `native_subagents` mode already means that the active platform invokes its matching generated agents without an external preflight. OpenCode becomes a valid active platform for this route. No OpenCode-specific mode or additional enum value will be introduced. The generated root router will name the OpenCode tier mapping and native agent location.

When bootstrap or migration is configuring an OpenCode-led workflow and no prior approved route exists, it will propose `native_subagents` as the default for both `epic-planner` and `reviewer`. The normal Forge approval gate still records the selected value explicitly in `.ai/project.yaml`; runtime behavior will not depend on an unrecorded implicit fallback. Migration will preserve an already approved route until the user explicitly changes it.

The cross-runtime modes keep their current orchestrator constraints: `claude_with_codex` requires Claude Code and `codex_with_claude` requires Codex. Selecting either while OpenCode is the active orchestrator blocks only planner/reviewer execution and never falls back to OpenCode native agents. Users who operate Forge primarily through OpenCode select `native_subagents`.

### Extend atomic ownership and parity to three platforms

The manifest will add `opencode` to `adapters`, `.opencode/agents/` to managed generated membership, and `opencode.json`, `.opencode/commands/`, `.opencode/plugins/`, `.opencode/skills/`, plus unlisted `.opencode/agents/` entries to protected or project-owned membership as appropriate.

Step 05 and adapter synchronization will stage and validate all enabled generated outputs before replacing any of them. A failure in one enabled adapter replaces none. `.ai/framework.lock` will record hashes and ownership for managed OpenCode agent files and preserved unlisted OpenCode paths. Migration will classify collisions against prior lock evidence, preserve project-owned OpenCode files, remove only obsolete Forge-managed outputs, and roll back all adapter sets together on validation failure.

Parity checks compare IDs, descriptions, tiers, role bodies, write/network/spawn boundaries, and effective permissions across Codex, Claude, and OpenCode. Platform-specific syntax may differ, but no adapter may weaken the neutral contract.

### Validate with contract tests rather than a live provider

Repository tests will parse generated OpenCode Markdown frontmatter, verify all eleven agent IDs and tier mappings, check UTF-8/BOM rules, assert permission boundaries for representative roles, ensure router and skill reuse, and enforce protected-file and atomic-generation language. Tests will also cover unresolved or malformed OpenCode models, disabled-platform behavior during migration, native routing, no fallback, and preservation of project-owned `.opencode/` content.

The release validation does not require a live OpenCode provider or network call. When an `opencode` executable is locally available, a read-only discovery or syntax check may be reported as supplementary evidence but is not allowed to install, authenticate, or contact a provider.

## Risks / Trade-offs

- OpenCode providers expose different model IDs and provider-specific reasoning options. -> Require explicit provider-qualified IDs and avoid pretending one default works everywhere; keep provider-specific options for a future scoped change.
- OpenCode permissions do not encode all dynamic TASK path restrictions. -> Combine conservative static permissions with unchanged neutral role instructions and deny nested task invocation; validate that only the implementer receives edit permission.
- Sharing `.agents/skills/` means OpenCode support depends on a documented compatibility location. -> Contract-test the declared path and keep the official documentation reference in maintained framework guidance.
- A third adapter increases migration and collision surface. -> Extend lock ownership and stage all enabled sets atomically, preserving unlisted `.opencode/` content.
- Users may select a cross-runtime route while running OpenCode. -> Propose `native_subagents` by default for OpenCode-led setup, preserve explicit approval and existing choices, and make any remaining orchestrator mismatch an explicit stage blocker with no fallback.

## Migration Plan

1. Increment the framework minor version and add the OpenCode adapter declaration, template, configuration schema, and ownership rules.
2. Update bootstrap and migration to ask whether OpenCode is enabled, propose the existing `native_subagents` mode by default for an OpenCode-led workflow when no approved route exists, and resolve all three provider-qualified model tiers before rendering.
3. Stage Codex, Claude, and enabled OpenCode outputs; detect same-ID collisions and require the existing explicit overwrite confirmation.
4. Validate router reuse, skill discovery, agent parity, model mappings, permissions, UTF-8 format, protected files, and no generated hooks/MCP/provider configuration.
5. Replace all staged adapter sets as one logical operation and update `.ai/framework.lock`; restore the previous sets if replacement validation fails.
6. Update maintained documentation and regression tests, then run the full repository test suite and strict OpenSpec validation when the CLI is available.

Rollback restores the prior framework bundle, project configuration, lock, and all adapter outputs together. It removes only OpenCode files proven by the prior lock to be Forge-managed and preserves project-owned `.opencode/` content.
