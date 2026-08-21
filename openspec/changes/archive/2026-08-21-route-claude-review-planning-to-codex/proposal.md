## Why

Claude Code currently performs Epic planning and independent Task review through generated Claude subagents, so the strongest planning and review gates are tied to Claude's native agent runtime. Routing those two read-only stages to Codex gives Claude Code projects the same `gpt-5.6-sol`/`high` reasoning baseline used by the Codex adapter while preserving Forge's existing role contracts and orchestration gates.

## What Changes

- Add a Claude-specific Codex delegation path backed by the `openai/codex-plugin-cc` runtime and the locally authenticated Codex CLI.
- Prefer a fresh, synchronous, read-only Codex task for `epic-planner` work from `forge-prepare-epic` and `reviewer` work from `forge-run-task` when the active platform is Claude Code.
- Pass the existing neutral `epic-planner` or `reviewer` assignment unchanged as the task contract, including the exact Epic evidence or Review Packet supplied by the orchestrator.
- Pin both calls to model `gpt-5.6-sol` with reasoning effort `high`; project Claude model-tier overrides do not alter these two Codex-backed stages.
- Fall back to the current native Claude `epic-planner` or `reviewer` subagent when preflight cannot establish an available plugin runtime and its required Node.js, Codex CLI, or authentication prerequisites.
- Treat failures or invalid output after a Codex task has started as blocking errors rather than silently rerunning the assignment with Claude.
- Keep native Codex behavior and all other Claude agents unchanged, and keep lifecycle transitions, approvals, result validation, and remediation routing owned by the orchestrator.
- Keep generated native Claude `epic-planner` and `reviewer` agent files as the deterministic fallback path, so the plugin remains an optional enhancement rather than a mandatory runtime dependency.

## Capabilities

### New Capabilities

- `claude-codex-role-routing`: Defines how Claude Code prefers direct Codex delegation for Epic planning and Task review through `codex-plugin-cc`, including runtime selection, prompt parity, read-only execution, native-subagent fallback, failure handling, and adapter generation.

### Modified Capabilities

None.

## Impact

- Neutral orchestration skills: `.ai/framework/skills/forge-prepare-epic/SKILL.md` and `.ai/framework/skills/forge-run-task/SKILL.md`.
- Claude adapter generation and validation: `.ai/05-create-platform-adapters.md`, `.ai/framework/skills/forge-sync-adapters/SKILL.md`, `.ai/06-final-validation.md`, the manifest, and Claude/root router templates.
- Framework guidance and examples that currently describe both roles as Claude subagents, including `README.md`, `FRAMEWORK.md`, `RUNBOOK.md`, migration/bootstrap material, and scenarios.
- Optional external runtime path: `openai/codex-plugin-cc`, Node.js 18.18+, a global Codex CLI recognized by the plugin, and a valid local Codex login.
- The Codex adapter, canonical neutral role definitions, and generated Claude fallback agents remain available; Claude only changes its preferred execution mechanism for the two roles when preflight succeeds.
