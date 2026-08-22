## Purpose

Define how heterogeneous records from a configured external work source become traceable Forge work candidates while canonical project documents and existing approval gates retain lifecycle authority.

## ADDED Requirements

### Requirement: Explicit and queue-based ticket retrieval
Forge SHALL support external-work intake for explicitly identified records and for a candidate collection selected by configured source filters. A queue-based request MUST report the applied integration, source scope, filters, source ordering, and retrieved candidate set before recommending work.

#### Scenario: User names one external ticket
- **WHEN** the user requests intake for a specific ticket in a configured source
- **THEN** Forge retrieves that ticket and the minimum related metadata needed for classification

#### Scenario: User asks for the next board work
- **WHEN** the user asks Forge to inspect a configured board without naming a ticket
- **THEN** Forge retrieves the configured candidate collection, reports its source ordering and filters, and recommends candidates without silently changing Backlog priority or starting work

#### Scenario: Retrieval is partial
- **WHEN** pagination, permissions, connector errors, or source limits make the candidate set incomplete
- **THEN** Forge marks the result incomplete, reports the known boundary, and MUST NOT claim that its recommendation covers the full configured queue

### Requirement: Normalized work-item evidence
Forge SHALL normalize each retrieved record into a source-neutral work item containing at least integration ID, external stable ID, title, description, source reference, retrieval time, available version/update marker, labels, and relationship data. Missing or conflicting fields MUST be reported as evidence gaps rather than inferred as confirmed intent.

#### Scenario: Ticket contains a detailed specification
- **WHEN** a ticket has a title, description, labels, and attachments or linked records available through declared read operations
- **THEN** Forge presents the normalized evidence and distinguishes source facts from its own scope assumptions

#### Scenario: Ticket is underspecified
- **WHEN** a ticket contains only a brief title such as `Проверить работает ли отсечка по площади`
- **THEN** Forge investigates relevant canonical and repository evidence and asks for any material product decision that the ticket and code cannot resolve

### Requirement: Intent and granularity classification precedes canonical changes
Forge MUST classify each normalized record as a possible defect, investigation, product change, duplicate, rejected item, or unresolved candidate and MUST determine the appropriate Forge decomposition before editing canonical state. A source ticket MUST NOT automatically become a standalone TASK or establish an Epic boundary.

#### Scenario: Small ticket fits an existing Epic
- **WHEN** a small ticket is compatible with an existing planned or active Epic and its approved outcome
- **THEN** Forge proposes it as a TASK or scope-change candidate through the applicable Plan Approval or Replan gate and does not insert it directly into execution state

#### Scenario: Small ticket describes accepted-code failure
- **WHEN** investigation supports that a ticket reports incorrect behavior in previously accepted code
- **THEN** Forge hands the candidate to the existing bug-intake classification and approval workflow before allocating a `BUG-*` or scheduling repair work

#### Scenario: Large ticket spans multiple outcomes
- **WHEN** a ticket such as `Создать модуль Рекомендации по бурению` contains independently deliverable outcomes or unresolved architecture boundaries
- **THEN** Forge proposes multiple ordered Epics when that decomposition best preserves observable outcomes, dependencies, and reviewable scope

#### Scenario: Related tickets form one outcome
- **WHEN** multiple tickets describe parts of one coherent user outcome
- **THEN** Forge may propose one Epic sourced by all of them and explains why combining them is preferable to separate Epics

### Requirement: Proposed decomposition is reviewable
Before retaining external work, Forge SHALL present a reviewable intake proposal that maps every selected external record to its proposed disposition, resulting Bug or Epic candidates, relevant requirements and repository areas, dependencies, assumptions, unresolved decisions, and rationale for splitting or combining. Records MUST NOT disappear from the proposal merely because they were grouped or judged duplicates.

#### Scenario: One ticket becomes several Epics
- **WHEN** Forge proposes a one-to-many decomposition
- **THEN** the proposal shows which part of the source ticket each Epic covers and identifies cross-Epic dependencies or deliberately deferred scope

#### Scenario: Several tickets become one Epic
- **WHEN** Forge proposes a many-to-one grouping
- **THEN** the proposal lists every source ticket, overlap or complementarity, duplicate scope, and the combined observable outcome

### Requirement: Existing Forge gates remain authoritative
External-work intake SHALL hand approved candidates to the existing feature-intake, bug-intake, release-planning, Replan, Plan Approval, Epic Start, and Task Start contracts as applicable. Retrieval, source-board status, labels, or a ticket author's wording MUST NOT count as canonical approval, Task Start, Epic Start, Task Acceptance, or Epic Acceptance.

#### Scenario: User approves retaining a proposed feature
- **WHEN** the user approves the intake decomposition and exact canonical change
- **THEN** Forge creates or updates the applicable requirements, architecture decisions, Backlog entries, plans, or TASK definitions only through their existing gates

#### Scenario: Board marks a ticket ready or in progress
- **WHEN** an external record's state implies that work is ready, approved, or started
- **THEN** Forge records that state as source evidence but derives Forge readiness and lifecycle status only from canonical project state and explicit Forge gates

### Requirement: Stable provenance and duplicate prevention
Forge SHALL maintain project-owned provenance that maps a source integration and external stable ID to its latest approved disposition and any canonical Forge IDs. Approved Epics and Bugs in `BACKLOG.md` and approved Tasks in `execution/` MUST also carry compact external source references, so the agent can traverse the relationship from either the external ticket or the current Forge work item. Provenance MUST be sufficient to detect repeated intake, one-to-many decomposition, many-to-one grouping, and source updates without making the external system authoritative for Forge lifecycle state.

#### Scenario: Previously retained ticket is fetched again unchanged
- **WHEN** a normalized record matches an existing provenance identity and content/version marker
- **THEN** Forge reports its current canonical mappings and does not create duplicate Bugs, Epics, or Tasks

#### Scenario: Previously retained ticket changed
- **WHEN** the same external identity has a newer version or different content fingerprint
- **THEN** Forge shows the source delta, checks affected canonical scope, and requires the applicable intake or Replan approval before changing it

#### Scenario: Ticket was explicitly rejected or deferred
- **WHEN** a previously reviewed record is fetched again
- **THEN** Forge reports its recorded disposition and asks before reconsidering it, unless the source change invalidates the prior decision

#### Scenario: Epic planning creates Tasks for an external ticket
- **WHEN** an approved Epic linked to one or more external tickets receives an approved plan and TASK definitions
- **THEN** Forge records which external tickets each TASK covers, updates the reverse provenance mapping, and preserves the Epic-level source links

#### Scenario: One Task covers several tickets
- **WHEN** one approved TASK implements a coherent slice sourced from multiple external tickets
- **THEN** the TASK identifies every source reference and the provenance mapping points each ticket to that TASK without duplicating the TASK

### Requirement: Source relationships are available throughout the lifecycle
Forge SHALL load and reconcile external source relationships whenever it recovers development state, prepares or replans an Epic, starts or runs a linked TASK, validates an Epic, or reports current work. The agent MUST distinguish source coverage from lifecycle status and MUST report broken, missing, or contradictory links before continuing through a gate that depends on them.

#### Scenario: Agent resumes development on linked work
- **WHEN** the agent reconstructs a project containing an active or planned Epic with external source references
- **THEN** it reports the Epic's linked tickets, each TASK's ticket coverage, any source items not yet covered by a TASK, and any stale or broken provenance links

#### Scenario: Replan changes ticket coverage
- **WHEN** an approved Replan adds, removes, splits, combines, or reorders Tasks associated with external tickets
- **THEN** Forge updates TASK source references and the provenance mapping in the same validated logical transition while preserving historical source identity

#### Scenario: Canonical and provenance mappings disagree
- **WHEN** a Backlog or TASK source reference disagrees with the project-owned provenance ledger
- **THEN** Forge blocks relationship-dependent planning or execution, treats canonical lifecycle state as authoritative, and requests or performs only an explicitly approved reconciliation

#### Scenario: Forge is upgraded with linked work in progress
- **WHEN** the framework is upgraded while planned, active, paused, or completed work has external source relationships
- **THEN** the upgrade preserves the source keys, Backlog references, TASK frontmatter, plan coverage matrix, and reverse mappings without changing Forge or external lifecycle state

#### Scenario: Framework rollback follows an upgrade
- **WHEN** a framework upgrade or separately approved integration-schema migration is rolled back
- **THEN** Forge restores a mutually compatible relationship representation or blocks relationship-dependent work with explicit recovery instructions, without deleting the external identities or canonical Epic, Bug, and Task records

### Requirement: Intake uses a current source snapshot
Forge MUST re-read selected external records before applying an approved canonical diff when the source exposes a version/update marker or when the intake session no longer has current evidence. If the material source content changed, Forge MUST invalidate the stale proposal and present an updated decomposition.

#### Scenario: Ticket changes during review
- **WHEN** a selected ticket's description, labels, relationships, or other material fields change after the proposal was prepared
- **THEN** Forge does not apply the stale canonical diff and instead presents the detected change for renewed review

### Requirement: Intake failures are atomic with respect to project state
A failed retrieval, normalization, classification, provenance update, or canonical validation MUST NOT leave partial new canonical identities or misleading provenance mappings. Forge SHALL report which external records were inspected, which stage failed, and whether any approved writes occurred.

#### Scenario: Provenance persistence fails after approval
- **WHEN** Forge cannot persist the source-to-canonical mapping as part of an approved intake change
- **THEN** it restores the affected intake state to the prior consistent form or stops before canonical changes, and reports the work as not retained

#### Scenario: One record in a grouped proposal becomes unavailable
- **WHEN** a selected source record cannot be revalidated before applying a many-to-one proposal
- **THEN** Forge leaves the canonical state unchanged and asks whether to retry, remove that record through a revised proposal, or cancel the intake
