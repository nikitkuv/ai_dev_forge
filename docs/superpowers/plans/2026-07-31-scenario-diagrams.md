# Scenario Diagrams Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create three self-contained, readable HTML diagrams for the framework scenarios.

**Architecture:** Each diagram is a standalone static HTML document with inline CSS and a small inline JavaScript helper for keyboard focus. The document carries the scenario-specific flow in semantic sections; CSS supplies a shared visual vocabulary without a build step or external dependencies.

**Tech Stack:** HTML5, inline CSS, minimal vanilla JavaScript.

## Global Constraints

- Source material: `scenarios/01-new-project.md`, `scenarios/02-existing-project.md`, `scenarios/03-development-pipeline.md`.
- Create the result files directly in `scenarios/`.
- No CDN, build step, or third-party dependency.
- Russian labels; user gates, artifacts, states, main flow, and return branches must be visually distinct.
- Layout must remain usable on narrow viewports and honor `prefers-reduced-motion`.

---

### Task 1: Diagram of a new project bootstrap

**Files:**
- Create: `scenarios/01-new-project-diagram.html`
- Test: browser/open-file structural check

**Interfaces:**
- Consumes: `scenarios/01-new-project.md`
- Produces: standalone HTML page for the new-project path.

- [ ] **Step 1: Add the document frame**

Create UTF-8 HTML with Russian `title`, a page heading, an inline legend, and a responsive `<main>` flow container.

- [ ] **Step 2: Encode the flow**

Represent initial request, bootstrap configuration, Product Discovery, System Design, Release Planning, platform adaptation, validation, and ready state. Put `SPEC`, `ARCHITECTURE`, ADR, `BACKLOG`, adapters, and framework lock in artifact labels. Mark approvals as user gates.

- [ ] **Step 3: Add return paths and responsive style**

Use clear dashed connectors and labels for corrections before approvals; include mobile stacking and reduced-motion rules.

- [ ] **Step 4: Verify structure**

Run: `Select-String -LiteralPath 'scenarios/01-new-project-diagram.html' -Pattern '<!doctype html>|<title>|Product Discovery|SPEC|ARCHITECTURE|BACKLOG'`

Expected: every required marker is present.

### Task 2: Diagram of an existing project bootstrap

**Files:**
- Create: `scenarios/02-existing-project-diagram.html`
- Test: browser/open-file structural check

**Interfaces:**
- Consumes: `scenarios/02-existing-project.md`
- Produces: standalone HTML page for the existing-project path.

- [ ] **Step 1: Add the document frame and legend**

Create a self-contained UTF-8 page using the same semantic class names as Task 1 but an independent accent palette.

- [ ] **Step 2: Encode migration-specific steps**

Show intake, preflight, legacy-context collection, migration plan/diff, explicit confirmation, canonical documents and adapter sync, then validation. Distinguish existing inputs from newly-created canonical documents.

- [ ] **Step 3: Add safeguards**

Make collision handling, low-confidence/context gaps, and user approval visible as return or stop branches. Add mobile and reduced-motion rules.

- [ ] **Step 4: Verify structure**

Run: `Select-String -LiteralPath 'scenarios/02-existing-project-diagram.html' -Pattern '<!doctype html>|<title>|migration|legacy|approval|validation'`

Expected: every required marker is present.

### Task 3: Diagram of the full development pipeline

**Files:**
- Create: `scenarios/03-development-pipeline-diagram.html`
- Test: browser/open-file structural check

**Interfaces:**
- Consumes: `scenarios/03-development-pipeline.md`
- Produces: standalone HTML page for the Epic/TASK lifecycle.

- [ ] **Step 1: Add the document frame and state legend**

Create a standalone page with a compact legend for TASK states, gates, actors, and artifacts.

- [ ] **Step 2: Encode the primary TASK lifecycle**

Show Task Start → IN PROGRESS → IN REVIEW → IN TESTING → AWAITING USER ACCEPTANCE → DONE. Draw review findings and failed testing back to IN PROGRESS, and differentiate a scope change that goes to the Replan gate.

- [ ] **Step 3: Encode Epic completion and side paths**

Show final TASK → read-only fuzzing → Epic Acceptance → COMPLETED. Add concise cards for feature intake, bug intake, reprioritization, pause/resume, and explicitly requested security audit.

- [ ] **Step 4: Verify structure**

Run: `Select-String -LiteralPath 'scenarios/03-development-pipeline-diagram.html' -Pattern '<!doctype html>|IN PROGRESS|IN REVIEW|IN TESTING|FUZZING|Epic Acceptance|Replan'`

Expected: every required marker is present.

### Task 4: Cross-file quality check

**Files:**
- Test: `scenarios/*-diagram.html`

**Interfaces:**
- Consumes: three generated HTML files.
- Produces: verification evidence for delivery.

- [ ] **Step 1: Check file presence and external references**

Run: `Get-ChildItem scenarios -Filter '*-diagram.html' | Select-Object Name,Length; Select-String -Path 'scenarios/*-diagram.html' -Pattern 'https?://|<script[^>]+src=|<link[^>]+href='`

Expected: three files with nonzero length; the reference scan returns no matches.

- [ ] **Step 2: Inspect opening markup**

Run: `Get-Content 'scenarios/01-new-project-diagram.html','scenarios/02-existing-project-diagram.html','scenarios/03-development-pipeline-diagram.html' -TotalCount 4`

Expected: all documents begin with `<!doctype html>` and use UTF-8 metadata.
