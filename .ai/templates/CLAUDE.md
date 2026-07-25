<!-- TEMPLATE: CLAUDE.md — the AI router. Navigation + workflow + rules. -->
<!-- Created in: Bootstrap Step 05. Reference layout — adapt to the project. Target: ~90 lines. -->

# CLAUDE.md — <Project Name>

## Project Overview

<1–2 lines: what this project is.>

## Project Map

- `SPEC.md` — WHAT the product is
- `ARCHITECTURE.md` — HOW the system is organized
- `BACKLOG.md` — Epics + current Active Epic
- `DECISIONS.md` → `decisions/` — ADR index + records
- `execution/active/EPIC-NNN-<name>/` — current work (plan.md + tasks/)
- `execution/completed/` — finished Epics
- `docs/` — documentation
- `references/` — external materials

## AI Workflow — Orchestrator Pattern

The main agent is an **orchestrator**. It does NOT implement code directly.

```
Read BACKLOG → find Active Epic → read plan.md → pick task(s) → spawn subagent(s) → review results → repeat
```

### Orchestrator Loop

1. Read `BACKLOG.md` → find the active Epic
2. Read `execution/active/.../plan.md` → understand task sequence
3. Pick the current task(s):
   - the single `IN PROGRESS` task, OR
   - the first `TODO` task(s) — set to `IN PROGRESS`
4. **Spawn implementation subagent** per task (via `Agent` tool), passing task file + context
5. If tasks are independent (different files) → spawn multiple subagents in parallel
6. When subagent reports DONE → **spawn review subagent** for that task
7. If review finds critical issues → spawn implementation subagent for fixes
8. When review passes → move to next task
9. When all tasks DONE → **spawn fuzzing subagent** for the Epic
10. When fuzzing passes → mark Epic Completed

### Subagents

Subagents live in `.claude/agents/`. Do not inline definitions here.

| Agent | Role | When |
|-------|------|------|
| `implementation` | Implement one task: gather context, write code, write tests | Every task |
| `validation` | Run tests and lint, report only (no fixes) | After implementation |
| `review` | Review code quality, architecture compliance, bugs | After task DONE |
| `fuzzing` | Test functions with random/boundary/invalid inputs | After all tasks DONE |

### When to Parallelize

- Tasks modify different files → spawn multiple implementation agents
- Tasks touch the same files → run sequentially
- Review can run while next task starts (review is read-only)

## Context Gathering

Understand the existing code and find the affected files before writing anything.

Never guess — always check existing code first.

## Global Rules

- Orchestrator delegates work to subagents — does not implement directly
- One task per subagent. Stay within task scope.
- Write tests after implementation.
- Update TASK + plan.md after each task. Move TODO → IN PROGRESS → DONE.
- Log significant decisions as ADRs in `decisions/`.
- Do not change architecture without explicit request.
- Report inconsistencies; do not silently ignore them.
- Do NOT make git commits — the developer handles version control manually.

## Code Quality

- **Max 300 lines/file.** Split if larger.
- **Single responsibility** — one file = one concern.
- **Separate data models** (Pydantic, DTOs) from business logic.
- **No bare `except`** — always log error with context and raise descriptive exception.
- **Logging in every module** — `logging.getLogger(__name__)`, include context (IDs, values, what was being done).
- **Naming:** `snake_case` files/functions (Python), `PascalCase` classes, `is_/has_` for booleans.

## Information Hierarchy

Prefer: `execution/` → `BACKLOG.md` → `ARCHITECTURE.md` → `SPEC.md` → `docs/` → `references/`.
