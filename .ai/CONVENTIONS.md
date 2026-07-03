# CONVENTIONS.md

---

## Purpose

This document defines the conventions used across all bootstrap steps in the AI Coding Framework 24.

These conventions ensure:

- consistency
- determinism
- maintainability
- AI-readability

All bootstrap steps MUST follow these rules.

---

# Naming Conventions

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
- CLAUDE.md ↔ navigation system

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