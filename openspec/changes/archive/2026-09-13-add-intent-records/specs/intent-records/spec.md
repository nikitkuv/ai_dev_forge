## Purpose

Captures the narrative of product requests (motivation, constraints, alternatives, open questions) as durable, bounded evidence records that survive session loss, feed Epic planning, and preserve rejected ideas for dedup — without becoming a source of lifecycle state.

## ADDED Requirements

### Requirement: Every material product request has one canonical intent record

Forge SHALL allocate a monotonic global `INT-NNNN` identifier for every material feature, product-change, or external-work request and store one document at `intents/INT-NNNN-<short-name>.md`. The identifier SHALL be reserved as the first durable action of intake, before any Backlog row or canonical change. The record SHALL contain, in the user's own words where possible: problem and motivation, proposed observable outcome, affected users or systems, constraints, considered alternatives with rejection reasons, open questions, and outcome history. The record SHALL be bounded to approximately one page and MUST NOT duplicate approved requirement criteria or implementation strategy.

#### Scenario: User states a feature request

- **WHEN** the user describes a desired feature or product change to the orchestrator
- **THEN** Forge reserves the next `INT-NNNN`, creates the draft intent record, and only then proceeds to interview and Backlog retention

#### Scenario: Session dies mid-intake

- **WHEN** the conversation is interrupted after the intent record was created but before retention approval
- **THEN** the recorded problem, outcome, constraints, and open questions remain available on disk and a later session resumes intake from the record instead of re-deriving context from chat history

#### Scenario: Record stays bounded

- **WHEN** an intent record grows toward duplicating requirement criteria or implementation planning
- **THEN** Forge moves that content to `SPEC.md` through the existing approval gate or to the Epic plan, and keeps in the intent record only the narrative sections and references

### Requirement: Intent capture uses a proportionate interview

Forge SHALL fill the intent template by interviewing the user only about missing or ambiguous sections, deriving what it can from repository evidence, `SPEC.md`, and linked investigations without re-asking. The finalized record SHALL be presented to the user for explicit confirmation before Backlog retention. Interview depth SHALL be proportionate to the size of the request.

#### Scenario: Vague request

- **WHEN** the user states an idea without outcome, affected systems, or constraints
- **THEN** the orchestrator asks targeted questions until every template section is concrete enough to plan against, and records answers in the intent record

#### Scenario: Well-specified request

- **WHEN** the user's request already fixes the outcome, scope, and constraints
- **THEN** the orchestrator fills the remaining sections from repository evidence and asks only for confirmation of the assembled record

### Requirement: Rejected, deferred, and superseded requests are retained

Every intent record SHALL carry exactly one current `outcome`: `draft`, `accepted`, `promoted`, `rejected`, `deferred`, or `superseded`. A `rejected` record SHALL include a short rationale and MUST NOT create or modify any Backlog row. Outcome transitions SHALL be preserved in an outcome history with dates inside the record. Intent records SHALL NOT be deleted when their request is implemented, rejected, or superseded.

#### Scenario: Idea dies in conversation

- **WHEN** the user discusses a request and decides not to pursue it
- **THEN** the intent record remains with `outcome: rejected` and a one-line rationale, and no Epic is created

#### Scenario: Deferred idea is resurrected

- **WHEN** a request previously recorded as `deferred` is raised again and accepted
- **THEN** the same intent record moves to `accepted`, appending the transition to its outcome history instead of creating a duplicate record

#### Scenario: Repeat request is recognized

- **WHEN** a new request materially matches an earlier rejected or deferred intent
- **THEN** Forge surfaces the prior record and its rationale before creating a new one

### Requirement: Intent records are evidence, not lifecycle state

An intent record MUST NOT control priority, readiness, lifecycle status, acceptance, or commit permission. Approved requirement criteria SHALL exist only in `SPEC.md`; implementation strategy SHALL exist only in the Epic plan. The Backlog Epic Roadmap MAY link an intent through an optional `Intent` column; Backlogs without the column SHALL remain valid.

#### Scenario: Intent without retention

- **WHEN** an intent record exists but the user never approves retaining the idea
- **THEN** Backlog, execution state, and all gates remain unchanged

#### Scenario: Existing project without intents

- **WHEN** a project predating this capability has no `intents/` folder and no `Intent` column
- **THEN** all existing workflows, validations, and lifecycle transitions remain valid without backfill

### Requirement: Planning consumes the linked intent

`forge-prepare-epic` SHALL read the intent record linked from the Epic row as a primary planning input alongside `SPEC.md`, using its motivation, constraints, and alternatives to shape the Epic plan. An Epic SHALL NOT move from `OUTLINE` to `READY` while its linked intent record contains unresolved open questions.

#### Scenario: Planning months after intake

- **WHEN** the planner prepares an Epic whose request was recorded months earlier
- **THEN** the intent record supplies the motivation, constraints, and rejected alternatives, and the planner does not require the user to restate them

#### Scenario: Open questions block readiness

- **WHEN** a linked intent record still lists material open questions
- **THEN** readiness remains `OUTLINE` until the questions are resolved and the record updated

### Requirement: Tooling allocates and validates intent records

Local tooling SHALL allocate `int` identifiers monotonically through the existing next-id mechanism and SHALL structurally validate intent records: required frontmatter, allowed outcome values, a `promoted_to` target that exists when set, and `research_refs` that resolve to existing investigations. Validation findings SHALL be advisory evidence for the orchestrator and MUST NOT mutate records.

#### Scenario: Identifier allocation

- **WHEN** two intake conversations reserve intent identifiers in sequence
- **THEN** tooling returns strictly increasing `INT-NNNN` values without reuse

#### Scenario: Malformed record is detected

- **WHEN** an intent record has an unknown outcome value or references a missing investigation
- **THEN** validation reports the exact record and problem without modifying it
