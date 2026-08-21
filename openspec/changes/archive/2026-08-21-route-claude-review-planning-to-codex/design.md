## Context

See `proposal.md` for motivation and `specs/claude-codex-role-routing/spec.md` for behavior. Forge currently keeps one neutral YAML definition per role, renders every role as both a Codex and Claude agent, and requires cross-platform file parity. The portable `forge-prepare-epic` and `forge-run-task` skills invoke `epic-planner` and `reviewer` by role name.

The referenced plugin exposes a `codex-companion.mjs task` runtime that wraps the local Codex app server and accepts `--model` and `--effort`; omitting `--write` produces the required read-only task. Its public `/codex:rescue` command is not used for the preferred path because that command intentionally launches a thin Claude subagent before calling the runtime. The plugin requires Node.js 18.18+ and a locally installed and authenticated Codex CLI. Existing native Claude `epic-planner` and `reviewer` agents remain the fallback when preflight cannot establish those prerequisites.

## Goals / Non-Goals

**Goals:**

- Make the execution provider for a neutral role platform-specific without duplicating or weakening the role contract.
- Provide a deterministic, inspectable Claude-to-Codex command path with a clearly bounded native Claude fallback when that path is unavailable before execution.
- Preserve all existing Forge lifecycle gates and adapter collision/rollback guarantees.

**Non-Goals:**

- Moving implementation, testing, Epic validation, fuzzing, security audit, or research roles to Codex when Claude is the orchestrator.
- Enabling the plugin's optional stop-review gate, background jobs, thread resume, write mode, or automatic remediation.
- Changing native Codex adapter model mappings or allowing project tier overrides for these two Claude-originated calls.

## Decisions

### 1. Model role routing explicitly in the manifest

Add a Claude preferred-route map for `epic-planner` and `reviewer` with provider `codex-plugin-cc`, model `gpt-5.6-sol`, effort `high`, fresh-thread, foreground, read-only properties, and native-agent fallback IDs. Keep both IDs in the neutral role inventory because their YAML instructions remain the source of truth and both Codex and Claude native agents still render normally.

This is preferable to deleting or conditionally generating the neutral/native agents: keeping them preserves the current implementation as a complete fallback without duplicating contracts in workflow skills.

### 2. Call the plugin runtime directly through a generated Claude launcher

Add a small framework-owned launcher template rendered into the managed Claude adapter. The launcher resolves the enabled `codex@openai-codex` installation from Claude Code's configured plugin cache (respecting `CLAUDE_CODE_PLUGIN_CACHE_DIR` when set), verifies a single usable plugin root and the expected companion script, then invokes:

```text
node <plugin-root>/scripts/codex-companion.mjs task --fresh --model gpt-5.6-sol --effort high <prompt>
```

It deliberately omits `--write`, `--background`, and resume flags. Prompt content is supplied without shell interpolation (stdin or an argument-array-safe temporary file) to preserve Review Packets containing quotes and newlines. The launcher returns stdout, stderr, exit code, and enough runtime metadata for the orchestrator to verify the effective route. Temporary prompt material must be removed after the process finishes and must never be committed or treated as canonical evidence.

Direct use of the plugin runtime is chosen over `/codex:rescue`, because the slash command routes through `codex:codex-rescue`, and over bare `codex exec`, because the requested integration is specifically the plugin's shared runtime and app-server lifecycle. The plugin script is an internal surface, so the launcher centralizes discovery and compatibility checks instead of scattering cache paths across skills.

### 3. Compose prompts from the neutral source at invocation time

The Claude orchestrator reads the selected `.ai/framework/agents/<role>.yaml`, extracts its complete `instructions`, and constructs a prompt with two explicit blocks: immutable role contract and current assignment. Planner assignment construction continues to follow `forge-prepare-epic`; reviewer assignment construction continues to use the exact Review Packet built by `forge-run-task`. No generated Claude agent Markdown is involved.

The runner starts a fresh task for every planning proposal and every review revision. A remediation revision gets a new reviewer run and cannot resume the prior thread, preventing stale conversational state from contaminating fingerprint-bound evidence.

### 4. Select fallback only at the preflight boundary

The launcher is transport only. Before creating a Codex task, preflight classifies the integration as available or unavailable. Unavailable includes a missing or disabled plugin runtime, unsupported Node.js, missing Codex CLI, or missing Codex authentication. In that state the orchestrator invokes the matching generated Claude subagent, supplies the identical assignment, validates its output through the existing contract, and reports the fallback reason.

Once Codex task creation begins, provider selection is final for that attempt. A non-zero exit, timeout, malformed response, or model/effort mismatch blocks the stage and does not trigger Claude fallback. This prevents an actual Codex failure from being hidden and prevents evidence for one planning/review attempt from being silently mixed across providers.

The main Claude session remains responsible for all state transitions. Process success is necessary but insufficient: missing required sections, a mismatched Review Packet/fingerprint, or claimed settings that do not match the requested route are stage failures.

### 5. Preserve native adapter parity and add route metadata

Codex and Claude continue to render all nine native agents. Claude additionally renders the launcher and preferred-route configuration for the two selected roles. Validation retains existing native agent parity checks and adds verification that the Codex prompt reuses the same neutral instructions and that fallback points to the matching Claude agent ID. Root routers remain byte-identical by describing conditional platform routing.

Because no native agent is removed, existing lock ownership and same-ID collision behavior remain unchanged. Plugin absence does not make adapter generation fail: the generated preferred route is dormant until runtime preflight succeeds.

## Risks / Trade-offs

- [The plugin companion script is an internal rather than stable public CLI surface] → Pin/document a tested minimum plugin version, isolate invocation in one launcher, validate its command contract during adapter generation, and fail with an upgrade/setup instruction when incompatible.
- [Claude plugin cache layout differs by OS, scope, or cache override] → Resolve from Claude's plugin metadata/cache root rather than hard-coding a home path; test Windows and POSIX path handling and reject ambiguous matches.
- [Large role prompts or Review Packets can break quoting or command limits] → Pass content through stdin or an argument-array-safe temporary file, never through a concatenated shell command.
- [Read-only Codex still creates plugin job/session state outside the repository] → Treat plugin state as runtime metadata, prohibit source/canonical writes, and document the distinction.
- [Fallback can make environments use different providers] → Report the selected provider and fallback reason for every selected stage while preserving identical role input and validation.
- [A transient preflight failure can select Claude even though Codex might recover] → Make one deterministic preflight decision per attempt; do not retry or switch providers after execution begins.
- [Plugin installation or authentication is machine-local] → Add explicit optional setup guidance; never auto-install or authenticate without user action.
- [Root-router identity becomes semantically more complex] → Keep byte-identical router text, retain native agent parity, and validate the additional platform-aware route metadata separately.

## Migration Plan

1. Increment the framework version for the optional Claude-to-Codex routing capability and document the plugin/Node/Codex prerequisites for enabling the preferred path.
2. Update neutral workflow instructions, manifest route metadata, Claude generation rules, launcher template, router guidance, lock semantics, and validation rules.
3. Atomically regenerate both adapters with all existing native agents plus the Claude launcher and route metadata; plugin absence does not block generation.
4. Update `.ai/framework.lock` only after nine-agent parity, two preferred-route checks, prompt parity, fallback mapping, and launcher static compatibility all pass.
5. Verify runtime preflight when the plugin is available and verify native fallback when it is absent or unauthenticated.
6. Roll back by restoring the prior adapter sets and lock; native Claude execution remains available throughout and no canonical project or execution data requires migration.
