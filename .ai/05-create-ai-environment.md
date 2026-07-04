# Bootstrap Step 05 — Create AI Environment

---

## Purpose

The purpose of this step is to initialize the AI runtime environment for the repository.

This step defines how AI agents navigate, execute and coordinate work inside the project.

The primary outputs are:

- CLAUDE.md
- `.claude/agents/*.md` (subagent definitions)

Optionally:

- AI rules in .ai/rules/
- lightweight runtime configuration

---

## Inputs

Required:

- BOOTSTRAP.md
- CONVENTIONS.md
- SPEC.md
- ARCHITECTURE.md
- BACKLOG.md
- execution/

Optional:

- docs/
- references/
- DECISIONS.md

---

## Core Principle

> CLAUDE.md is a navigation + execution router, not a knowledge base.

It defines HOW to work, not WHAT the system is.

---

## Overview

This step consists of 5 phases:

1. Analyze repository structure
2. Define the AI execution workflow
3. Define subagents → write them to `.claude/agents/`
4. Generate CLAUDE.md (navigation + workflow + global rules only)
5. Validate the AI environment

---

## Key Design Rule

Two separate concerns, two separate locations:

- **CLAUDE.md** = the router. Navigation map, execution workflow, global rules, information hierarchy. ≤ 100 lines. No knowledge, no detailed agent definitions.
- **`.claude/agents/*.md`** = the subagent definitions. One file per agent, with YAML frontmatter and a system prompt. CLAUDE.md only points at this directory.

This keeps CLAUDE.md small while still giving the workflow a concrete, executable agent model.

---

## Phase 1 — Analyze Repository

Analyze:

- SPEC.md (WHAT)
- ARCHITECTURE.md (HOW)
- BACKLOG.md (WHAT TO BUILD)
- execution/ (WHAT IS BEING BUILT)
- docs/ (supporting knowledge)
- references/ (external context)

Identify:

- active Epic
- task execution structure
- navigation path for AI

Do not modify any files.

---

## Phase 2 — Define AI Execution Model

### Standard AI Navigation Flow

Every session MUST follow:

CLAUDE.md
→ BACKLOG.md
→ Active Epic (execution/active)
→ plan.md
→ TASK.md
→ Code
→ Tests
→ Update state

---

### Execution Rules

AI must:

- work on ONE task at a time
- never mix tasks
- never skip execution steps
- always update TASK + EPIC after changes
- write tests after implementation
- avoid architectural changes unless explicitly required

---

### Information Priority

AI must always prefer:

1. execution/
2. BACKLOG.md
3. ARCHITECTURE.md
4. SPEC.md
5. docs/
6. references/

---

## Phase 3 — Define Subagents (`.claude/agents/`)

The workflow described in Phase 2 is executed by a fixed set of subagents. Each subagent is a separate file in `.claude/agents/` so it can be invoked deterministically and kept out of CLAUDE.md.

Copy the ready-made subagent files from `.ai/templates/agents/` into `.claude/agents/`:

- `context.md`
- `code-context.md`
- `implementation.md`
- `validation.md`
- `documentation.md`

Each file has YAML frontmatter (`name`, `description`, optional `tools`, `model`) followed by a system prompt. For any additional custom agent, start from the generic skeleton `.ai/templates/agents/agent.md`.

### Standard subagents

#### 1. Context Agent — `.claude/agents/context.md`
- reads BACKLOG.md
- finds the active Epic
- reads plan.md
- selects the current task (the single `IN PROGRESS` task, or the first `TODO`)
- produces an execution summary

---

#### 2. Code Context Agent — `.claude/agents/code-context.md`
- analyzes the codebase (MCP / code search)
- returns a concise summary
- does not modify code

---

#### 3. Implementation Agent (MAIN) — `.claude/agents/implementation.md`
- implements the current task
- writes tests
- stays strictly within the task scope

---

#### 4. Validation Agent — `.claude/agents/validation.md`
- runs tests
- runs lint (ruff, mypy, etc.)
- reports results only — **no fixes**

---

#### 5. Documentation Agent — `.claude/agents/documentation.md`
- updates `docs/`
- summarizes changes
- never modifies core logic

---

### Subagent Rules

Subagents:

- do NOT modify code unless explicitly assigned
- do NOT cross responsibilities
- communicate only via summaries
- are invoked by the main agent as the workflow requires

Only create the subagents the project actually needs. For small projects, the main agent may perform several roles directly; in that case still create the Implementation and Validation agents, since they enforce the scope and "report, do not fix" invariants.

---

## Phase 4 — Generate CLAUDE.md

CLAUDE.md must be:

- ≤ 100 lines
- strictly navigational
- deterministic
- minimal
- non-redundant

---

### Required Sections

---

### 1. Project Overview

Short description only.

No architecture, no SPEC duplication.

---

### 2. Project Map (MANDATORY)

Must include:

- SPEC.md
- ARCHITECTURE.md
- BACKLOG.md
- execution/
- docs/
- references/

---

### 3. AI Workflow

BACKLOG
→ Active Epic
→ plan.md
→ TASK
→ Implementation
→ Tests
→ Update TASK
→ Update EPIC

---

### 4. Subagents (pointer only)

A single line pointing to the agent definitions:

> Subagents live in `.claude/agents/`. See that directory. Do not inline agent definitions here.

The detailed Context → Code Context → Implementation → Validation → Documentation model is defined in `.claude/agents/*.md`, not in CLAUDE.md.

---

### 5. Global Rules

- one task at a time
- no unrelated changes
- tests required after implementation
- update TASK + EPIC after work
- do not change architecture without request

If rules grow → move to .ai/rules/

---

### 6. Information Hierarchy

1. execution/
2. BACKLOG.md
3. ARCHITECTURE.md
4. SPEC.md
5. docs/
6. references/

---

## CLAUDE.md MUST NOT CONTAIN

- architecture details
- backlog details
- implementation instructions
- domain knowledge
- duplicated documentation
- more than 100 lines

---

## Phase 5 — Validate the AI Environment

Verify:

- CLAUDE.md exists and is ≤ 100 lines;
- CLAUDE.md contains the project map, AI workflow, global rules, and information hierarchy;
- CLAUDE.md contains no knowledge, no architecture, no detailed agent definitions;
- `.claude/agents/` exists with at least the Implementation and Validation agents;
- every subagent file has valid frontmatter and a single responsibility;
- the navigation path CLAUDE.md → BACKLOG.md → active Epic → plan.md → current task resolves without external guidance.

Fix only structural issues. Do not redesign the workflow.

---

## Outputs

Create:

- CLAUDE.md
- `.claude/agents/*.md` (at minimum: Implementation, Validation; typically all five)

Optional:

- `.ai/rules/*` (when global rules outgrow CLAUDE.md)

Do not modify:

- SPEC.md
- ARCHITECTURE.md
- BACKLOG.md
- DECISIONS.md
- decisions/
- execution/
- source code

---

## Definition of Done

Step is complete when:

- AI can navigate the repo using CLAUDE.md only
- the workflow is deterministic
- subagents are defined in `.claude/agents/*.md`
- CLAUDE.md is ≤ 100 lines and contains no agent definitions
- the system is ready for execution

---

## Next Step

Bootstrap Step 06 — Final Validation

Do not proceed automatically.
Wait for user confirmation.
