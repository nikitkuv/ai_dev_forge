# CONVENTIONS.md

---

## Purpose

This document defines the conventions used across all bootstrap steps in the AI Dev Forge.

These conventions ensure:

- consistency
- determinism
- maintainability
- AI-readability

All bootstrap steps MUST follow these rules.

---

# Naming Conventions

## Bootstrap Steps

Bootstrap steps are executed sequentially.

Use the following naming format:

```text
01-<step>.md
02-<step>.md
03-<step>.md
...
```

---

## Examples

```text
01-spec.md
02-architecture.md
03-backlog.md
04-execution.md
05-ai-environment.md
06-final-validation.md
```

---

## Identifier Naming (Canonical)

All identifiers are zero-padded to 3 digits and use kebab-case for the human-readable suffix.

| Entity | Identifier | Folder / File |
|--------|-----------|---------------|
| Epic | `EPIC-001` | `execution/active/EPIC-001-<short-name>/` |
| Task | `TASK-001` | `execution/active/EPIC-001-<name>/tasks/TASK-001-<short-name>.md` |
| Decision | `ADR-001` | `decisions/ADR-001-<short-name>.md` |

Rules:

- `<short-name>` is lowercase kebab-case, 1–4 words, stable over the artifact's lifetime.
- The Epic folder name MUST exactly match the Epic name in BACKLOG.md.
- A Task file belongs to exactly one Epic folder.
- Never reuse an identifier once retired.

---

## Directory Layout (Canonical)

```text
project/
├── README.md
├── CLAUDE.md
├── SPEC.md
├── ARCHITECTURE.md
├── BACKLOG.md
├── DECISIONS.md            # ADR index (navigation)
├── decisions/              # individual ADR records
│   └── ADR-001-<name>.md
├── execution/
│   ├── active/
│   │   └── EPIC-001-<name>/
│   │       ├── plan.md
│   │       └── tasks/
│   │           └── TASK-001-<name>.md
│   └── completed/
├── docs/                   # created during bootstrap (may start empty)
└── references/             # created during bootstrap (may start empty)
```

---

# Status Vocabularies

Controlled vocabularies are mandatory. Free-text statuses break determinism.

## Epic Status (BACKLOG.md)

- `Planned` — not started
- `Active` — currently being executed
- `Completed` — done and archived to `execution/completed/`
- `Blocked` — cannot proceed (reason required)
- `Cancelled` — abandoned

Invariant: **exactly one** Epic is `Active` (or none, before execution starts).

---

## Task Status (TASK-NNN.md)

- `TODO` — not started
- `IN PROGRESS` — currently being worked on
- `DONE` — complete, acceptance criteria met
- `BLOCKED` — cannot proceed (reason required)
- `CANCELLED` — abandoned

Invariant: **at most one** Task is `IN PROGRESS` per active Epic.

This is the determinism mechanism for "current task": the active task is the single `IN PROGRESS` task inside the single `Active` Epic. If none is `IN PROGRESS`, the next task is the first `TODO` task in plan.md order.

---

## Decision Status (ADR-NNN.md)

- `Proposed` — drafted, not yet ratified
- `Accepted` — ratified and in force
- `Superseded` — replaced by a later ADR (link required)
- `Deprecated` — no longer relevant
- `Rejected` — considered and discarded (kept for the record)

---

# Decision Records Model

Architectural and significant technical decisions are captured as **ADR (Architecture Decision Records)**.

The model mirrors the BACKLOG / execution split:

- `DECISIONS.md` — lightweight **index** (navigation only). Lists every ADR: ID, title, status, file link. Contains no decision content.
- `decisions/` — one **atomic record per file**: `decisions/ADR-NNN-<short-name>.md`.

Each ADR is single-responsibility and independently readable (Minimal Context Principle): an AI agent reads only the relevant record, not the whole log.

`DECISIONS.md` + `decisions/` are initialized during Step 02 (System Design), where the first architectural decisions are made, and grow during runtime as new significant decisions occur.

---

# Templates

Every artifact has a canonical fill-in template under `.ai/templates/`.

During bootstrap, copy the relevant template to its target location and fill the placeholders. This is the primary mechanism for reproducible (deterministic) output: the agent fills a defined form rather than inventing structure each run.

See `.ai/templates/README.md` for the full mapping.

---

# Standard Step Structure

Every bootstrap step MUST follow this structure:

---

## 1. Goal

Define:

- purpose of the step
- expected outcome
- scope boundaries

---

## 2. Inputs

List required artifacts before execution.

Examples:

- SPEC.md
- ARCHITECTURE.md
- BACKLOG.md

If none:

```text
None
```

---

## 3. Actions

Define step-by-step instructions for the AI agent.

Rules:

- must be ordered
- must be explicit
- must avoid ambiguity
- must be deterministic

---

## 4. Restrictions

Define what MUST NOT be done during the step.

Common restrictions:

- do not implement features
- do not modify production code
- do not skip steps
- do not invent requirements
- do not proceed automatically

---

## 5. Definition of Done

Define objective completion criteria.

Must be:

- verifiable
- non-ambiguous
- based on outputs, not intent

---

## 6. Outputs

List all files created or modified.

Must clearly separate:

- created files
- updated files

Examples:

- SPEC.md
- ARCHITECTURE.md
- BACKLOG.md
- execution/
- CLAUDE.md

---

## 7. Next Step

Specify the next bootstrap step.

Rule:

> Bootstrap never proceeds automatically.

User must explicitly confirm continuation.

---

# Documentation Style Rules

All generated documentation MUST be:

- concise
- structured
- AI-readable
- deterministic
- unambiguous

---

## Preferred Formatting

Use:

- headings
- bullet points
- tables (when useful)
- short paragraphs

Avoid:

- long narrative explanations
- ambiguous phrasing
- duplicated information

---

# Question Policy

If required information is missing:

- ask the user
- do NOT assume
- do NOT fabricate
- do NOT infer silently

Bootstrap is a controlled process, not a guessing system.

---

# Existing Repository Handling

When bootstrap is applied to an existing project:

- analyze existing code first
- preserve valid documentation
- extend rather than overwrite
- explicitly report inconsistencies
- align structure gradually

---

# New Repository Handling

When bootstrap is applied to a new project:

- generate all required artifacts
- initialize full structure
- ensure consistency across all documents
- prepare system for execution phase

---

# Consistency Rules

All artifacts must remain consistent:

- SPEC ↔ ARCHITECTURE
- BACKLOG ↔ execution
- execution ↔ plan.md ↔ TASK.md
- DECISIONS.md ↔ decisions/ (index ↔ records)
- CLAUDE.md ↔ navigation system
- Epic folder name ↔ Epic name in BACKLOG.md
- Epic Status ↔ Task Status (one Active Epic ↔ at most one IN PROGRESS task)

If inconsistencies appear:

- report them immediately
- do not silently ignore them

---

# Output Quality Requirements

Every generated artifact MUST:

- be syntactically valid Markdown
- be internally consistent
- avoid duplication of information
- follow framework structure
- be optimized for AI reasoning

---

# Completion Protocol

After each bootstrap step:

1. Summarize completed actions
2. List created/modified files
3. Report inconsistencies or open questions
4. Suggest next step
5. Wait for user confirmation

---

# Critical Principle

> Bootstrap is a deterministic system, not a creative process.

The goal is not to “design freely”, but to produce a reproducible engineering environment for AI agents.

---
