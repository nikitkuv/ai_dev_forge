# Bootstrap Step 05 — Create AI Environment

---

## Purpose

Initialize the AI runtime environment: CLAUDE.md (the router) and `.claude/agents/` (subagent definitions).

Primary outputs:

- CLAUDE.md
- `.claude/agents/*.md`

---

## Inputs

Required: BOOTSTRAP.md, CONVENTIONS.md, SPEC.md, ARCHITECTURE.md, BACKLOG.md, execution/

Optional: docs/, references/, DECISIONS.md

---

## Core Principle

> CLAUDE.md is a navigation + execution router, not a knowledge base.
> The main agent is an **orchestrator** — it delegates to subagents, does not implement code directly.

---

## Phase 1 — Analyze Repository

Read: SPEC.md, ARCHITECTURE.md, BACKLOG.md, execution/, docs/, references/

Identify: active Epic, task execution structure, navigation path.

Do not modify any files.

---

## Phase 2 — Define AI Execution Model

### Orchestrator Flow

```
CLAUDE.md → BACKLOG.md → Active Epic → plan.md → TASK → spawn subagent → review → next task → fuzzing → done
```

### Execution Rules

- Orchestrator reads backlog and selects tasks — does NOT implement code
- One task per subagent
- Independent tasks (different files) → parallel subagents
- Dependent tasks → sequential
- After task DONE → review subagent
- After all tasks DONE → fuzzing subagent

---

## Phase 3 — Define Subagents (`.claude/agents/`)

Copy from `.ai/templates/agents/` into `.claude/agents/`:

**Required:**
- `implementation.md` — gathers code context, writes code and tests
- `validation.md` — runs tests and lint, reports only (no fixes)
- `review.md` — post-task code review (stronger model), critical findings → task returns to IN PROGRESS
- `fuzzing.md` — post-epic robustness testing with random/boundary inputs

**Optional:**
- `documentation.md` — updates docs/ after task completion

**Custom:** start from `agent.md` skeleton for project-specific agents.

### Subagent Rules

- Each subagent has a single responsibility
- Subagents report to the orchestrator via summaries
- Subagents do NOT cross responsibilities
- Subagents do NOT modify code unless that is their explicit role

---

## Phase 4 — Generate CLAUDE.md

Use `.ai/templates/CLAUDE.md` as reference layout.

### Required Sections

1. **Project Overview** — 1-2 lines
2. **Project Map** — paths to SPEC, ARCHITECTURE, BACKLOG, execution, docs, references
3. **AI Workflow — Orchestrator Pattern** — the orchestrator loop, subagent table, parallelization rules
4. **Context Gathering** — understand existing code before writing new code
5. **Global Rules** — one task per subagent, tests required, update state, no architecture changes
6. **Code Quality** — max 300 lines/file, single responsibility, logging, error handling
7. **Information Hierarchy** — execution/ > BACKLOG > ARCHITECTURE > SPEC > docs > references

### CLAUDE.md MUST NOT CONTAIN

- architecture details, backlog details, implementation instructions
- domain knowledge, duplicated documentation
- inlined subagent definitions

---

## Phase 5 — Validate the AI Environment

Verify:

- CLAUDE.md exists and is concise (~90 lines)
- CLAUDE.md contains: project map, orchestrator workflow, context gathering, code quality rules, global rules
- `.claude/agents/` exists with at least: implementation, validation, review, fuzzing
- every subagent file has valid frontmatter and a single responsibility
- no stale MCP references (codebase-memory-mcp) in any agent file
- the navigation path CLAUDE.md → BACKLOG.md → active Epic → plan.md → task resolves without external guidance

Fix only structural issues. Do not redesign the workflow.

---

## Outputs

Create: CLAUDE.md, `.claude/agents/*.md` (implementation, validation, review, fuzzing; optional: documentation)

Do not modify: SPEC.md, ARCHITECTURE.md, BACKLOG.md, DECISIONS.md, decisions/, execution/, source code

---

## Definition of Done

- CLAUDE.md exists with orchestrator pattern
- 4 required subagents defined in `.claude/agents/`
- No stale tool references
- Navigation path works end-to-end

---

## Next Step

Bootstrap Step 06 — Final Validation. Wait for user confirmation.
