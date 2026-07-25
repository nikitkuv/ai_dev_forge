# Bootstrap Step 06 — Final Validation

---

## Purpose

The purpose of this step is to verify that the project foundation is complete, internally consistent, and ready for day-to-day development.

This is a validation step.

No new architecture, planning, or implementation should be introduced.

Only verify and, if necessary, correct inconsistencies within the bootstrap outputs.

---

# Inputs

Required:

- BOOTSTRAP.md
- CONVENTIONS.md
- SPEC.md
- ARCHITECTURE.md
- BACKLOG.md
- execution/
- CLAUDE.md

Optional:

- docs/
- references/
- DECISIONS.md

---

# Core Principle

> If an AI coding agent cannot reliably navigate from `CLAUDE.md` to the current development task without additional user guidance, the bootstrap process is incomplete.

---

# Overview

This step consists of four phases.

1. Validate the project structure.
2. Validate the AI workflow.
3. Validate documentation consistency.
4. Correct minor inconsistencies.

Do not redesign the project.

Do not introduce new functionality.

---

# Phase 1 — Structural Validation

Verify that the repository contains all required artifacts.

Required project files:

- README.md
- CLAUDE.md
- SPEC.md
- ARCHITECTURE.md
- BACKLOG.md
- DECISIONS.md

Required directories:

- execution/
- execution/active/
- execution/completed/
- decisions/
- docs/
- references/
- .claude/agents/

Verify that:

- naming follows the framework conventions (`EPIC-NNN-<name>`, `TASK-NNN-<name>.md`, `ADR-NNN-<name>.md`);
- directory structure is correct;
- no required artifact is missing.

---

# Phase 2 — AI Workflow Validation

Simulate a completely new AI coding session.

Verify that the following navigation path is possible:

```text
CLAUDE.md
&#x20;   ↓
BACKLOG.md
&#x20;   ↓
Active Epic
&#x20;   ↓
plan.md
&#x20;   ↓
Current Task
&#x20;   ↓
Relevant Documentation
&#x20;   ↓
Source Code
```

Ensure that:

- the active Epic is clearly identified;
- the current task is unambiguous;
- the next development action is obvious.

If any navigation step is unclear, improve the documentation rather than adding explanations elsewhere.

---

# Phase 3 — Consistency Validation

Verify that every document has a single responsibility.

## SPEC.md

Verify that it contains:

- product definition;
- goals;
- requirements;
- constraints.

Verify that it does not contain:

- architecture;
- implementation plans;
- backlog;
- tasks.

---

## ARCHITECTURE.md

Verify that it contains:

- system structure;
- architectural components;
- responsibilities;
- high-level data flow.

Verify that it does not contain:

- product requirements;
- task breakdowns;
- implementation details.

---

## BACKLOG.md

Verify that it contains:

- project roadmap;
- Epic list;
- Epic priorities;
- current active Epic.

Verify that it does not contain:

- implementation plans;
- task lists;
- execution progress.

---

## execution/

Verify that:

- exactly one active Epic exists;
- every active Epic contains a `plan.md`;
- every task belongs to its Epic;
- every task has a Status field with a valid value;
- at most one task is `IN PROGRESS` per active Epic (current-task determinism);
- task ordering matches the implementation plan.

---

## DECISIONS.md + decisions/

Verify that:

- `DECISIONS.md` is a navigation index (no decision content);
- every entry in `DECISIONS.md` points to an existing record in `decisions/`;
- every record in `decisions/` is referenced from `DECISIONS.md`;
- ADR files follow the canonical `ADR-NNN-<name>.md` naming and have a valid status.

---

## .claude/agents/

Verify that:

- at least the Implementation, Validation, Review, and Fuzzing agents exist;
- every agent file has valid frontmatter and a single responsibility;
- CLAUDE.md does not inline agent definitions (it only points to this directory).

---

## CLAUDE.md

Verify that:

- it acts as a navigation entrypoint (~90 lines);
- it contains the project map;
- it defines the orchestrator workflow (main agent delegates to subagents);
- it contains a Context Gathering section;
- it contains Code Quality rules (modular code, logging, error handling);
- it does not duplicate other documentation;
- it does not inline subagent definitions;
- it does not reference removed agents (context, code-context).

---

# Phase 4 — Correct Minor Inconsistencies

If inconsistencies are found, apply only the minimum necessary corrections.

Allowed corrections include:

- fixing document structure;
- aligning naming conventions;
- removing duplicated information;
- correcting navigation references;
- synchronizing related documents.

Do not:

- redesign the architecture;
- change the product scope;
- introduce new Epics;
- rewrite major documentation sections without user approval.

---

# Validation Criteria

After validation, the repository should satisfy the following principles.

## 1. Navigability

An AI coding agent can navigate from `CLAUDE.md` to the current task without external guidance.

---

## 2. Determinism

Given the same repository state:

- the same active Epic is identified;
- the same current task is selected;
- the same workflow is followed.

---

## 3. Separation of Concerns

Each document has a single responsibility.

- SPEC.md → What the product is
- ARCHITECTURE.md → How the system is organized
- BACKLOG.md → What should be built next
- execution/ → What is currently being implemented
- CLAUDE.md → How the AI navigates the repository

Information should not be duplicated across layers.

---

## 4. Minimal Cognitive Load

Each artifact should:

- have one clear purpose;
- avoid duplicated information;
- remain concise;
- be easy to navigate.

---

# Definition of Done

This step is complete only if:

- all required project artifacts exist;
- the repository structure follows the framework;
- documentation is internally consistent;
- exactly one active Epic exists (or none if development has not started);
- the execution workspace is valid;
- the AI navigation workflow is unambiguous;
- CLAUDE.md serves as a reliable entrypoint with orchestrator pattern;
- the repository is ready for everyday development.

---

# Outputs

Update documentation only if required to resolve inconsistencies.

Do not create new architectural artifacts.

Do not modify source code.

---

# Bootstrap Completion

If all validation checks pass, report:

> Bootstrap Complete — Repository Ready for Development

---

# Post-Bootstrap State

After successful bootstrap:

- project planning is managed through `BACKLOG.md`;
- active development is managed through `execution/`;
- documentation evolves together with the project;
- AI agents navigate the repository exclusively through `CLAUDE.md`;
- future work follows the standard development workflow defined by this framework.

---

# End of Step
