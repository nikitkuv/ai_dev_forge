---
document_type: backlog
document_status: draft
language: "<language-code>"
created_at: "<YYYY-MM-DD>"
approved_at:
---

# <Product Name> — Backlog

## Document Contract

This document is the single source of truth for Epic priority, readiness, dependencies, blocking metadata and lifecycle status, and for defect lifecycle state.

It must not contain Tasks, completion percentages, execution summaries, or a duplicated “current Epic” section. Every retained product idea is an Epic in the roadmap, initially `PLANNED` and optionally `OUTLINE`.

The user controls `P0`–`P3` priority and row order within each priority. The agent analyzes dependencies and warns when a later Epic blocks an earlier one, but changes priority or order only after explicit user confirmation.

## Epic Roadmap

| ID | Epic and intended outcome | Requirements | Priority | Readiness | Dependencies | Status | Blocked by |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EPIC-001 | <Name — observable outcome> | <FR-/NFR-/BR-IDs or `TBD` while OUTLINE> | P0 | READY | — | PLANNED | — |
| EPIC-002 | <Name — observable outcome> | TBD | P1 | OUTLINE | EPIC-001 | PLANNED | EPIC-001 |

Readiness and lifecycle values are defined only in `.ai/framework/contracts.yaml`. An `OUTLINE` Epic cannot receive an approved detailed workspace. A `PLANNED + READY` Epic may have one approved workspace under `execution/planned/` even while its declared dependencies or blockers prevent activation. At most one Epic may occupy the nonterminal active-work states `ACTIVE`, `VALIDATING`, `FUZZING`, or `AWAITING EPIC ACCEPTANCE`.

## Defect Queue

| ID | Problem | Severity | User priority | Related requirement | Status | Scheduled TASK |
| --- | --- | --- | --- | --- | --- | --- |
| BUG-001 | <Observable failure and affected user or system> | <critical/high/medium/low> | P1 | <FR-/NFR-/BR-ID or —> | OPEN | — |
| BUG-002 | <Observable failure> | <severity> | P2 | <requirement or —> | SCHEDULED | TASK-001 |

Severity describes impact; user priority controls repair order. Defect lifecycle values are defined only in `.ai/framework/contracts.yaml`. A problem found in an unaccepted Task remains in that Task and does not receive a separate Bug ID.
