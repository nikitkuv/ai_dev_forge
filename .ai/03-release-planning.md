# Bootstrap Step 03 — Backlog Generation



---



## Purpose



The purpose of this step is to transform the product specification and system architecture into a structured development roadmap.



The primary output of this step is **BACKLOG.md**.



BACKLOG.md is the **project control document**.



It serves as the single source of truth for:



- the project's development roadmap;

- the list of Epics;

- Epic priorities;

- the current active Epic.



BACKLOG.md intentionally contains **no implementation details**.



Implementation planning is performed later inside the corresponding Epic workspace.



---



# Inputs



Required:



- BOOTSTRAP.md

- CONVENTIONS.md

- SPEC.md

- ARCHITECTURE.md



Optional:



- Existing repository

- Existing issue tracker

- Existing roadmap

- Existing backlog

- Existing TODO lists



---



# Core Principle



> BACKLOG.md defines **what should be built next**, not **how it will be built**.



---



# Overview



This step consists of five phases.



1. Analyze project scope.

2. Identify major work items.

3. Organize work into Epics.

4. Validate the roadmap.

5. Generate BACKLOG.md.



All phases are mandatory.



---



# Phase 1 — Analyze the Project



Review:



- SPEC.md

- ARCHITECTURE.md



Identify:



- product capabilities

- technical initiatives

- infrastructure work

- integrations

- future evolution



Focus on significant units of work.



Do NOT think about implementation.



---



# Phase 2 — Identify Epics



Identify every major development initiative.



Typical Epic categories include:



- product features

- infrastructure

- integrations

- refactoring

- testing improvements

- developer experience

- documentation



Each Epic should represent a meaningful milestone.



Do NOT decompose Epics into tasks.



---



# Phase 3 — Organize the Roadmap



Organize Epics into a development roadmap.



For each Epic define:



- ID

- Name

- Short description

- Priority

- Status



Recommended statuses:



- Planned

- Active

- Completed

- Blocked

- Cancelled



Exactly one Epic may be marked as **Active**.



If implementation has not started:



Active Epic = None.



Do NOT create implementation plans.



Do NOT estimate effort.



---



# Phase 4 — Validate the Roadmap



Present the proposed roadmap.



Summarize:



- project phases

- Epic ordering

- priorities

- active Epic (if any)



Ask the user:



> "Is this roadmap correct?"



Do NOT generate BACKLOG.md until approval.



If changes are requested:



- update the roadmap

- validate again if necessary



---



# Phase 5 — Generate BACKLOG.md



After approval:



Generate BACKLOG.md.



The document should contain:



- project overview

- current project status

- current active Epic

- Epic roadmap

- future ideas (optional)



BACKLOG.md should remain concise.



It is a navigation document, not a planning document.



Detailed planning belongs inside **execution/**.



---



# Recommended Structure of BACKLOG.md



## Project Overview



Short description.



---



## Project Status



Examples:



- Planning

- Active Development

- Maintenance

- Completed



---



## Current Active Epic



Exactly one Epic.



Example:



EPIC-003 — AI Agent Runtime



or



None



---



## Epic Roadmap



For each Epic:



- ID

- Name

- Description

- Priority

- Status



No task lists.



No implementation notes.



---



## Future Ideas (Optional)



Ideas intentionally excluded from the current roadmap.



---



## Notes (Optional)



Project-level planning notes.



---



# Restrictions



During this step, do NOT:



- create execution plans

- create TASK files

- create plan.md

- estimate work

- assign deadlines

- write production code

- duplicate SPEC.md

- duplicate ARCHITECTURE.md



---



# Definition of Done



This step is complete only if:



- all major work is organized into Epics;

- Epic priorities are defined;

- at most one Epic is marked as Active;

- the roadmap is approved by the user;

- BACKLOG.md is generated;

- BACKLOG.md contains no implementation details.



---



# Outputs



Create or update:



- BACKLOG.md



Do NOT create:



- execution/

- plan.md

- TASK files



Those belong to the next bootstrap step.



---



# Next Step



Recommend:



Bootstrap Step 04 — Execution Workspace Initialization



Do NOT proceed automatically.



Wait for user confirmation.



---



# End of Step

