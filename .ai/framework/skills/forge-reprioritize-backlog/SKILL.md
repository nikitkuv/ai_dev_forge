---
name: forge-reprioritize-backlog
description: Reprioritize the Epic Roadmap or Defect Queue while preserving user ownership of P0-P3 priority and row order. Use when priorities change or dependency analysis suggests that a later Epic blocks earlier work.
---

# Reprioritize the Backlog

## Build the evidence

1. Read `BACKLOG.md`, relevant requirements, architecture, ADRs, active or paused Epic state, and known external dependencies.
2. Ask the `context-collector` for a read-only dependency graph when repository evidence is needed.
3. Capture the user's requested priority and ordering changes without applying them.
4. Distinguish Epic dependencies from `Blocked by`, defect severity from user-defined priority, and active execution from planned order.

## Analyze conflicts

1. Compare the proposed order with the dependency graph.
2. Identify any later Epic that blocks an earlier one, any unresolved dependency, and any priority collision.
3. Show the current order, proposed order, conflict, impact, and a concrete recommendation.
4. Ask whether the user wants to change the order.

The user owns priority and row order. Never reorder silently.

## Apply only the approved diff

1. Present the exact `BACKLOG.md` diff.
2. Request explicit user approval.
3. Update only approved priority, row-order, dependency, and `Blocked by` fields.
4. Preserve a conflicting user order when requested: keep the affected Epic `PLANNED` and record its blocker.
5. Revalidate IDs, readiness, dependencies, and the invariant of at most one `ACTIVE` Epic.

Do not activate, pause, cancel, or complete an Epic as a side effect. Do not modify plan or TASK scope, move execution directories, schedule defects, or start work. If the requested priority change requires altering active work, present that as a separate decision and gate.

Return the accepted ordering, unresolved conflicts, and any blocked work.
