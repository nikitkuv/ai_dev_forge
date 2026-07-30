---
name: forge-intake-feature
description: Add a new feature, product change, or retained future idea to an initialized Forge project. Use when the request may affect SPEC, ARCHITECTURE, ADRs, Epic scope, or Backlog priority and must not be inserted silently into active work.
---

# Intake a Feature or Product Change

## Classify the request

1. Read the relevant SPEC, ARCHITECTURE, BACKLOG, ADRs, active Epic plan, current TASK, and Git state.
2. Clarify the desired observable outcome, users, scope, exclusions, acceptance direction, constraints, urgency, and dependencies.
3. If a TASK is awaiting user acceptance, do not add new scope to it. Ask the user to choose:
   - accept the current TASK and track the feature separately;
   - expand the active Epic through the Replan gate;
   - defer the idea.

## Create the Backlog identity first

1. Present the proposed feature candidate and request explicit user approval to retain it.
2. Allocate the next global `EPIC-NNN`.
3. Add it to the Epic Roadmap as `PLANNED` with readiness `OUTLINE`, linked requirements marked `TBD` where necessary, user-defined priority, dependencies, and `Blocked by`.
4. Do not activate it or change active work.

Every retained future idea is an Epic; do not create a separate idea list.

## Update canonical target state

1. Show the exact proposed `SPEC.md` diff for new or changed target behavior, including `FR-*`, `NFR-*`, or `BR-*` acceptance criteria.
2. Apply it only after explicit user approval and update document approval metadata.
3. If architecture changes, show the `ARCHITECTURE.md` diff and proposed ADRs. Use the ADR Approval gate for significant decisions.
4. Regenerate `DECISIONS.md` from ADR frontmatter when ADRs change.
5. Change Epic readiness from `OUTLINE` to `READY` only after requirements, scope boundaries, acceptance direction, and dependencies are approved.

If the user expands the active Epic, show the plan and TASK diff and use the Replan gate before changing scope, order, or composition. New TASK files remain `TODO` until their own Task Start gates.

## Recheck priority and dependencies

Preserve user-defined priority and row order. Warn if the new Epic blocks earlier work, explain the impact, and ask before reordering. If the user preserves the order, keep blocked work `PLANNED` and record `Blocked by`.

Report the canonical changes and the next available gate. Do not start implementation or commit without the applicable explicit authorization.
