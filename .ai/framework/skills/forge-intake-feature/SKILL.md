---
name: forge-intake-feature
description: Add a new feature, product change, or retained future idea to an initialized Forge project. Use when the request may affect SPEC, ARCHITECTURE, ADRs, Epic scope, or Backlog priority and must not be inserted silently into active work.
---

# Intake a Feature or Product Change

## Classify the request

1. Read the relevant SPEC, ARCHITECTURE, BACKLOG, ADRs, all affected planned workspaces, the active Epic plan, current TASK, explicitly referenced `INV-NNNN` records, obviously relevant investigations by subject, area, or relevant paths, and Git state. Confirm uncertain investigation matches with the user. Check their baseline and relevant paths before reusing conclusions; recheck only what changed materially.
2. Clarify the desired observable outcome, users, scope, exclusions, acceptance direction, constraints, urgency, and dependencies.
3. Separate confirmed user intent, repository evidence, assumptions, and unresolved decisions. Do not turn an inference into target behavior.
4. If a material product or design choice remains, present two or three viable approaches with trade-offs and a recommendation. Keep the discussion proportional to the decision; do not create a parallel design artifact.
5. If a TASK is awaiting user acceptance, do not add new scope to it. Ask the user to choose:
   - accept the current TASK and track the feature separately;
   - expand the active Epic through the Replan gate;
   - defer the idea.

Discovery ends at the applicable canonical approval gate. Do not invoke implementation planning, create implementation files, activate an Epic, start a TASK, or commit discovery artifacts.

## Create the Backlog identity first

1. Present the proposed feature candidate and request explicit user approval to retain it.
2. Allocate the next global `EPIC-NNN`.
3. Add it to the Epic Roadmap as `PLANNED` with readiness `OUTLINE`, linked requirements marked `TBD` where necessary, compact `Research` references for investigations actually used, user-defined priority, dependencies, and `Blocked by`.
4. When invoked from approved external-work intake, add the compact provider-neutral `Sources` keys and stage the matching reverse provenance; otherwise use `—` and create no integration state.
5. Do not activate it or change active work.

When an approved feature is promoted from an investigation, update the INV to `outcome: promoted`, add the new Epic under Linked Work and Outcome History, and store the reciprocal research reference. Apply those references as one logical canonical update; the INV never approves the Epic.

Every retained future idea is an Epic; do not create a separate idea list.

## Update canonical target state

1. Show the exact proposed `SPEC.md` diff for new or changed target behavior, including `FR-*`, `NFR-*`, or `BR-*` acceptance criteria.
2. Apply it only after explicit user approval and update document approval metadata.
3. If architecture changes, show the `ARCHITECTURE.md` diff and proposed ADRs. Use the ADR Approval gate for significant decisions.
4. Regenerate `DECISIONS.md` from ADR frontmatter when ADRs change.
5. Change Epic readiness from `OUTLINE` to `READY` only after requirements, scope boundaries, acceptance direction, and dependencies are approved.

If the approved product or architecture change affects an existing planned or active workspace, show each affected plan and TASK diff and use the Replan gate before changing scope, order, or composition. Planned workspaces remain under `execution/planned/`; new TASK files remain `TODO` until their Epic passes Epic Start and each Task passes its own Task Start gate.

## Recheck priority and dependencies

Preserve user-defined priority and row order. Warn if the new Epic blocks earlier work, explain the impact, and ask before reordering. If the user preserves the order, keep blocked work `PLANNED` and record `Blocked by`.

Report the canonical changes and the next available gate. Do not start implementation or commit without the applicable explicit authorization.
