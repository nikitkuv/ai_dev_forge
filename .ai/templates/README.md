# Templates

Canonical, fill-in templates for every artifact the bootstrap produces.
They exist so bootstrap output is **reproducible** (a stated framework goal):
the agent fills a form rather than inventing structure each run.

## Usage

During bootstrap, copy the relevant template to its target location and fill
the `<placeholders>`. Remove placeholders and comments you do not need.

| Template | Becomes | Created in |
|----------|---------|-----------|
| `SPEC.md` | `SPEC.md` | Step 01 |
| `ARCHITECTURE.md` | `ARCHITECTURE.md` | Step 02 |
| `DECISIONS.md` | `DECISIONS.md` (index) | Step 02 |
| `ADR.md` | `decisions/ADR-NNN-<name>.md` | Step 02, runtime |
| `BACKLOG.md` | `BACKLOG.md` | Step 03 |
| `plan.md` | `execution/active/EPIC-NNN-<name>/plan.md` | Step 04 |
| `TASK.md` | `.../tasks/TASK-NNN-<name>.md` | Step 04 |
| `CLAUDE.md` | `CLAUDE.md` (~90 lines) | Step 05 |
| `agents/implementation.md` | `.claude/agents/implementation.md` | Step 05 |
| `agents/validation.md` | `.claude/agents/validation.md` | Step 05 |
| `agents/review.md` | `.claude/agents/review.md` | Step 05 |
| `agents/fuzzing.md` | `.claude/agents/fuzzing.md` | Step 05 |
| `agents/documentation.md` | `.claude/agents/documentation.md` | Step 05 (optional) |
| `agents/agent.md` | `.claude/agents/<custom>.md` (skeleton for extra agents) | Step 05, on demand |

## Conventions baked in

- Canonical naming: `EPIC-NNN-<name>`, `TASK-NNN-<name>.md`, `ADR-NNN-<name>.md`
- Status vocabularies (Epic / Task / ADR) — see `../CONVENTIONS.md`
- Single responsibility per artifact; no cross-layer duplication
