---
name: forge-sync-adapters
description: Use after bootstrap, framework upgrade, model mapping changes, custom overlay changes, or detected drift in local Codex and Claude adapters.
---

# Synchronize Platform Adapters

## Build the render input

1. Read `.ai/project.yaml`, the manifest, framework integration and mutation-testing contracts, neutral agents, portable skills, the full `AGENTS.md` router template, the importing `CLAUDE.md` template, `.ai/custom/router-shared.md`, existing local adapters, and lock hashes. Do not use project-owned `.ai/integrations/` definitions/state as render input. Do not use `quality/mutation-testing/` history as render input.
2. Require both platforms and resolve every configured model tier from the bundled defaults or explicit project overrides. Never invent or silently change a model or effort.
3. Require one valid project `role_execution.mode` and derive managed membership from manifest `subagents`, `skills`, `role_execution`, root `AGENTS.md`, and `CLAUDE.md`. The three modes and two external launchers supplement rather than replace native `epic-planner` and `reviewer` agents on either platform.
4. Inventory unlisted agents, skills, `.codex/config.toml`, Claude settings, commands, hooks, project-owned integration consumers, independent mutation history, and adjacent platform files as project-owned content.
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
- `.claude/forge/codex-role-runner.mjs` copied verbatim from the Claude adapter template;
- `.codex/forge/claude-role-runner.mjs` copied verbatim from the Codex adapter template;
- all preserved unlisted project-owned entries.

Write each generated `.claude/agents/*.md` file as UTF-8 without BOM. Its first bytes must be the opening YAML frontmatter delimiter `---`; do not emit the UTF-8 BOM byte sequence `EF BB BF`, because Claude Code then fails to recognize the frontmatter and does not register the subagent.

Install no global agent or skill. Generate no hook, MCP configuration, platform settings, commands, or framework CLI dependency.
Generate no `.ai/integrations/` or `quality/mutation-testing/` content and embed no project-local integration IDs, mutation records, provider names, scopes, bindings, or credentials. Generic profile/consumer and mutation routing comes only from framework-owned sources.

## Validate and finalize

1. verify `AGENTS.md` has no unresolved placeholder and remains within the configured line limit, and verify `CLAUDE.md` is the exact `@AGENTS.md` import;
2. verify the complete manifest-declared Forge agent and skill set on both platforms;
3. verify managed IDs, tiers, permissions, descriptions, instructions, models, effort, and skill bodies have cross-platform parity; verify all three `role_execution` modes, both launchers, active-orchestrator requirements, complete neutral prompt parity, fresh/read-only boundaries, configured model sources, and `fallback: forbidden`;
4. verify additional project-owned agents, skills, integration consumers, `quality/mutation-testing/` history, and all unlisted platform files are unchanged;
5. verify every generated `.claude/agents/*.md` file is UTF-8 without BOM and begins at byte zero with `---`;
6. verify the framework lock contains only inputs that render managed outputs and that local integration changes are reported separately rather than as adapter drift;
7. run the read-only framework conformance check.

If either platform fails, replace neither. Back up every affected managed path before replacement and restore both adapter sets on failure. Update managed source/output hashes and preserved-path ownership in `.ai/framework.lock` only after success. Create no sync report file.
