<!-- TEMPLATE: CLAUDE.md — the AI router. Navigation + workflow + global rules ONLY. -->
<!-- Created in: Bootstrap Step 05. HARD LIMIT: ≤ 100 lines. No knowledge, no agent defs. -->
<!-- This is a reference layout. Strip every placeholder you do not need to stay under 100 lines. -->

# CLAUDE.md — <Project Name>

## Project Overview

<1–2 lines: what this project is. No architecture.>

## Project Map

- `SPEC.md` — WHAT the product is
- `ARCHITECTURE.md` — HOW the system is organized
- `BACKLOG.md` — roadmap of Epics + current Active Epic
- `DECISIONS.md` → `decisions/` — ADR index + records
- `execution/active/EPIC-NNN-<name>/` — current work (plan.md + tasks/)
- `execution/completed/` — finished Epics
- `docs/` — supporting documentation
- `references/` — external materials

## AI Workflow

Every session:

```
CLAUDE.md → BACKLOG.md → Active Epic → plan.md → current TASK → implement → test → update state
```

The current task is the single `IN PROGRESS` task in the Active Epic (or the first `TODO`).

## Subagents

Subagents live in `.claude/agents/`. Invoke them per the workflow; do not inline their definitions here.

- Context → Code Context → Implementation → Validation → Documentation

## Global Rules

- Work on ONE task at a time. Stay within its scope.
- Write tests after implementation.
- Update TASK + plan.md after work. Move task TODO → IN PROGRESS → DONE.
- Log significant decisions as ADRs in `decisions/` + update `DECISIONS.md`.
- Do not change architecture without an explicit request.
- Report inconsistencies; do not silently ignore them.

## Information Hierarchy

Prefer, in order: `execution/` → `BACKLOG.md` → `ARCHITECTURE.md` → `SPEC.md` → `docs/` → `references/`.
