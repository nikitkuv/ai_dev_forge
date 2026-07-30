# Bootstrap Step 03 — Release Planning

## Purpose

Create an approved `BACKLOG.md` containing the Epic Roadmap and Defect Queue. This step decides what should be delivered and in what user-controlled order; it does not create execution plans or Tasks.

Use `.ai/templates/BACKLOG.md`, `.ai/CONVENTIONS.md`, and lifecycle values from `.ai/framework/contracts.yaml`.

## Preconditions and Inputs

Required:

- approved `SPEC.md`;
- approved `ARCHITECTURE.md`;
- resolved ADRs relevant to planning;
- the Backlog template and framework contracts.

Optional evidence includes existing roadmaps, issue trackers, TODO material, code findings, test gaps, and user-provided features or defects. Existing-project findings remain candidates until the user confirms whether to retain them.

## Build the Candidate Roadmap

1. Trace required product outcomes to `FR-*`, `NFR-*`, and `BR-*`.
2. Group meaningful product, architecture, migration, infrastructure, quality, integration, or documentation outcomes into Epics.
3. Represent every retained future idea as an Epic; do not create a separate idea list.
4. Allocate globally unique `EPIC-NNN` identifiers without reusing gaps.
5. Give every new Epic lifecycle `PLANNED`.
6. Use readiness:
   - `OUTLINE` when requirements, boundaries, or dependencies are unresolved;
   - `READY` only when requirements, scope boundaries, acceptance direction, and dependencies are approved.
7. Do not activate an Epic in this step. Epic activation belongs to the separate Epic Start gate in Step 04.

Do not decompose Epics into Tasks or estimate implementation effort.

## Build the Defect Queue

1. Present candidate defects found in code, tests, documents, issues, or user reports.
2. Add a defect only after the user confirms it should be tracked.
3. Allocate the next global `BUG-NNN`.
4. Record impact severity separately from user repair priority.
5. Use the lifecycle defined in `.ai/framework/contracts.yaml`.
6. Leave Scheduled TASK empty until an approved planning workflow actually creates the repair Task.

A failure inside unaccepted work stays with that Task and is not added as a separate defect.

## Priority, Order, and Dependencies

The user owns the **user-defined priority** (`P0`–`P3`) and row order within each priority.

The agent must:

1. build a dependency graph across Epics and relevant external or decision dependencies;
2. compare that graph with the user's proposed order;
3. warn when a later Epic blocks an earlier Epic;
4. explain the impact and propose a concrete reorder;
5. ask whether the user wants to change the order;
6. reorder only after explicit confirmation.

If the user preserves the conflicting order, keep the earlier Epic `PLANNED` and record the dependency in `Blocked by`. Blocking is metadata, not a lifecycle status.

## Draft and Approval Workflow

1. Present the proposed Epic Roadmap, requirement coverage, readiness, dependency warnings, priorities, ordering, and candidate Defect Queue.
2. Resolve which candidates should be retained.
3. Create or update `BACKLOG.md` from the template with `document_status: draft`.
4. Request explicit user approval of the complete roadmap and defect queue.
5. Only after approval, set `document_status: approved` and `approved_at`.

The agent must not change user priority, order, scope, or retained items silently.

## Completion Gate

This step is complete only when:

- every retained future idea is a `PLANNED` Epic;
- every `READY` Epic has approved requirements, boundaries, and dependencies;
- unresolved work remains `OUTLINE`;
- dependency conflicts were shown and any reorder was explicitly approved;
- confirmed defects are separate from Epics and use the Defect Queue;
- `BACKLOG.md` has explicit user approval and is marked `approved`;
- no plan, Task file, execution directory, or active Epic was created.

Do not start Step 04 automatically. Report the result and request a separate user confirmation.

## Output

- `BACKLOG.md`
