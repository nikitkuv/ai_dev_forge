# Bootstrap Step 04 — Execution Workspace Initialization

---

## Purpose

The purpose of this step is to initialize the execution workspace for the current development cycle.

This step transforms the selected Epic into an executable workspace that AI coding agents can use for day-to-day development.

The primary outputs of this step are:

- execution/
- the active Epic workspace
- plan.md
- atomic task files

After completing this step, the repository is ready for implementation.

---

# Inputs

Required:

- BOOTSTRAP.md
- CONVENTIONS.md
- SPEC.md
- ARCHITECTURE.md
- BACKLOG.md

---

# Core Principle

> BACKLOG defines **what should be built**.

> execution defines **what is being built now**.

---

# Overview

This step consists of five phases.

1. Select the active Epic.
2. Initialize the execution workspace.
3. Create the Epic implementation plan.
4. Decompose the Epic into atomic tasks.
5. Validate the workspace.

All phases are mandatory.

---

# Phase 1 — Select the Active Epic

Read BACKLOG.md.

Locate the Epic marked as **Active**.

Rules:

- exactly one Active Epic must exist;
- if none exists, ask the user;
- if multiple Active Epics exist, report the inconsistency and stop.

Do not continue until a single Active Epic has been identified.

---

# Phase 2 — Initialize the Execution Workspace

Create the following structure if it does not already exist:

```text
execution/
&#x20;   active/
&#x20;       EPIC-001-<short-name>/
&#x20;           plan.md
&#x20;           tasks/
&#x20;   completed/
docs/                      # may start empty (.gitkeep)
references/                # may start empty (.gitkeep)
```

The Epic folder name MUST exactly match the Epic name in BACKLOG.md and follow the canonical naming (`EPIC-NNN-<short-name>`, see CONVENTIONS.md).

`docs/` and `references/` are part of the standard project layout. Create them during this step even if empty (use a `.gitkeep` file so empty directories are tracked by version control). They are filled later, on demand.

If the workspace already exists:

- preserve existing progress;
- do not overwrite existing files unless explicitly requested.

---

# Phase 3 — Create plan.md

Generate the implementation plan for the active Epic.

The purpose of plan.md is to define **how this Epic will be executed**, not how individual pieces of code will be written.

The plan should include:

- Epic objective
- expected outcome
- implementation strategy
- dependencies
- technical risks
- ordered task sequence
- Epic Definition of Done
- current execution status

The plan should remain stable even if implementation details change.

---

## Recommended Structure of plan.md

- Epic Overview
- Objective
- Expected Outcome
- Dependencies
- Risks
- Implementation Strategy
- Task Sequence
- Epic Definition of Done
- Current Status

---

# Phase 4 — Create Atomic Tasks

Decompose the Epic into small implementation tasks.

Each task should:

- have a single responsibility;
- produce one logical outcome;
- be independently testable;
- preferably fit within a single development session;
- have explicit completion criteria.

Create one Markdown file per task.

Store them in:

```text
execution/
&#x20;   active/
&#x20;       EPIC-001-<short-name>/
&#x20;           tasks/
&#x20;               TASK-001-<short-name>.md
```

File naming follows the canonical convention (`TASK-NNN-<short-name>.md`, see CONVENTIONS.md).

---

## Recommended Task Structure

Each task document should include:

- Status — one of `TODO` / `IN PROGRESS` / `DONE` / `BLOCKED` / `CANCELLED` (see CONVENTIONS.md)
- Goal
- Context
- Scope
- Constraints
- Acceptance Criteria
- Progress
- Notes

Status rule: **at most one** task is `IN PROGRESS` per active Epic. That task is the "current task". To start a task, set it to `IN PROGRESS`; to finish, set it to `DONE`.

Tasks describe **work**, not code.

Do not write implementation details.

Do not implement the task.

---

# Phase 5 — Validate the Workspace

Verify:

- execution/ exists;
- exactly one Active Epic exists;
- the Epic folder name matches the canonical convention and BACKLOG.md;
- plan.md exists;
- task files exist and follow the canonical `TASK-NNN-<short-name>.md` naming;
- every task belongs to the Active Epic;
- every task has a Status field with a valid value;
- at most one task is `IN PROGRESS`;
- task ordering matches the implementation strategy;
- `docs/` and `references/` exist (empty is acceptable).

If inconsistencies are found:

Report them before continuing.

---

# Restrictions

During this step, do NOT:

- implement production code;
- modify source code;
- write tests;
- create future Epic workspaces;
- activate additional Epics;
- generate documentation unrelated to execution.

This step prepares the workspace only.

---

# Definition of Done

This step is complete only if:

- execution/ has been initialized;
- the Active Epic workspace exists;
- plan.md has been generated;
- the Epic has been decomposed into atomic tasks;
- every task has its own Markdown document;
- the execution workspace is ready for implementation.

---

# Outputs

Create (if necessary):

```text
execution/
execution/active/
execution/completed/
execution/active/EPIC-001-<short-name>/
execution/active/EPIC-001-<short-name>/plan.md
execution/active/EPIC-001-<short-name>/tasks/
execution/active/EPIC-001-<short-name>/tasks/TASK-001-<short-name>.md
execution/active/EPIC-001-<short-name>/tasks/TASK-002-<short-name>.md
...
docs/                       # empty if nothing yet (.gitkeep)
references/                 # empty if nothing yet (.gitkeep)
```

Do not modify source code.

---

# Next Step

Recommend:

Bootstrap Step 05 — Create AI Environment

Do NOT proceed automatically.

Wait for user confirmation.

---

# End of Step
