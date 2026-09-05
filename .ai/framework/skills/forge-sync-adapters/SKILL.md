---
name: forge-sync-adapters
description: Use after bootstrap, framework upgrade, model mapping changes, custom overlay changes, or detected drift in local Codex, Claude, or OpenCode adapters.
---

# Synchronize Platform Adapters

## Build the render input

1. Read `.ai/project.yaml`, the manifest, framework investigation, integration and mutation-testing contracts, neutral agents, portable skills, the full `AGENTS.md` router template, the importing `CLAUDE.md` template, `.ai/custom/router-shared.md`, existing local adapters, and lock hashes. Do not use project-owned `.ai/integrations/` definitions/state as render input. Do not use project-owned `investigations/` or `quality/mutation-testing/` history as render input.
2. Require Codex and Claude plus one explicit OpenCode enabled flag. Resolve Codex and Claude tiers from bundled defaults or explicit overrides. When OpenCode is enabled, require every tier to be an explicit non-empty `provider/model-id` from user input or evidenced local `opencode models` output; never invent, install, authenticate, or silently change a provider, model, or effort.
3. Require one valid project `role_execution.mode` and derive managed membership from manifest `subagents`, `skills`, `role_execution`, root `AGENTS.md`, `CLAUDE.md`, and enabled OpenCode agents. The unchanged three modes and two external launchers supplement rather than replace native `epic-planner` and `reviewer` agents. For an OpenCode-led setup with no prior approved route, propose existing `native_subagents` by default, require approval before recording it, and preserve an existing approved route.
4. Inventory unlisted agents, skills, `.codex/config.toml`, Claude settings, `opencode.json`, `.opencode/commands/`, `.opencode/plugins/`, `.opencode/skills/`, unlisted `.opencode/agents/`, hooks, project-owned investigations and integration consumers, independent mutation history, and adjacent platform files as project-owned content.
5. Detect manual edits and same-ID collisions in managed entries.

## Preview collisions

Show the complete regeneration diff before replacing a manually changed root router or managed entry. Request explicit confirmation for each same-ID collision.

Preserve project router content only through the shared overlay:

```text
.ai/custom/router-shared.md
```

If `.ai/custom/codex-router.md` or `.ai/custom/claude-router.md` exists, stop and require explicit migration/reconciliation into the shared overlay before rendering. Never ignore or silently delete a legacy project-owned overlay; platform-specific root router content is incompatible with the identical-router invariant.

Preserve every unlisted adapter entry in place. Do not modify canonical product or execution documents.

## Render local adapters

Stage one synchronized candidate containing:

- full root `AGENTS.md` from its template plus the shared overlay, and root `CLAUDE.md` containing exactly `@AGENTS.md`;
- manifest-declared Codex agents under `.codex/agents/`;
- manifest-declared Codex skills under `.agents/skills/`;
- manifest-declared Claude agents under `.claude/agents/`;
- manifest-declared Claude skills under `.claude/skills/`;
- when enabled, manifest-declared OpenCode agents under `.opencode/agents/`, reusing root `AGENTS.md` and `.agents/skills/` rather than duplicating either;
- `.claude/forge/codex-role-runner.mjs` copied verbatim from the Claude adapter template;
- `.codex/forge/claude-role-runner.mjs` copied verbatim from the Codex adapter template;
- all preserved unlisted project-owned entries.

Write each generated `.claude/agents/*.md` and `.opencode/agents/*.md` file as UTF-8 without BOM. Its first bytes must be the opening YAML frontmatter delimiter `---`; do not emit the UTF-8 BOM byte sequence `EF BB BF`, because the platform then fails to recognize the frontmatter and does not register the subagent.

Install no global agent or skill. Generate no hook, MCP configuration, platform settings, commands, or framework CLI dependency.
Generate no `.ai/integrations/` or `quality/mutation-testing/` content. Generate no `investigations/` content. Embed no project-local INV IDs, integration IDs, mutation records, provider names, scopes, bindings, or credentials. Generic investigation, profile/consumer, and mutation routing comes only from framework-owned sources.

## Validate and finalize

1. verify `AGENTS.md` has no unresolved placeholder and remains within the configured line limit, and verify `CLAUDE.md` is the exact `@AGENTS.md` import;
2. verify the complete manifest-declared Forge agent and skill set on Codex and Claude, plus every agent on enabled OpenCode and shared OpenCode skill discovery from `.agents/skills/`;
3. verify managed IDs, tiers, effective permissions, descriptions, instructions, models, applicable effort, and skill bodies have cross-platform parity; verify OpenCode allows edits only for implementer, grants command/research access only where neutral policy permits, and denies external-directory and nested task access for every subagent; verify both delivery-track routes are present in the shared router and portable skills, fast invokes neither reviewer nor tester, standard preserves both roles, and delivery track never changes model mappings; verify `forge-investigate` is portable, main-agent-owned, and invokes no generated subagent; verify all three unchanged `role_execution` modes, both launchers, OpenCode's default proposal of existing `native_subagents`, active-orchestrator requirements, complete neutral prompt parity, fresh/read-only boundaries, configured model sources, and `fallback: forbidden`;
4. verify additional project-owned agents, skills, `investigations/`, integration consumers, `quality/mutation-testing/` history, and all unlisted platform files are unchanged;
5. verify every generated `.claude/agents/*.md` and `.opencode/agents/*.md` file is UTF-8 without BOM and begins at byte zero with `---`;
6. verify the framework lock contains only inputs that render managed outputs and that local integration changes are reported separately rather than as adapter drift;
7. run the read-only framework conformance check.

If any enabled platform fails, replace none. Back up every affected managed path before replacement and restore all adapter sets on failure. Update managed source/output hashes and preserved-path ownership in `.ai/framework.lock` only after success, including only manifest-declared OpenCode agent entries. Create no sync report file.
