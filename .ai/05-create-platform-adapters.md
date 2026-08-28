# Bootstrap Step 05 — Create Platform Adapters

## Purpose

Finalize project configuration, ensure a concise operational README, and create deterministic native adapters for both Codex CLI and Claude Code CLI from the same neutral framework sources.

This step generates derived platform files. It does not change canonical product, architecture, Backlog, ADR, plan, TASK, source code, hooks, or MCP configuration.

## Inputs

Read:

- `.ai/framework/manifest.yaml` and `.ai/framework/contracts.yaml`;
- eleven `.ai/framework/agents/*.yaml` definitions;
- sixteen `.ai/framework/skills/*/SKILL.md` sources;
- `.ai/templates/project.yaml`;
- `.ai/templates/README.md`;
- Codex and Claude adapter templates under `.ai/templates/adapters/`;
- the Claude-side Codex launcher `.ai/templates/adapters/claude/codex-role-runner.mjs` and Codex-side Claude launcher `.ai/templates/adapters/codex/claude-role-runner.mjs`;
- `.ai/custom/router-shared.md` when present;
- existing `.ai/project.yaml`, `.ai/framework.lock`, and generated adapters when present.

Optional `.ai/integrations/` and `quality/mutation-testing/` content is project-owned state, not a render input. Do not create, read for tool discovery, invoke, or embed local definitions or mutation history while generating adapters.

Stop if source counts, IDs, or framework versions disagree.

## Resolve Project Configuration

Create or update `.ai/project.yaml` from its template while preserving project-owned values.

Require:

- both `platforms.codex.enabled` and `platforms.claude.enabled` to be `true`;
- `role_execution.mode` to be exactly `claude_with_codex`, `codex_with_claude`, or `native_subagents`, explicitly approved for both selected roles;
- `documentation_language` to match the user's communication language;
- `framework_language: en`;
- an explicit Git policy;
- resolved model mappings for every tier, using the bundled defaults unless the project explicitly overrides them.
- quality profiles approved in the Epic plan and reusable Task/Epic command catalogs derived only from confirmed repository, build-system, and CI evidence. Keep an unresolved list empty and report the blocker; never invent a command.
- optional mutation-testing backend, version, baseline, mutation and result-adapter commands only when separately approved and evidenced. Preserve a null/absent configuration as valid; do not install a backend or create mutation history.

Model mappings must provide:

```yaml
models:
  codex:
    strong: {model: gpt-5.6-sol, reasoning_effort: medium}
    balanced: {model: gpt-5.6-terra, reasoning_effort: medium}
    fast: {model: gpt-5.6-luna, reasoning_effort: medium}
  claude:
    strong: {model: opus, effort: medium}
    balanced: {model: sonnet, effort: medium}
    fast: {model: haiku, effort: medium}
```

These are framework defaults, not unresolved placeholders. Accept provider aliases or full model IDs as explicit project overrides. Never invent an override, leave a mapping unresolved, or silently upgrade or downgrade a tier. Warn if the main orchestrator session is not suitable for tier `strong`, but do not change that session.

## Detect Collisions

Before rendering:

1. compare existing generated files with hashes in `.ai/framework.lock`;
2. derive the managed agent and skill IDs from the manifest;
3. detect manual changes in root routers and manifest-declared Forge entries;
4. preserve unlisted agents, skills, and adjacent platform files as project-owned content;
5. distinguish generated drift from approved `.ai/custom/` overlays;
6. show the exact regeneration diff;
7. request explicit user confirmation before overwriting a same-ID collision.

Do not overwrite unrelated project files. Stage both adapter sets in a temporary location or memory so a partial render never replaces only one platform.

## Render Codex

Generate:

```text
AGENTS.md
.codex/agents/context-collector.toml
.codex/agents/documentation-researcher.toml
.codex/agents/epic-planner.toml
.codex/agents/implementer.toml
.codex/agents/reviewer.toml
.codex/agents/tester.toml
.codex/agents/epic-validator.toml
.codex/agents/fuzzer.toml
.codex/agents/security-auditor.toml
.codex/agents/mutation-runner.toml
.codex/agents/mutation-analyzer.toml
.codex/forge/claude-role-runner.mjs
.agents/skills/<sixteen-skill-ids>/SKILL.md
```

Render the single root router from `.ai/templates/adapters/codex/AGENTS.md` plus the shared overlay. Do not copy legacy framework sections into the overlay.

The rendered router must include the complete Common Engineering Prohibitions section from the neutral `AGENTS.md` template.

For each neutral agent, render `.ai/templates/adapters/codex/agent.toml` with:

- its `id`, English description, permissions, and English instructions;
- the concrete Codex model for its tier;
- the configured `model_reasoning_effort`;
- the neutral `codex_sandbox_mode`.

Copy all sixteen portable `SKILL.md` files verbatim into `.agents/skills/`.
Copy the Codex-side Claude launcher template verbatim to `.codex/forge/claude-role-runner.mjs`.

## Render Claude Code

Generate:

```text
CLAUDE.md
.claude/agents/context-collector.md
.claude/agents/documentation-researcher.md
.claude/agents/epic-planner.md
.claude/agents/implementer.md
.claude/agents/reviewer.md
.claude/agents/tester.md
.claude/agents/epic-validator.md
.claude/agents/fuzzer.md
.claude/agents/security-auditor.md
.claude/agents/mutation-runner.md
.claude/agents/mutation-analyzer.md
.claude/forge/codex-role-runner.mjs
.claude/skills/<sixteen-skill-ids>/SKILL.md
```

Render `CLAUDE.md` exactly from `.ai/templates/adapters/claude/CLAUDE.md`. It must contain only `@AGENTS.md`; do not render the shared overlay or router instructions into it.

For each neutral agent, render `.ai/templates/adapters/claude/agent.md` with:

- native YAML frontmatter;
- its `id`, English description, concrete Claude model and effort, and allowed tools;
- `effort: high` for every generated Claude agent when `role_execution.mode` is `native_subagents`; in the other modes, preserve the configured Claude tier effort so the native-only override does not change the managed `codex_with_claude` route;
- the same English role contract used by the Codex adapter.
- Write every `.claude/agents/*.md` file as UTF-8 **without BOM**. Byte zero must be the first `-` of the opening `---` frontmatter delimiter; never prepend `EF BB BF`.

Copy all sixteen portable `SKILL.md` files verbatim into `.claude/skills/`.

Copy the Claude-side Codex launcher template verbatim to `.claude/forge/codex-role-runner.mjs`. Preserve every one of the eleven generated agents on both platforms, including `epic-planner`, `reviewer`, `mutation-runner`, and `mutation-analyzer`, because `native_subagents` is a first-class mode. Render the complete neutral reviewer contract unchanged on both platforms, including its production-only blocking findings, separate advisory non-production observations, and production-fingerprint review-reuse rules. Generate both launchers regardless of the selected mode or local prerequisite availability. Do not preflight, install, authenticate, or invoke either external runtime or a mutation backend while generating adapters.

## Validate Before Replacement

Verify the staged outputs:

- `AGENTS.md` contains no unresolved placeholder and is no more than 150 lines;
- `CLAUDE.md` contains exactly `@AGENTS.md`, so Claude Code imports the complete `AGENTS.md` router without duplication;
- the imported router contains the complete Common Engineering Prohibitions without project-specific weakening;
- each platform contains every agent and skill ID declared by the manifest;
- `role_execution.mode` is valid and applies to both selected roles; both managed launchers and all three manifest routes exist; the Codex route pins fresh read-only `gpt-5.6-sol/medium`, the Claude route uses fresh non-persistent plan mode with restricted tools and the configured Claude strong mapping, native mode performs no external preflight, and every route forbids fallback;
- additional project-owned agents and skills remain present and are excluded from Forge parity counts;
- IDs, descriptions, tiers, role instructions, write/network/spawn boundaries, and skill bodies have cross-platform parity;
- every rendered agent contains its concrete model and effort; when `role_execution.mode` is `native_subagents`, every Claude agent has `effort: high` while Codex agents retain their configured tier effort;
- every generated `.claude/agents/*.md` file is UTF-8 without BOM and begins at byte zero with `---`;
- generated files contain English control text;
- `.ai/custom/router-shared.md` appears once in `AGENTS.md` and is not duplicated in `CLAUDE.md`;
- `.codex/config.toml`, Claude settings, commands, hooks, and all other unlisted platform files are unchanged;
- no hook or MCP file was generated.
- no `.ai/integrations/` file or project-local provider/tool name was generated or embedded;
- no `quality/mutation-testing/` record was generated or embedded.

If either platform fails, replace neither. After both pass, replace both adapter sets as one logical operation and restore the previous sets if replacement validation fails.

## Write the Framework Lock

Only after successful replacement, create or update `.ai/framework.lock` with:

- lock schema version;
- framework name and version;
- hash algorithm;
- hashes of the manifest, framework contracts including generic integration profile contracts, project configuration, neutral agents, portable skills, renderer templates, and custom overlays;
- managed generated file paths, IDs, and per-file hashes for both platforms;
- preserved unlisted adapter paths without claiming their content as Forge-owned;
- generation timestamp;
- ownership categories needed to detect later collisions and obsolete files.

The lock is project-owned state; migration must not replace it with a release template.

Do not hash `.ai/integrations/` definitions or state into managed-output provenance: they do not render managed adapters. Validate their schema and references separately as project state, so changing a local board, knowledge source, dataset, or analysis service is not reported as framework drift.

Do not hash `quality/mutation-testing/` registry, run records, or retained artifacts into managed-output provenance. They are independent project-owned history, do not render adapters, and must survive synchronization and migration unchanged.

## Ensure the Project README

Treat root `README.md` as project-owned, non-canonical operational orientation.

- If it is absent, create it from `.ai/templates/README.md` in the project documentation language.
- Fill setup, run, and test commands only from confirmed repository evidence; never invent commands.
- Link `SPEC.md`, `ARCHITECTURE.md`, `BACKLOG.md`, `DECISIONS.md`, `AGENTS.md`, and `CLAUDE.md` without copying their content.
- If a README already exists, preserve it. Show a minimal diff and request explicit confirmation before adding missing operational links.
- Leave no template placeholder in the completed README.

## Completion Gate

Report concrete model mappings, created paths, collision decisions, parity checks, router line counts, and lock update. Request explicit user approval before Step 06. Do not create reports, commit, or proceed automatically.
