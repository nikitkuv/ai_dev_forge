---
name: forge-sync-adapters
description: Regenerate and verify both Codex CLI and Claude Code adapters from neutral Forge agents, portable skills, project model mappings, and custom overlays. Use after bootstrap, configuration changes, framework migration, or detected adapter drift.
---

# Synchronize Platform Adapters

## Build the render input

1. Read `.ai/project.yaml`, `.ai/framework/manifest.yaml`, neutral agent files, all fourteen portable skills, adapter templates, `.ai/custom/`, existing generated outputs, and adapter hashes in `.ai/framework.lock`.
2. Require both Codex and Claude platforms to be enabled.
3. Resolve every `strong`, `balanced`, and `fast` mapping:
   - Codex requires concrete `model` and `reasoning_effort`;
   - Claude requires a concrete `model`.
4. Accept provider aliases or full model IDs, but never invent, silently downgrade, or silently upgrade a model.
5. Detect manual edits and collisions in root routers, agent files, and copied skills.

## Preview collisions

Show the regeneration diff before overwriting manually changed generated outputs. Preserve project-specific additions only through `.ai/custom/`. Request explicit user confirmation for any collision.

Do not treat generated adapters as project-owned canonical files and do not modify canonical product or execution documents.

## Render both platforms

Generate as one synchronized operation:

- root `AGENTS.md` and `CLAUDE.md`;
- seven `.codex/agents/*.toml` files with concrete Codex model and reasoning effort;
- seven `.claude/agents/*.md` files with concrete Claude model and tool restrictions;
- fourteen `.agents/skills/*/SKILL.md` copies;
- fourteen `.claude/skills/*/SKILL.md` copies;
- approved custom router or adapter overlays.

Create no framework hooks or MCP configuration.

## Validate and finalize

1. verify both routers are no more than 150 lines;
2. verify all role IDs, tiers, permissions, descriptions, and instructions have cross-platform parity;
3. verify skill names, descriptions, and bodies are identical across native skill directories;
4. verify no unresolved model or template placeholder remains;
5. verify generated paths contain no unapproved manual content;
6. run the framework conformance check.

If either platform fails, restore both adapter sets to their prior state. Update adapter source and output hashes in `.ai/framework.lock` only after both pass. Create no sync report file and require no framework CLI.
