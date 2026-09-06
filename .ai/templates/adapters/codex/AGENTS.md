# AI Development Forge — Project Router

<!-- Generated from .ai/framework and .ai/custom. Do not edit directly. -->

## Authority and context

The main session is the strong orchestrator: it owns user communication, routing, gates and canonical writes. Subagents report to it, never spawn agents or change lifecycle state. Use the documentation language in `.ai/project.yaml`; control instructions and IDs stay English.

Bootstrap: read `.ai/BOOTSTRAP.md`. Staged upgrade: read `.ai-next/MIGRATE.md`. Otherwise run `python .ai/tools/forge.py context` and read `BACKLOG.md`. Consume all inventory pages, then the selected plan, current TASK and relevant Git diff. Load planned workspace bodies only for concrete dependency/eligibility questions. Use `section` for relevant SPEC/ARCHITECTURE/ADR/INV excerpts.

Canonical owners: SPEC = behavior; ARCHITECTURE = architecture; BACKLOG = Epic priority/readiness/status, dependencies and defects; ADR = decision; plan = Task order and Epic evidence; TASK = Task state/evidence; INV = research. Git supplies actual changes. History, caches and external systems are not authoritative. Report contradictions; do not silently reconcile them.

## Python automation

Use `.ai/tools/forge.py` for context, sections, fingerprints, validation, adapters, checks, external roles, budgets and metrics. Read only the relevant `.ai/tools/USAGE.md` section; execute helpers without loading their source. If Python/dependencies are unavailable, report that limitation and use manual workflows; do not install implicitly.

Do not invoke a model for enumeration, hashing, metadata extraction, rendering, approved command execution or successful-command summaries. Invoke context-collector only for unresolved interpretation. Pass agents exact relevant paths/excerpts, scope and fingerprints; never truncate required contracts to meet a token budget.

Opt-in check reuse needs approved complete inputs, unchanged commands/runtime/environment and intact passing evidence. It never replaces independent test-integrity judgment, review, current fast assurance, RED evidence or fresh Epic Validation. Inspect material warnings/failure logs. Persist compact evidence in TASK/plan; disposable `.ai/local/` artifacts have no canonical authority.

## Lifecycle and Git Gates

Require explicit approval for SPEC, ARCHITECTURE, BACKLOG, plans, ADR acceptance, Epic Start, Replan, Task Start, Task Acceptance and Epic Acceptance. Enums/transitions come from `.ai/framework/contracts.yaml`. Prior explicit authorization remains valid within scope; do not ask twice. A bounded Task Start grant must match `task-start-check` and ordinary dependencies/blockers/eligibility; it grants no acceptance, commit, Replan or Epic Start.

Plan Approval leaves an approved workspace in `execution/planned/` and Epic PLANNED. Epic Start separately moves one eligible workspace to active and updates Backlog as one recoverable operation. Run no more than one code-writing Task at a time. Task Acceptance never starts the next Task without explicit authorization for both decisions. Do not activate the next Epic automatically.

Never commit before explicit Task Acceptance and DONE. Under `manual`, require separate scoped commit authorization; under `auto_commit_after_acceptance`, commit only the accepted Task. Preserve unrelated changes. Task checks are focused/affected/scoped; full regression/global checks belong to Epic Validation, followed by applicable fuzzing and Epic Acceptance.

## Common Engineering Prohibitions

TASK delivery track is independent from model tier and risk level. `fast` retains implementer plus orchestrator assurance and invokes neither reviewer nor tester; `standard` retains independent reviewer and tester. Uncertainty selects standard; fast eligibility failure escalates monotonically; standard never downgrades after Task Start. Both retain Task Acceptance and Epic Validation/fuzzing.

- Stay within approved scope; resolve material product/architecture decisions explicitly. Preserve unrelated code, formatting and user work.
- Derive test expectations independently from contracts/invariants; assertions must fail for plausible wrong implementations. Never use captured production output or duplicated production algorithms as oracles, mock the subject under test, or substitute private call structure for behavior.
- Trace acceptance/risk to normal, boundary, invalid-input, failure/recovery, state-transition and side-effect evidence. Classify changed tests/fixtures/snapshots; fix production code instead of adapting tests when the contract is unchanged. Weaker assertions, removed cases, skips, broader tolerances or increased mocking require disposition. No rerun-until-green.
- Claim passed/clean/complete only with current reproducible evidence. Never hide failures, material warnings or missing coverage. Bound process time/output/retries.
- Protect secrets and personal data. Production/network/external/destructive actions need applicable explicit scope. Preserve compatibility and require migration/backup/rollback for destructive data/schema changes. For ML/data, prevent leakage and preserve reproducibility, uncertainty and artifact lineage.
- Change neutral sources/overlays and synchronize; never hand-edit generated adapters.

## Skills and roles

Explicitly invoke the matching bundled skill using platform-native syntax. When delegating, name the skill and role. External process skills do not add Forge lifecycle gates, artifacts, routing or Git actions.

- Bootstrap: `forge-bootstrap-new`, `forge-bootstrap-existing`.
- Intake and priority: `forge-intake-feature`, `forge-intake-bug`, `forge-intake-external-work`, `forge-reprioritize-backlog`.
- Execution: `forge-prepare-epic`, `forge-resume-development`, `forge-run-task`, `forge-complete-task`, `forge-complete-epic`.
- Diagnostics: `forge-investigate`, `forge-security-audit`, `forge-mutation-test`.
- Maintenance: `forge-migrate-framework`, `forge-check-framework`, `forge-sync-adapters`.

Resolve model tiers from `.ai/project.yaml` and boundaries from the selected neutral role contract. Never silently change mappings. Planner/reviewer provide independent semantic judgment; implementer writes code; tester checks integrity/coverage; epic-validator checks aggregate assurance. Research/fuzzing/security specialists run only when applicable. `mutation-runner` runs metrics; `mutation-analyzer` requires separate authorization and current candidates. Independent read-only research may run in parallel.

`forge-investigate` invokes no generated subagent. Canonical `INV-NNNN` outcomes: `no_action`, `promoted`, `fixed_directly`, `unresolved`. Direct fixes require explicit authorization, proportionate checks and a path-level ledger; they imply neither acceptance nor commit permission.

## Planner and reviewer execution mode

Resolve `role_execution.mode` first. Prefer `python .ai/tools/forge.py role --orchestrator <active> --role <role> --prompt-file <path>` for external routes. It runs one bounded preflight internally; separate `--preflight` is diagnostic only. Legacy .mjs launchers remain compatible.

`claude_with_codex` requires Claude, fresh ephemeral read-only `codex exec` and pinned `gpt-5.6-sol/medium`; never copy wrappers into user directories, create `BASH_ENV` or manipulate broker/app-server state. `codex_with_claude` requires Codex, Claude Code 2.1.203+, configured strong model/effort, fresh non-persistent plan mode and restricted tools. Supply the complete neutral contract and exact assignment through stdin, using a secure temporary prompt file and removing it afterwards.

`native_subagents` uses the active Codex, Claude Code, or OpenCode platform's matching generated agent with no external preflight; Claude native agents use high effort. An OpenCode-led setup proposes this existing mode only without a prior approved route, and records it only after approval. There is no fallback: invalid configuration, active-orchestrator mismatch or runtime mismatch, timeout, permission failure, malformed output or packet-integrity failure blocks the stage. The orchestrator validates semantic output and owns transitions.

## Ownership

`AGENTS.md` is the shared complete router; `CLAUDE.md` contains exactly `@AGENTS.md`. OpenCode uses `.opencode/agents/` and shared `.agents/skills/`; do not generate `opencode.json` or duplicate `.opencode/skills/`. Project router additions belong in `.ai/custom/router-shared.md`.

Generate only manifest-managed entries; preserve unlisted agents/skills, settings, hooks, MCP and project data. Forge generates no hooks or MCP configuration. Optional `.ai/integrations/`: Registration alone grants no tool authority; compatible consumers use only allowed operations. Optional `quality/mutation-testing/` is metrics-only by default and never alters lifecycle. Create no synthetic INV/mutation records during bootstrap/sync/migration and no separate review/testing report Markdown files.

{{ custom.router_shared }}
