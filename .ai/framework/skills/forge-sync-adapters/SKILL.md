---
name: forge-sync-adapters
description: Use after bootstrap, framework upgrade, model mapping changes, custom overlay changes, or detected drift in local Codex and Claude adapters.
---

# Synchronize Platform Adapters

## Build the render input

1. Read `.ai/project.yaml`, the manifest, neutral agents, portable skills, renderer templates, structured `.ai/custom/` overlays, existing local adapters, and lock hashes.
2. Require both platforms and resolve every configured model tier. Never invent or silently change a model or reasoning effort.
3. Derive managed membership only from the manifest `subagents` and `skills` IDs plus root `AGENTS.md` and `CLAUDE.md`.
4. Inventory unlisted agents, skills, `.codex/config.toml`, Claude settings, commands, hooks, and adjacent platform files as project-owned content.
5. Detect manual edits and same-ID collisions in managed entries.

## Preview collisions

Show the complete regeneration diff before replacing a manually changed root router or managed entry. Request explicit confirmation for each same-ID collision.

Preserve project router content only through:

```text
.ai/custom/router-shared.md
.ai/custom/codex-router.md
.ai/custom/claude-router.md
```

Preserve every unlisted adapter entry in place. Do not modify canonical product or execution documents.

## Render local adapters

Stage one synchronized candidate containing:

- root `AGENTS.md` and `CLAUDE.md` from current templates plus structured overlays;
- manifest-declared Codex agents under `.codex/agents/`;
- manifest-declared Codex skills under `.agents/skills/`;
- manifest-declared Claude agents under `.claude/agents/`;
- manifest-declared Claude skills under `.claude/skills/`;
- all preserved unlisted project-owned entries.

Install no global agent or skill. Generate no hook, MCP configuration, platform settings, commands, or framework CLI dependency.

## Validate and finalize

1. verify both routers have no unresolved placeholder and remain within the configured line limit;
2. verify the complete manifest-declared Forge agent and skill set on both platforms;
3. verify managed IDs, tiers, permissions, descriptions, instructions, models, reasoning effort, and skill bodies have cross-platform parity;
4. verify additional project-owned agents and skills and all unlisted platform files are unchanged;
5. run the read-only framework conformance check.

If either platform fails, replace neither. Back up every affected managed path before replacement and restore both adapter sets on failure. Update managed source/output hashes and preserved-path ownership in `.ai/framework.lock` only after success. Create no sync report file.
