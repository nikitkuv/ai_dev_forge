# BOOTSTRAP.md

---

## Purpose

This document defines the global rules for the bootstrap process used by the AI Coding Framework 24.

The bootstrap process prepares a repository for long-term AI-assisted software development.

Its purpose is **not to implement product features**.

Its purpose is to construct a complete, deterministic engineering workspace that enables AI coding agents to operate with minimal external context across the entire lifecycle of the project.

Bootstrap is executed only during:
- project initialization
- migration of an existing repository into this framework

---

# Core Principles

---

## 1. Documentation Before Implementation

No production code is written during bootstrap.

The system must first define:

- what the product is (SPEC)
- how the system works (ARCHITECTURE)
- what will be built (BACKLOG)
- how work is executed (execution/)
- how AI navigates the repository (CLAUDE.md)

Implementation begins only after this structure exists.

---

## 2. Documentation Is the Source of Truth

During bootstrap, documentation is authoritative.

Never invent information.

If required information is missing:

- ask the user
- inspect the repository
- mark unknowns explicitly as `TODO`

Do not fabricate:
- requirements
- architecture
- system behavior

---

## 3. Progressive Refinement

Bootstrap is iterative.

Each step refines system understanding.

No generated document is assumed final until validation step.

All artifacts may be revised before proceeding.

---

## 4. Single Responsibility per Artifact

Each file has one role:

- SPEC.md → WHAT the product is
- ARCHITECTURE.md → HOW the system works
- BACKLOG.md → WHAT will be built (Epics only)
- execution/ → WHAT is currently being built
- CLAUDE.md → HOW AI navigates the repository

No cross-layer duplication is allowed.

Documents must reference each other instead of repeating content.

---

## 5. Repository First Principle

Prefer existing repository information in this order:

1. Source code
2. Existing documentation
3. Tests
4. User input

Never overwrite existing valid documentation unless explicitly required.

---

## 6. Ask Before Assuming

If critical information is missing:

→ ask the user

Do not guess.

Do not infer missing requirements.

---

## 7. Human Validation Gate

All major decisions require user confirmation:

- product scope (SPEC)
- system design (ARCHITECTURE)
- roadmap (BACKLOG)

Bootstrap may propose, but not decide unilaterally.

---

## 8. Consistency Requirement

All artifacts must remain consistent:

- SPEC ↔ ARCHITECTURE
- BACKLOG ↔ execution
- execution ↔ plan.md ↔ TASK.md
- CLAUDE.md ↔ navigation model

Any inconsistency must be reported and resolved immediately.

---

## 9. AI-Oriented Documentation Design

All documents are optimized for AI reasoning.

They must be:

- structured
- explicit
- unambiguous
- navigable
- minimal but complete

Avoid prose-heavy explanations.

Prefer:
- headings
- lists
- deterministic structure

---

# Bootstrap Workflow

Bootstrap consists of 6 sequential steps:

---

## Step 01 — SPEC.md (Product Definition)

Define:
- what the product is
- constraints
- requirements
- goals

---

## Step 02 — ARCHITECTURE.md (System Design)

Define:
- system structure
- components
- interactions
- technical decisions

---

## Step 03 — BACKLOG.md (Epic Planning)

Define:
- Epics only
- no tasks
- no execution state
- no progress tracking

---

## Step 04 — execution/ (Workspace Initialization)

Create runtime structure:

- active Epic
- plan.md
- atomic TASK files
- task decomposition

execution = current state of work

---

## Step 05 — CLAUDE.md (AI Runtime Router)

Create AI entrypoint:

Requirements:
- ≤ 100 lines
- navigation only
- no duplicated knowledge
- contains project map
- contains AI workflow rules

CLAUDE.md is NOT documentation.

It is a routing layer for AI.

---

## Step 06 — Final Validation

Validate:

- structure correctness
- navigation completeness
- workflow determinism
- consistency across artifacts
- readiness for execution

Fix only inconsistencies, do not redesign system.

---

# Scope

Bootstrap MAY:

- analyze repository
- generate documentation
- structure project layout
- define execution system
- configure AI navigation layer

Bootstrap MUST NOT:

- implement features
- refactor production systems
- introduce speculative architecture
- expand product scope

---

# Definition of Done

Bootstrap is complete when:

- all required artifacts exist
- system structure is consistent
- execution workflow is operational
- AI navigation via CLAUDE.md is functional
- at least one Epic is ready for execution
- repository is ready for daily AI-driven development

---

# Success Criteria

A new AI session must be able to understand and execute the project using ONLY:

CLAUDE.md
↓
BACKLOG.md
↓
Active Epic (execution/)
↓
Current TASK

Without requiring additional user explanation.

---

# End of Bootstrap Specification