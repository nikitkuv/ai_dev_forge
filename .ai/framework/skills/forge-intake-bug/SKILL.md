---
name: forge-intake-bug
description: Classify and record a reported defect in an initialized Forge project. Use when a user finds incorrect behavior and the workflow must distinguish an unaccepted TASK regression from a new BUG in previously accepted code.
---

# Intake a Bug

## Establish the affected state

1. Read the reported behavior, relevant requirements, affected planned workspaces, active Epic and TASK files, user-validation history, accepted code history, and Git state.
2. Clarify reproduction conditions, expected behavior, actual behavior, impact, affected versions or environments, and available evidence.
3. Reproduce the problem consistently when local evidence permits. Capture exact commands, inputs, outputs, error messages, and environmental differences; if it is not reproducible, state the evidence gap instead of guessing.
4. Inspect relevant recent changes, data flow, component boundaries, dependencies, and similar working behavior. Trace the first point where observed behavior diverges from expected behavior.
5. Separate observations from hypotheses. Test one minimal root-cause hypothesis at a time using read-only inspection or reversible diagnostics, and record what supports or rejects it.
6. State the supported root cause, or the narrowest unresolved evidence gap, before proposing remediation.
7. Do not change product requirements merely to match the defect. If expected behavior is genuinely undecided, pause bug intake and use the product-change workflow.

Investigation before scheduling is read-only with respect to production code and tests. Any diagnostic instrumentation that changes tracked files requires an approved TASK and separate Task Start gate.

## Classify before allocating an ID

### Defect inside an unaccepted TASK

- Do not create a `BUG-ID`.
- Record the feedback in that TASK's User Validation and Iteration History.
- Return the TASK to `IN PROGRESS` through the orchestrator.
- Invalidate prior review and testing evidence after code changes.
- Repeat implementation, structured review, selected Task testing, and user acceptance. Full regression remains the Epic Validation gate.

### Defect in previously accepted code

1. Present the defect candidate and request explicit user approval to track it.
2. Allocate the next global `BUG-NNN`.
3. Add it to the Backlog Defect Queue as `OPEN`.
4. Record observable problem, impact severity, user-defined priority, related requirement, and no Scheduled TASK yet.

Severity describes consequences; priority belongs to the user.

## Decide scheduling without side effects

Present the available paths:

- add a repair TASK to the active Epic through the Replan gate;
- add a repair TASK to an existing compatible planned workspace through the Replan gate without activating it;
- create a separate `PLANNED/OUTLINE` Bugfix Epic;
- leave the Bug `OPEN`;
- reject, deduplicate, or mark it `WONT_FIX` after the user's decision.

Set the Bug to `SCHEDULED` only after a repair TASK is actually approved. Set it to `RESOLVED` only after that repair is explicitly accepted by the user.

Do not pause an active Epic, change priority, create a TASK, start work, or invoke external security scanning without explicit authorization. Return the recorded classification, evidence gaps, and next gate to the orchestrator.
