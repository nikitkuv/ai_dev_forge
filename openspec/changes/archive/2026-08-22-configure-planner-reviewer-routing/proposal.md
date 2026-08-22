## Why

Forge currently hard-codes one asymmetric route: Claude Code prefers Codex for `epic-planner` and `reviewer`, then falls back to native Claude subagents when the plugin is unavailable, while Codex always uses native Codex subagents. Projects need an explicit, durable choice of which orchestrator runs the workflow and whether those two independent read-only roles run on the other provider or inside the active platform.

## What Changes

- Add one project-owned `role_execution.mode` setting that applies together to `epic-planner` and `reviewer`.
- Support exactly three modes:
  - `claude_with_codex`: run the workflow in Claude Code and execute both roles through the existing `openai/codex-plugin-cc` route.
  - `codex_with_claude`: run the workflow in Codex CLI and execute both roles through a managed fresh headless Claude Code CLI process.
  - `native_subagents`: run both roles as native internal subagents of whichever supported orchestrator is active.
- Require bootstrap and migration to obtain and persist an explicit user choice. Existing projects are offered `claude_with_codex` as the compatibility-preserving migration value but it is not written without approval.
- Treat a mismatch between the active orchestrator and either cross-provider mode as a configuration error at the selected role stage.
- Remove implicit cross-provider fallback. If the explicitly selected external provider is unavailable before execution, block the stage with setup diagnostics; if a started external run fails, continue to fail closed.
- Add a managed Codex-side Claude launcher using Claude Code's supported non-interactive `claude -p` interface, structured output, a fresh non-persistent session, the configured Claude strong model, plan-mode permissions, restricted tools, and no nested agents.
- Preserve the complete neutral role contract, exact assignment evidence, orchestrator-owned gates, result validation, and native agent generation on both platforms.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `claude-codex-role-routing`: Generalize the current Claude-to-Codex preference into explicit bidirectional or native role-execution modes for Epic planning and Task review.

## Impact

- Project configuration template and schema expectations in `.ai/project.yaml`.
- Bootstrap, migration, adapter generation/synchronization, final validation, and framework-lock inputs.
- `forge-prepare-epic` and `forge-run-task` provider selection and diagnostics.
- Manifest route metadata, both byte-identical root routers, the existing Claude-side Codex launcher, and a new Codex-side Claude launcher.
- Contract and launcher tests, migration fixtures, documentation, and development scenarios.
- Optional external prerequisites: `openai/codex-plugin-cc` plus Codex CLI for `claude_with_codex`; installed and authenticated Claude Code CLI for `codex_with_claude`; neither for `native_subagents`.
