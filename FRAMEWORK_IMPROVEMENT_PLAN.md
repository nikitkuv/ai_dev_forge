# AI Development Forge v3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Перестроить documentation-only framework в соответствии с утверждённым `FRAMEWORK_DESIGN.md`: dual-platform bootstrap для Codex CLI и Claude Code CLI, единые canonical documents, управляемые lifecycle, семь субагентов и portable skills без обязательного CLI, hooks, MCP или Superpowers.

**Architecture:** `.ai/` остаётся копируемым framework bundle. Нейтральные contracts, agent definitions и skills являются источниками для одновременной генерации нативных Codex- и Claude-adapters. Канонические документы создаются в корне целевого проекта, а runtime state хранится только в BACKLOG, plan и TASK.

**Tech Stack:** Markdown, YAML, TOML, Git, нативные форматы Codex CLI и Claude Code CLI. В первой версии нет framework executable и package dependencies.

## Global Constraints

- Утверждённый дизайн: `FRAMEWORK_DESIGN.md`.
- Framework control files и templates должны быть написаны на английском.
- Генерируемые canonical documents используют язык общения пользователя.
- `AGENTS.md` и `CLAUDE.md` не должны превышать 150 строк.
- Bootstrap всегда создаёт оба platform adapters.
- Core workflow обязан работать без Superpowers.
- Framework не создаёт hooks и MCP configuration.
- Никаких отдельных report, progress, checkpoint или validation Markdown-файлов.
- TASK status хранится только в соответствующем TASK-файле.
- Epic status и priority хранятся только в BACKLOG.
- Git policy для выполнения этого плана — `manual`: каждый commit только после пользовательского подтверждения.
- Перед каждой следующей задачей плана требуется отдельный Start gate.
- Не изменять `.venv/`, `venv/`, `build/`, `dist/` и другие untracked artifacts пользователя.
- Не запускать bootstrap внутри репозитория `ai_dev_forge` и не создавать здесь root `SPEC.md`, `ARCHITECTURE.md`, `BACKLOG.md`, `DECISIONS.md`, `decisions/`, `execution/`, `AGENTS.md`, `CLAUDE.md`, `.codex/`, `.claude/` или `.agents/`.
- В этом репозитории изменяются только framework source bundle `.ai/`, framework documentation и утверждённые design/plan files; generated project artifacts проверяются только в disposable test repositories.

---

## File Map

### Existing files to rewrite

```text
FRAMEWORK.md
README.md
RUNBOOK.md
.ai/BOOTSTRAP.md
.ai/CONVENTIONS.md
.ai/01-product-discovery.md
.ai/02-system-design.md
.ai/03-release-planning.md
.ai/04-prepare-workspace.md
.ai/06-final-validation.md
.ai/templates/README.md
.ai/templates/SPEC.md
.ai/templates/ARCHITECTURE.md
.ai/templates/BACKLOG.md
.ai/templates/DECISIONS.md
.ai/templates/ADR.md
.ai/templates/plan.md
.ai/templates/TASK.md
```

### Legacy files to remove

```text
.ai/05-create-ai-environment.md
.ai/templates/CLAUDE.md
.ai/templates/agents/agent.md
.ai/templates/agents/documentation.md
.ai/templates/agents/fuzzing.md
.ai/templates/agents/implementation.md
.ai/templates/agents/review.md
.ai/templates/agents/validation.md
```

### New framework contracts and configuration templates

```text
.ai/framework/manifest.yaml
.ai/framework/contracts.yaml
.ai/templates/project.yaml
```

### New neutral agent definitions

```text
.ai/framework/agents/context-collector.yaml
.ai/framework/agents/documentation-researcher.yaml
.ai/framework/agents/implementer.yaml
.ai/framework/agents/reviewer.yaml
.ai/framework/agents/tester.yaml
.ai/framework/agents/fuzzer.yaml
.ai/framework/agents/security-auditor.yaml
```

### New platform render templates

```text
.ai/templates/adapters/codex/AGENTS.md
.ai/templates/adapters/codex/agent.toml
.ai/templates/adapters/claude/CLAUDE.md
.ai/templates/adapters/claude/agent.md
```

### New portable skill sources

```text
.ai/framework/skills/forge-bootstrap-new/SKILL.md
.ai/framework/skills/forge-bootstrap-existing/SKILL.md
.ai/framework/skills/forge-intake-feature/SKILL.md
.ai/framework/skills/forge-intake-bug/SKILL.md
.ai/framework/skills/forge-reprioritize-backlog/SKILL.md
.ai/framework/skills/forge-prepare-epic/SKILL.md
.ai/framework/skills/forge-resume-development/SKILL.md
.ai/framework/skills/forge-run-task/SKILL.md
.ai/framework/skills/forge-complete-task/SKILL.md
.ai/framework/skills/forge-complete-epic/SKILL.md
.ai/framework/skills/forge-migrate-framework/SKILL.md
.ai/framework/skills/forge-security-audit/SKILL.md
.ai/framework/skills/forge-check-framework/SKILL.md
.ai/framework/skills/forge-sync-adapters/SKILL.md
```

### Renamed bootstrap step

```text
.ai/05-create-platform-adapters.md
```

---

### Task 1: Define framework ownership and lifecycle contracts

**Files:**

- Create: `.ai/framework/manifest.yaml`
- Create: `.ai/framework/contracts.yaml`
- Create: `.ai/templates/project.yaml`
- Modify: `.ai/CONVENTIONS.md`

**Interfaces:**

- Consumes: approved lifecycle and ownership rules from `FRAMEWORK_DESIGN.md`.
- Produces: one structured contract used by bootstrap, adapters, skills, validation and migration.

- [ ] **Step 1: Verify the contract files do not yet exist**

```powershell
@(
  '.ai/framework/manifest.yaml',
  '.ai/framework/contracts.yaml',
  '.ai/templates/project.yaml'
) | ForEach-Object { '{0}: {1}' -f $_, (Test-Path -LiteralPath $_) }
```

Expected: all three paths report `False`.

- [ ] **Step 2: Create the release manifest**

Write `.ai/framework/manifest.yaml` with:

- framework name `ai-dev-forge`;
- version `3.0.0`;
- schema version `1`;
- both adapters `codex` and `claude`;
- explicit framework-owned paths;
- explicit project-owned paths;
- the fourteen skill IDs;
- the seven subagent IDs;
- `hooks: false`, `mcp: false`, `cli: false`.

- [ ] **Step 3: Create the lifecycle contract**

Write `.ai/framework/contracts.yaml` with exact enums:

```yaml
epic_readiness: [OUTLINE, READY]
epic_status:
  [PLANNED, ACTIVE, FUZZING, "AWAITING EPIC ACCEPTANCE", COMPLETED, PAUSED, CANCELLED]
task_status:
  [TODO, "IN PROGRESS", "IN REVIEW", "IN TESTING", "AWAITING USER ACCEPTANCE", DONE, PAUSED, CANCELLED]
bug_status: [OPEN, SCHEDULED, RESOLVED, REJECTED, DUPLICATE, WONT_FIX]
adr_status: [PROPOSED, ACCEPTED, REJECTED, SUPERSEDED, DEPRECATED]
model_tiers: [strong, balanced, fast]
```

Also encode allowed transitions, the two separate Task gates, Epic Start/Acceptance gates, Replan gate, ADR Approval gate and mandatory fuzzing outcomes.

- [ ] **Step 4: Create the generated project configuration template**

Write `.ai/templates/project.yaml` with both platforms enabled, unset concrete model values, `documentation_language: null`, `framework_language: en`, `integrations.superpowers.enabled: false`, and `git.policy: manual`.

- [ ] **Step 5: Rewrite conventions as a human-readable companion**

Make `.ai/CONVENTIONS.md` reference `contracts.yaml` for enums instead of maintaining a second status list. Retain naming, global ID allocation, paths, language rules, generated-file policy and one-source-of-truth rules.

- [ ] **Step 6: Validate contract coverage**

```powershell
Select-String -Path '.ai/framework/*.yaml' -Pattern `
  'AWAITING_EPIC_ACCEPTANCE|AWAITING_USER_ACCEPTANCE|security-auditor|forge-sync-adapters|hooks: false|mcp: false'
```

Expected: every listed concept appears in the structured contracts.

- [ ] **Step 7: Manual Git checkpoint**

Proposed commit: `docs: define framework contracts and ownership`

Stop for Task Acceptance and a separate Start gate before Task 2.

---

### Task 2: Rebuild product, architecture and decision templates

**Files:**

- Modify: `.ai/templates/SPEC.md`
- Modify: `.ai/templates/ARCHITECTURE.md`
- Modify: `.ai/templates/DECISIONS.md`
- Modify: `.ai/templates/ADR.md`
- Modify: `.ai/templates/README.md`

**Interfaces:**

- Consumes: IDs, language and approval metadata from Task 1.
- Produces: target-state canonical document templates used by bootstrap Steps 01 and 02.

- [ ] **Step 1: Capture the legacy template failures**

```powershell
Select-String -Path '.ai/templates/SPEC.md','.ai/templates/ARCHITECTURE.md' `
  -Pattern 'Document Contract|Key User Journeys|Domain Rules|Data Ownership|Trust Boundaries'
```

Expected before editing: required headings are absent.

- [ ] **Step 2: Rewrite `SPEC.md`**

Use `document_status` frontmatter and add exact sections:

```text
Document Contract
Product Overview
Vision
Goals
Scope
Out of Scope
Users
Key User Journeys
Functional Requirements
Non-Functional Requirements
Domain Rules
External Integrations
Constraints
Assumptions
Success Criteria
Glossary
```

State that SPEC is approved target behavior and must not contain architecture, tasks or implementation status. Define observable `FR-*`, measurable `NFR-*` and invariant `BR-*` entries with acceptance criteria.

- [ ] **Step 3: Rewrite `ARCHITECTURE.md`**

Use `document_status` frontmatter and add system context, requirement drivers, component boundaries, dependency rules, data ownership, interfaces, trust boundaries, deployment, reliability, observability, testing strategy, migration, risks and ADR references.

State that it is target architecture and excludes task-level implementation steps.

- [ ] **Step 4: Rewrite ADR and decision index templates**

Give ADR machine-readable metadata for `id`, decision lifecycle status, dates, `supersedes`, related requirements and related components. Add Decision Drivers, Migration and Compatibility, Verification and References.

Make `DECISIONS.md` explicitly generated navigation only; ADR files remain authoritative.

- [ ] **Step 5: Update the generated project README template**

Keep README non-canonical. Include setup/run information and links to SPEC, ARCHITECTURE, BACKLOG, DECISIONS, AGENTS and CLAUDE without duplicating their content.

- [ ] **Step 6: Validate template boundaries**

```powershell
Select-String -Path '.ai/templates/SPEC.md' -Pattern 'implementation status|Key User Journeys|FR-|NFR-|BR-'
Select-String -Path '.ai/templates/ARCHITECTURE.md' -Pattern 'Data Ownership|Trust Boundaries|ADR'
Select-String -Path '.ai/templates/ADR.md' -Pattern 'Decision Drivers|Verification|supersedes'
```

Expected: all required terms are present and no template contains mojibake such as `вЂ`, `в†` or `�`.

- [ ] **Step 7: Manual Git checkpoint**

Proposed commit: `docs: rebuild canonical product and architecture templates`

Stop for Task Acceptance and a separate Start gate before Task 3.

---

### Task 3: Rebuild BACKLOG, plan and TASK templates

**Files:**

- Modify: `.ai/templates/BACKLOG.md`
- Modify: `.ai/templates/plan.md`
- Modify: `.ai/templates/TASK.md`

**Interfaces:**

- Consumes: lifecycle enums from `contracts.yaml`.
- Produces: the only templates allowed to store Epic, Bug and Task execution state.

- [ ] **Step 1: Demonstrate legacy duplication**

```powershell
Select-String -Path '.ai/templates/BACKLOG.md','.ai/templates/plan.md','.ai/templates/TASK.md' `
  -Pattern 'Current Active Epic|Future Ideas|Current Status|BLOCKED'
```

Expected before editing: matches show duplicate current-state sections and obsolete status values.

- [ ] **Step 2: Rewrite BACKLOG**

Add `document_status` frontmatter, `Epic Roadmap` and `Defect Queue`.

Epic rows must contain ID, outcome, requirement IDs, priority, readiness, dependencies, status and `Blocked by`. Bug rows must contain ID, problem, severity, user priority, related requirement, lifecycle status and scheduled TASK.

Remove `Current Active Epic`, `Future Ideas` and unstructured Notes.

- [ ] **Step 3: Rewrite plan**

Add document approval metadata, Epic objective, expected outcome, dependencies, risks, implementation strategy, ordered TASK sequence with `Depends on`, Epic acceptance criteria, mandatory quality gates, fuzzing summary and Epic user-validation history.

Remove TASK status and `Current Status`.

- [ ] **Step 4: Rewrite TASK**

Use distinct `definition_status` and lifecycle `status`. Include:

```text
Goal
Context
Scope
Out of Scope
Constraints
Acceptance Criteria
Required Tests
Manual Verification
References
Workflow State
Implementation Summary
Review Summary
Test Summary
User Validation
Iteration History
User Acceptance
```

Include revision/fingerprint fields for review and testing evidence. Do not reference external reports.

- [ ] **Step 5: Validate single-source rules**

```powershell
Select-String -Path '.ai/templates/plan.md' -Pattern 'Task.*Status|Current Status'
Select-String -Path '.ai/templates/TASK.md' -Pattern 'IN REVIEW|IN TESTING|AWAITING USER ACCEPTANCE|User Acceptance'
Select-String -Path '.ai/templates/BACKLOG.md' -Pattern 'OUTLINE|READY|Defect Queue|SCHEDULED'
```

Expected: the first command returns no matches; the other commands return all required lifecycle terms.

- [ ] **Step 6: Manual Git checkpoint**

Proposed commit: `docs: rebuild backlog and execution templates`

Stop for Task Acceptance and a separate Start gate before Task 4.

---

### Task 4: Rewrite discovery, architecture and roadmap bootstrap steps

**Files:**

- Modify: `.ai/01-product-discovery.md`
- Modify: `.ai/02-system-design.md`
- Modify: `.ai/03-release-planning.md`

**Interfaces:**

- Consumes: canonical templates from Tasks 2 and 3.
- Produces: three approval-driven workflows that create SPEC, ARCHITECTURE, DECISIONS, ADR and BACKLOG.

- [ ] **Step 1: Rewrite Product Discovery**

Separate new-project interview from existing-project repository analysis. Require the agent to surface code/document/user conflicts, write target-state requirements, create `draft` SPEC and wait for explicit approval before `approved`.

Reference `.ai/templates/SPEC.md`; do not duplicate its complete structure.

- [ ] **Step 2: Rewrite System Design**

Drive an architecture interview from approved SPEC, existing code evidence, constraints and NFRs. Add ADR-required criteria and ADR Approval gate. Require target architecture and generated DECISIONS index.

Reference templates rather than repeating them.

- [ ] **Step 3: Rewrite Release Planning**

Generate `PLANNED/OUTLINE` Epic for retained future ideas, `READY` only after requirements approval, and a separate Defect Queue. State that the user owns priority and order.

Require dependency analysis and a question before any reorder. Preserve a conflicting order as `Blocked by`, not as an automatic change.

- [ ] **Step 4: Validate removed legacy concepts**

```powershell
Select-String -Path '.ai/01-product-discovery.md','.ai/02-system-design.md','.ai/03-release-planning.md' `
  -Pattern 'Current Active Epic|Future Ideas \(Optional\)|Status.*Blocked'
```

Expected: no matches.

- [ ] **Step 5: Validate approval gates**

```powershell
Select-String -Path '.ai/01-product-discovery.md','.ai/02-system-design.md','.ai/03-release-planning.md' `
  -Pattern 'explicit user approval|ADR Approval|user-defined priority|OUTLINE|READY'
```

Expected: each workflow exposes its applicable approval rule.

- [ ] **Step 6: Manual Git checkpoint**

Proposed commit: `docs: rewrite discovery and planning bootstrap steps`

Stop for Task Acceptance and a separate Start gate before Task 5.

---

### Task 5: Rewrite active Epic and TASK preparation

**Files:**

- Modify: `.ai/04-prepare-workspace.md`

**Interfaces:**

- Consumes: approved BACKLOG plus plan and TASK templates.
- Produces: one approved active Epic workspace with all TASK files still waiting for individual Start gates.

- [ ] **Step 1: Replace automatic active-Epic selection**

Require a `READY`, unblocked Epic and an explicit Epic Start gate. If dependencies conflict, stop and ask the user.

- [ ] **Step 2: Define workspace creation**

Create:

```text
execution/active/EPIC-NNN-<name>/plan.md
execution/active/EPIC-NNN-<name>/tasks/TASK-NNN-<name>.md
```

Update BACKLOG and move/create the execution directory as one state transition.

- [ ] **Step 3: Define planning rules**

Create all initial TASK files, global IDs, ordered dependencies, acceptance criteria, required tests and manual verification. Set `definition_status: approved` only after the plan review.

Do not add a mandatory atomicity classifier. Allow later Replan only when the user requests change or actual execution requires it.

- [ ] **Step 4: Encode Replan and first-task behavior**

Any composition/order/scope change requires a displayed diff and Replan gate. After workspace approval the first TASK remains `TODO`; do not start implementation.

- [ ] **Step 5: Validate the new rules**

```powershell
Select-String -Path '.ai/04-prepare-workspace.md' `
  -Pattern 'Epic Start gate|Replan gate|definition_status|remains TODO|global'
Select-String -Path '.ai/04-prepare-workspace.md' `
  -Pattern 'Current Status|TODO.*IN PROGRESS.*DONE.*BLOCKED'
```

Expected: the first command finds every new rule; the second returns no matches.

- [ ] **Step 6: Manual Git checkpoint**

Proposed commit: `docs: enforce epic and task preparation gates`

Stop for Task Acceptance and a separate Start gate before Task 6.

---

### Task 6: Add neutral agent contracts and native adapter render templates

**Files:**

- Create: `.ai/framework/agents/context-collector.yaml`
- Create: `.ai/framework/agents/documentation-researcher.yaml`
- Create: `.ai/framework/agents/implementer.yaml`
- Create: `.ai/framework/agents/reviewer.yaml`
- Create: `.ai/framework/agents/tester.yaml`
- Create: `.ai/framework/agents/fuzzer.yaml`
- Create: `.ai/framework/agents/security-auditor.yaml`
- Create: `.ai/templates/adapters/codex/AGENTS.md`
- Create: `.ai/templates/adapters/codex/agent.toml`
- Create: `.ai/templates/adapters/claude/CLAUDE.md`
- Create: `.ai/templates/adapters/claude/agent.md`
- Delete: `.ai/templates/CLAUDE.md`
- Delete: `.ai/templates/agents/agent.md`
- Delete: `.ai/templates/agents/documentation.md`
- Delete: `.ai/templates/agents/fuzzing.md`
- Delete: `.ai/templates/agents/implementation.md`
- Delete: `.ai/templates/agents/review.md`
- Delete: `.ai/templates/agents/validation.md`

**Interfaces:**

- Consumes: role IDs, tiers and permissions from `contracts.yaml`.
- Produces: seven neutral roles and deterministic Codex TOML / Claude Markdown rendering inputs.

- [ ] **Step 1: Create the seven neutral role files**

Each YAML file must define `id`, English description, `model_tier`, write policy, network policy, spawn policy and English instructions.

Use:

- `strong`: reviewer, security-auditor;
- `balanced`: implementer, fuzzer;
- `fast`: context-collector, documentation-researcher, tester.

Orchestrator remains the strong main session and receives no subagent file.

- [ ] **Step 2: Encode role boundaries**

Require:

- only orchestrator coordinates agents and canonical state;
- agents never spawn agents;
- implementer writes code and tests but not canonical statuses;
- reviewer is read-only and returns findings only;
- tester runs targeted, affected, full-suite and configured checks without fixes;
- fuzzer is read-only and supports `PASSED`, `HARNESS REQUIRED`, `FINDINGS`, `NOT APPLICABLE`;
- security-auditor is strong, on-demand, local and network-disabled by default.

- [ ] **Step 3: Create the Codex renderer templates**

`AGENTS.md` must be a router under 150 lines. `agent.toml` must render:

```toml
name = "{{ agent.id }}"
description = "{{ agent.description }}"
model = "{{ models.codex[agent.model_tier].model }}"
model_reasoning_effort = "{{ models.codex[agent.model_tier].reasoning_effort }}"
sandbox_mode = "{{ agent.codex_sandbox_mode }}"
developer_instructions = """{{ agent.instructions }}"""
```

- [ ] **Step 4: Create the Claude renderer templates**

`CLAUDE.md` must be a router under 150 lines. `agent.md` must use native YAML frontmatter with `name`, `description`, concrete `model`, tool restrictions and the English role contract in its Markdown body.

- [ ] **Step 5: Remove Claude-only legacy templates**

Delete the old direct-copy agent set only after all seven neutral roles and both renderer shells exist.

- [ ] **Step 6: Validate roles and router limits**

```powershell
(Get-ChildItem -LiteralPath '.ai/framework/agents' -Filter '*.yaml').Count
(Get-Content -LiteralPath '.ai/templates/adapters/codex/AGENTS.md').Count
(Get-Content -LiteralPath '.ai/templates/adapters/claude/CLAUDE.md').Count
```

Expected: `7`, then two values no greater than `150`.

- [ ] **Step 7: Manual Git checkpoint**

Proposed commit: `feat: add dual-platform agent definitions`

Stop for Task Acceptance and a separate Start gate before Task 7.

---

### Task 7: Add bootstrap, intake and planning skills

**Files:**

- Create: `.ai/framework/skills/forge-bootstrap-new/SKILL.md`
- Create: `.ai/framework/skills/forge-bootstrap-existing/SKILL.md`
- Create: `.ai/framework/skills/forge-intake-feature/SKILL.md`
- Create: `.ai/framework/skills/forge-intake-bug/SKILL.md`
- Create: `.ai/framework/skills/forge-reprioritize-backlog/SKILL.md`
- Create: `.ai/framework/skills/forge-prepare-epic/SKILL.md`

**Interfaces:**

- Consumes: bootstrap steps, contracts and canonical templates.
- Produces: portable Agent Skills copied into both `.agents/skills/` and `.claude/skills/`.

- [ ] **Step 1: Use common portable skill frontmatter**

Each file must contain an English `name`, precise `description` and English workflow body. Avoid platform-only tool names in the shared body; place platform invocation differences in adapter instructions.

- [ ] **Step 2: Implement both bootstrap skills**

`forge-bootstrap-new` starts product interview. `forge-bootstrap-existing` performs repository evidence collection before interview. Both route through the six numbered steps and require explicit approvals.

- [ ] **Step 3: Implement feature and bug intake**

Feature intake creates `PLANNED/OUTLINE` Epic first and updates SPEC/ARCHITECTURE only after approval. Bug intake distinguishes an unaccepted TASK defect from a new `BUG-ID` in accepted code.

- [ ] **Step 4: Implement backlog reprioritization**

Preserve user-owned priorities. Analyze the dependency graph, show conflicts and ask before reordering. Never modify active work as a side effect.

- [ ] **Step 5: Implement Epic preparation**

Require `READY`, resolve blockers, request Epic Start, create plan/TASK files and leave the first TASK at `TODO`.

- [ ] **Step 6: Validate this skill group**

```powershell
Get-ChildItem -LiteralPath '.ai/framework/skills' -Filter 'SKILL.md' -Recurse |
  Select-String -Pattern 'explicit user approval|OUTLINE|READY|user-defined priority|Epic Start'
```

Expected: every approval-sensitive workflow contains its applicable gate.

- [ ] **Step 7: Manual Git checkpoint**

Proposed commit: `feat: add bootstrap and intake skills`

Stop for Task Acceptance and a separate Start gate before Task 8.

---

### Task 8: Add runtime, completion, security and migration skills

**Files:**

- Create: `.ai/framework/skills/forge-resume-development/SKILL.md`
- Create: `.ai/framework/skills/forge-run-task/SKILL.md`
- Create: `.ai/framework/skills/forge-complete-task/SKILL.md`
- Create: `.ai/framework/skills/forge-complete-epic/SKILL.md`
- Create: `.ai/framework/skills/forge-migrate-framework/SKILL.md`
- Create: `.ai/framework/skills/forge-security-audit/SKILL.md`
- Create: `.ai/framework/skills/forge-check-framework/SKILL.md`
- Create: `.ai/framework/skills/forge-sync-adapters/SKILL.md`

**Interfaces:**

- Consumes: TASK/Epic lifecycles, agent definitions, manifest and ownership rules.
- Produces: complete runtime and maintenance workflow without a framework CLI.

- [ ] **Step 1: Implement durable resume**

Read BACKLOG, execution directories, plan, TASK workflow state and Git diff. Treat session history as optional. Rerun any stage whose agent result was not persisted into TASK/plan.

- [ ] **Step 2: Implement the TASK loop**

Encode:

```text
Task Start → implementer → reviewer → tester → user acceptance
```

Route all failures through orchestrator back to implementer. Require review and testing again after every code change. Require the full suite unless the user approves a documented exception.

- [ ] **Step 3: Implement Task completion**

Keep Task Acceptance separate from the next Task Start. Record user acceptance in TASK. Close a scheduled BUG only after accepted TASK completion. Respect `manual` and `auto_commit_after_acceptance` Git policies.

- [ ] **Step 4: Implement Epic completion**

Automatically call fuzzer after the final accepted TASK. Handle all four outcomes. Require a new TASK and Replan for harnesses/findings, rerun fuzzing after changes, then request separate Epic Acceptance.

- [ ] **Step 5: Implement security audit**

Make invocation explicit-only. Default to local read-only analysis with no installation, network or production scan. Require separate user authorization for expanded scope. Persist accepted findings as BUG or Epic, not a report file.

- [ ] **Step 6: Implement framework checks, sync and migration**

Check adapter hashes/parity, line limits, IDs, lifecycle transitions and ownership. Sync both adapters from neutral definitions. Migration must preview, confirm, back up, validate, update lock on success and restore on failure.

- [ ] **Step 7: Validate this skill group**

```powershell
Get-ChildItem -LiteralPath '.ai/framework/skills' -Filter 'SKILL.md' -Recurse |
  Select-String -Pattern 'session history|full test suite|HARNESS REQUIRED|Epic Acceptance|read-only|migration diff'
```

Expected: the applicable workflow files contain all six safety concepts.

- [ ] **Step 8: Manual Git checkpoint**

Proposed commit: `feat: add runtime and maintenance skills`

Stop for Task Acceptance and a separate Start gate before Task 9.

---

### Task 9: Integrate dual-platform adapter generation into bootstrap

**Files:**

- Modify: `.ai/BOOTSTRAP.md`
- Delete: `.ai/05-create-ai-environment.md`
- Create: `.ai/05-create-platform-adapters.md`
- Modify: `.ai/06-final-validation.md`

**Interfaces:**

- Consumes: all canonical templates, neutral agents, portable skills and adapter renderers.
- Produces: a complete six-step bootstrap capable of creating both adapters and validating recovery.

- [ ] **Step 1: Rewrite BOOTSTRAP preflight**

Add new/existing mode, documentation language, both platforms, model mapping, Git policy, optional Superpowers, collision checks and interrupted-bootstrap recovery.

Keep BOOTSTRAP as a router; link to numbered steps instead of duplicating them.

- [ ] **Step 2: Replace Step 05**

Create `05-create-platform-adapters.md` that:

- writes `.ai/project.yaml` and `.ai/framework.lock`;
- resolves concrete model mappings;
- renders seven Codex TOML agents;
- renders seven Claude Markdown agents;
- copies fourteen skills to both native skill directories;
- creates root AGENTS and CLAUDE routers;
- creates no hooks or MCP configuration;
- checks parity and 150-line limits.

- [ ] **Step 3: Rewrite final validation**

Validate canonical frontmatter, no placeholders, global IDs, source ownership, status transitions, one active Epic/TASK, directory/status alignment, references, dual-adapter parity, no reports, no hooks/MCP and recovery without session history.

End by asking for a separate Start gate for the first TASK.

- [ ] **Step 4: Remove every reference to the old Step 05**

```powershell
Get-ChildItem -LiteralPath '.ai' -File -Recurse |
  Select-String -Pattern '05-create-ai-environment|\\.claude/agents/.*required|CLAUDE\\.md →'
```

Expected: no stale Claude-only bootstrap references.

- [ ] **Step 5: Validate bootstrap links**

```powershell
1..6 | ForEach-Object {
  $prefix = '{0:D2}-' -f $_
  Get-ChildItem -LiteralPath '.ai' -File | Where-Object Name -Like "$prefix*"
}
```

Expected: exactly one file for each prefix 01 through 06.

- [ ] **Step 6: Manual Git checkpoint**

Proposed commit: `docs: integrate dual-platform bootstrap`

Stop for Task Acceptance and a separate Start gate before Task 10.

---

### Task 10: Align public framework documentation

**Files:**

- Modify: `README.md`
- Modify: `FRAMEWORK.md`
- Modify: `RUNBOOK.md`

**Interfaces:**

- Consumes: the completed framework bundle and approved design.
- Produces: concise human-facing installation, architecture and operation guidance without duplicating detailed skills.

- [ ] **Step 1: Rewrite README quick start**

Document copying `.ai/`, the exact new/existing bootstrap prompts, both generated adapters, no framework CLI, optional Superpowers, and no default hooks/MCP.

- [ ] **Step 2: Rewrite FRAMEWORK architecture**

Describe sources of truth, root canonical documents, `.ai/` ownership, seven agents, model tiers, skill routing, Task/Epic lifecycles, fuzzing, security and migration.

Link to `FRAMEWORK_DESIGN.md` for rationale rather than duplicating its complete content.

- [ ] **Step 3: Rewrite RUNBOOK operational flows**

Cover:

- new and existing bootstrap;
- continue development;
- feature and bug intake;
- Task Start and Acceptance;
- manual validation feedback;
- Replan;
- Epic fuzzing and Acceptance;
- pause/resume;
- security audit;
- adapter sync and migration.

- [ ] **Step 4: Validate public-doc consistency**

```powershell
Select-String -Path 'README.md','FRAMEWORK.md','RUNBOOK.md' `
  -Pattern 'Codex|Claude Code|Task Start|Epic Acceptance|Superpowers|hooks|MCP'
Select-String -Path 'README.md','FRAMEWORK.md','RUNBOOK.md' `
  -Pattern 'framework CLI|Current Active Epic|fuzzing-report|TASK-NNN-review'
```

Expected: the first command finds the supported concepts; the second finds no legacy claims.

- [ ] **Step 5: Manual Git checkpoint**

Proposed commit: `docs: align framework documentation with v3 design`

Stop for Task Acceptance and a separate Start gate before Task 11.

---

### Task 11: Run conformance and bootstrap smoke validation

**Files:**

- Modify only files that fail the checks from Tasks 1–10.
- Do not add report Markdown files.

**Interfaces:**

- Consumes: the complete rewritten bundle.
- Produces: verified framework release candidate and a user-facing validation summary.

- [ ] **Step 1: Check repository whitespace and encoding**

```powershell
git diff --check
Get-ChildItem -Path '.ai','README.md','FRAMEWORK.md','RUNBOOK.md' -Recurse -File |
  Select-String -Pattern 'вЂ|в†|�'
```

Expected: no whitespace errors and no mojibake matches.

- [ ] **Step 2: Check forbidden legacy artifacts**

```powershell
Get-ChildItem -Path '.ai','README.md','FRAMEWORK.md','RUNBOOK.md' -Recurse -File |
  Select-String -Pattern `
    'Current Active Epic|Current Status|fuzzing-report\\.md|TASK-NNN-review\\.md|05-create-ai-environment'
```

Expected: no matches.

- [ ] **Step 3: Check exact role and skill counts**

```powershell
(Get-ChildItem '.ai/framework/agents' -Filter '*.yaml').Count
(Get-ChildItem '.ai/framework/skills' -Filter 'SKILL.md' -Recurse).Count
```

Expected: `7` agents and `14` skills.

- [ ] **Step 4: Check adapter constraints**

```powershell
(Get-Content '.ai/templates/adapters/codex/AGENTS.md').Count
(Get-Content '.ai/templates/adapters/claude/CLAUDE.md').Count
Get-ChildItem '.ai/templates' -Recurse -File |
  Select-String -Pattern 'hooks\\.json|\\.mcp\\.json|mcpServers|SessionStart'
```

Expected: each router is at most 150 lines; no default hook or MCP templates exist.

- [ ] **Step 5: Simulate a new-project bootstrap**

In a disposable empty Git repository outside `ai_dev_forge`:

1. copy the rewritten `.ai/`;
2. invoke Codex with the approved new-project bootstrap prompt;
3. complete only enough interview input to generate draft documents;
4. verify canonical documents appear in the repository root;
5. verify both platform adapters are generated;
6. verify the first TASK remains `TODO`;
7. verify no production code, hooks, MCP or report files are created.

- [ ] **Step 6: Simulate an existing-project bootstrap**

In a disposable repository outside `ai_dev_forge` containing source code, tests and conflicting legacy documentation:

1. copy `.ai/`;
2. invoke Claude Code with the approved existing-project prompt;
3. verify it reports conflicts before canonicalizing them;
4. verify discovered issues remain candidates until user approval;
5. verify both adapters are generated and equivalent;
6. interrupt and resume once to validate frontmatter-based recovery.

- [ ] **Step 7: Review design coverage**

Check every section of `FRAMEWORK_DESIGN.md` against at least one implemented file. Specifically confirm:

- no framework CLI;
- optional Superpowers;
- no hooks/MCP;
- no report Markdown files;
- separate Task acceptance/start gates;
- user-owned priority;
- mandatory full tests and Epic fuzzing;
- on-demand strong security auditor;
- preview/confirmation migration.
- no self-bootstrap artifacts in the `ai_dev_forge` repository root.

- [ ] **Step 8: Present final evidence**

Show the user:

- changed/deleted/created file list;
- static-check output;
- both bootstrap smoke results;
- any remaining limitations;
- proposed final commit message.

Do not claim completion and do not commit until the user accepts the final result.

Proposed commit: `release: prepare ai-dev-forge v3 framework bundle`
