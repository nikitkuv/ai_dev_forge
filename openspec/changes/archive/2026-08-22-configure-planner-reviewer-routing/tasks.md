## 1. Configuration and route model

- [x] 1.1 Increment framework and project schema versions; add required `role_execution.mode` with exactly `claude_with_codex`, `codex_with_claude`, and `native_subagents`, applying atomically to `epic-planner` and `reviewer`; add valid/invalid configuration fixtures and verify unrelated workflows remain available when the field is unresolved.
- [x] 1.2 Replace the one-way preferred-route manifest contract with bidirectional external route metadata plus native mode while retaining all nine neutral/native agents for both platforms; verify model, permission, fallback-prohibition, and expected-orchestrator metadata.
- [x] 1.3 Update bootstrap to explain the three modes, require explicit selection, and persist it in `.ai/project.yaml`; verify no external runtime is installed, authenticated, or invoked during configuration.

## 2. Codex-to-Claude launcher

- [x] 2.1 Add the managed Codex adapter launcher for headless Claude Code using fresh `claude -p` structured output, configured Claude strong model/effort, plan permission mode, non-persistent sessions, safe multiline prompt transport, and no fallback model or session resume.
- [x] 2.2 Enforce the launcher's read-only and no-spawn surface by restricting tools, denying edit/write/notebook, Agent/Task/team, browser/web, plugin, and MCP capabilities, and prohibiting bypass/accept-edits/auto permission modes; verify runtime metadata exposes the effective restrictions.
- [x] 2.3 Add preflight and process tests for Windows/POSIX executable resolution, supported/unsupported versions, missing authentication, quoted and large prompts, timeouts, malformed JSON, permission denial, non-zero exits, temporary-file cleanup, and preflight-versus-started failure classification.

## 3. Workflow provider selection

- [x] 3.1 Update `forge-prepare-epic` and workspace preparation to select the configured route, validate the active orchestrator, preserve the complete neutral planner contract/evidence, and reject all implicit provider fallback while keeping Plan Approval and Epic Start unchanged.
- [x] 3.2 Update `forge-run-task` to select the configured route, validate the active orchestrator, preserve the exact fingerprint-bound Review Packet, and reject all implicit provider fallback while keeping remediation and testing gates unchanged.
- [x] 3.3 Add route-matrix contract tests covering both roles across all three modes, both active orchestrators, missing/invalid configuration, unavailable preflight, successful results, malformed output, actionable findings, and post-start failures.

## 4. Adapter generation and migration

- [x] 4.1 Update adapter generation to render both launchers and all native agents regardless of mode or prerequisite availability; verify both adapter sets are staged/replaced atomically and unrelated platform files are preserved.
- [x] 4.2 Update sync, conformance, root-router parity, and framework-lock validation for the selected mode, route metadata, launcher safety flags, complete role prompt parity, and absence of implicit fallback.
- [x] 4.3 Update migration to request explicit mode selection, offer `claude_with_codex` only as the compatibility-preserving suggestion for existing 4.2 behavior, preview configuration/adapter diffs, and roll back configuration, adapters, and lock together on failure.

## 5. Documentation and verification

- [x] 5.1 Update `README.md`, `FRAMEWORK.md`, `RUNBOOK.md`, bootstrap/migration guidance, and scenarios with the three-mode matrix, prerequisites, active-orchestrator mismatch, no-fallback semantics, mode switching, and rollback.
- [x] 5.2 Add sanitized end-to-end fixtures for Claude-to-Codex, Codex-to-Claude, native Codex, and native Claude execution; verify contract/result parity and lifecycle gates across providers without live-provider claims in automated evidence.
- [x] 5.3 Run all repository framework/documentation tests and strict OpenSpec validation; record live Codex plugin and Claude Code CLI smoke checks as environment-specific manual verification when prerequisites are available.
