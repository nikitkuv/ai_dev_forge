# Bootstrap Step 05 — Create AI Environment

---

## Purpose

The purpose of this step is to initialize the AI runtime environment for the repository.

This step defines how AI agents navigate, execute and coordinate work inside the project.

The primary output is:

- CLAUDE.md

Optionally:

- AI subagents definitions
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

This step consists of 4 phases:

1. Analyze repository structure
2. Define AI execution workflow
3. Generate CLAUDE.md
4. Define optional subagents

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

## Phase 3 — Subagent Workflow (SIMPLIFIED MODEL)

### Agents involved:

#### 1. Context Agent
- reads BACKLOG.md
- finds active Epic
- reads plan.md
- selects current TASK
- produces execution summary

---

#### 2. Code Context Agent
- analyzes codebase (MCP / search tools)
- returns concise summary

---

#### 3. Implementation Agent (MAIN)
- implements TASK
- writes tests
- stays within scope

---

#### 4. Validation Agent
- runs tests
- runs lint (ruff, mypy, etc.)
- reports results only (NO fixes)

---

#### 5. Documentation Agent
- updates docs/
- summarizes changes
- never modifies core logic

---

### Subagent Rule

Subagents:

- do NOT modify code unless explicitly assigned
- do NOT cross responsibilities
- communicate only via summaries

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

### 4. Subagent Execution Model

Context Agent
→ Code Context Agent
→ Implementation Agent
→ Validation Agent
→ Documentation Agent

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

## Phase 5 — Optional Subagents

Only create if needed.

Each must:

- have single responsibility
- be minimal
- be deterministic
- not overlap with others

---

## Outputs

Create:

- CLAUDE.md

Optional:

- .ai/rules/*
- subagent definitions

Do not modify:

- SPEC.md
- ARCHITECTURE.md
- BACKLOG.md
- execution/
- source code

---

## Definition of Done

Step is complete when:

- AI can navigate repo using CLAUDE.md only
- workflow is deterministic
- subagent model is defined
- CLAUDE.md is ≤ 100 lines
- system is ready for execution

---

## Next Step

Bootstrap Step 06 — Final Validation

Do not proceed automatically.
Wait for user confirmation.
