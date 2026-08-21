## 1. Runtime route and launcher

- [x] 1.1 Increment the framework version for the optional routing capability and add manifest metadata for the two preferred Claude `codex-plugin-cc` routes with matching native fallback IDs; verify the manifest still declares and renders all nine neutral agents for both platforms.
- [x] 1.2 Add the framework-owned Claude launcher template that discovers the enabled `codex@openai-codex` plugin, checks Node/Codex/auth prerequisites, accepts multiline prompt input safely, and invokes a fresh foreground task with `--model gpt-5.6-sol --effort high` and no write/resume/background flag; verify its reported command metadata and exit propagation with a fake companion runtime.
- [x] 1.3 Add launcher/preflight tests for Windows/POSIX cache paths, `CLAUDE_CODE_PLUGIN_CACHE_DIR`, missing/disabled/ambiguous/incompatible plugin installs, unavailable Node/Codex/auth prerequisites, multiline and quoted prompts, non-zero exits, and absence of write/resume/background flags; verify unavailable preflight is distinguishable from failure after task start and the complete test command passes.

## 2. Workflow routing and contract preservation

- [x] 2.1 Update `forge-prepare-epic` so Claude reads the complete neutral `epic-planner` contract, combines it with the existing planning assignment, prefers the generated Codex launcher after successful preflight, and otherwise invokes the existing native Claude planner with identical input; verify provider selection is reported and Plan Approval, Epic Start, result validation, and native Codex routing remain unchanged.
- [x] 2.2 Update `forge-run-task` so Claude sends the complete neutral `reviewer` contract and exact fingerprint-bound Review Packet through a fresh launcher call after successful preflight, or through the existing native Claude reviewer when preflight is unavailable; verify provider selection is reported, no post-start Codex failure triggers fallback, and the remediation/testing loop remains unchanged.
- [x] 2.3 Audit the two neutral agent definitions and shared contracts for assumptions about native Claude invocation, changing only wording needed for transport-neutral prompt execution; verify planner/reviewer instructions remain single-source and retain read-only, network, spawn, output, and orchestrator-only boundaries.

## 3. Adapter generation, synchronization, and validation

- [x] 3.1 Update bootstrap adapter generation to retain all nine Codex agents and all nine native Claude agents while adding the Claude launcher and two preferred external routes; verify atomic staging, collision handling, and existing planner/reviewer agent generation remain intact even when the plugin is absent.
- [x] 3.2 Update `forge-sync-adapters`, lock ownership rules, and final conformance checks to retain native cross-platform parity and additionally validate route prompt parity and fallback IDs; verify routers remain byte-identical and unrelated Claude commands/hooks/settings are preserved.
- [x] 3.3 Update both root-router templates with the conditional Claude-to-Codex routing, preflight fallback boundary, and post-start fail-closed behavior; verify the templates remain byte-identical, within the line limit, and do not direct the preferred path through `/codex:rescue`.

## 4. Migration and user guidance

- [x] 4.1 Update bootstrap and migration guidance with optional `openai/codex-plugin-cc` installation, `/codex:setup`, Node.js 18.18+, Codex authentication, minimum tested plugin compatibility, native fallback behavior, adapter regeneration, and rollback; verify no step auto-installs, authenticates, enables the optional review gate, or treats plugin absence as a bootstrap failure.
- [x] 4.2 Reconcile `README.md`, `FRAMEWORK.md`, `RUNBOOK.md`, and affected scenarios so they consistently describe Codex-backed Epic planning and Task review as Claude's preferred path with native Claude fallback, while native Codex and all other roles remain unchanged; verify a repository-wide search finds no contradictory routing or failure instructions.

## 5. End-to-end verification

- [x] 5.1 Exercise fixture Claude adapter generation/synchronization and simulate available and unavailable preflight, successful planner output, clean review, actionable findings, malformed output, and failed started runtime; verify unavailable preflight invokes the matching native subagent, post-start failures do not, and lifecycle gates advance only for valid outputs.
- [x] 5.2 Run the repository's applicable framework/documentation validation plus `openspec validate route-claude-review-planning-to-codex --strict`; verify all checks pass and record any environment-only live Codex invocation as an explicit manual verification rather than fabricated automated evidence.
