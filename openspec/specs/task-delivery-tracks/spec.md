# Task Delivery Tracks Specification

## Purpose

Defines two explicit, risk-bounded TASK delivery routes so small changes can be verified efficiently while materially risky work retains independent review and testing.

## Requirements

### Requirement: Forge exposes exactly two delivery tracks
Forge SHALL define exactly two TASK delivery tracks named `fast` and `standard`. A delivery track SHALL control assurance gates and agent routing independently from model tier, risk level, quality profile, and lifecycle status.

#### Scenario: Fast model does not imply fast delivery
- **WHEN** an agent uses the `fast` model tier for work on a `standard` TASK
- **THEN** the TASK retains every `standard` delivery gate

#### Scenario: Every approved TASK names a track
- **WHEN** an Epic plan and its TASK definitions are approved
- **THEN** each TASK records either `delivery_track: fast` or `delivery_track: standard` with a rationale

### Requirement: Fast selection is fail-closed
A TASK SHALL be eligible for `fast` only when its approved scope is bounded and reversible, its risk level is `low`, its expected behavior and verification are unambiguous, and no disqualifier is present. Disqualifiers SHALL include public-contract compatibility, authorization, security or privacy, persistence or data-format changes, schema or migration work, concurrency, shared-core behavior, dependency or production build changes, packaging or deployment behavior, runtime infrastructure, external integration contracts, critical user or system paths, test weakening, unresolved affected surface, and unresolved verification. Missing or uncertain eligibility evidence SHALL select `standard`.

#### Scenario: Small internal behavior is eligible
- **WHEN** a low-risk TASK changes bounded internal behavior, has no disqualifier, is reversible, and has deterministic focused verification
- **THEN** the planner may propose `delivery_track: fast` with criterion-by-criterion eligibility evidence

#### Scenario: Documentation-only change is eligible
- **WHEN** a bounded documentation-only TASK has no production effect and has deterministic link, format, or structure checks or a justified not-applicable check
- **THEN** the planner may propose `delivery_track: fast`

#### Scenario: Risk label alone is insufficient
- **WHEN** a TASK is labeled `low` but changes a public contract, migration, authorization rule, shared core, or another disqualified surface
- **THEN** Forge requires `delivery_track: standard`

#### Scenario: Eligibility is uncertain
- **WHEN** the planner or orchestrator cannot establish any fast-eligibility condition from current evidence
- **THEN** Forge selects `standard` without guessing or silently waiving the condition

### Requirement: Track selection is approved and revalidated
The proposed delivery track and its rationale SHALL be part of Plan Approval or Replan. At Task Start the orchestrator SHALL revalidate the selected track against current repository state, and after implementation it SHALL revalidate the track against the actual changed and affected surfaces before recording assurance.

#### Scenario: Approved fast track remains valid at Task Start
- **WHEN** the user authorizes Task Start and every approved fast criterion still matches current evidence
- **THEN** the orchestrator starts the TASK on the `fast` track

#### Scenario: Repository state invalidates fast before work
- **WHEN** a dependency, affected surface, baseline, or risk has changed so that approved fast eligibility is no longer true
- **THEN** the orchestrator blocks fast execution and requires track escalation through the applicable planning disposition

### Requirement: Fast uses implementer execution and orchestrator assurance
For a `fast` TASK, Forge SHALL invoke the implementer for the approved scope and SHALL retain focused RED/GREEN behavior evidence when TDD applies. After implementation, the orchestrator SHALL inspect the exact scoped diff, verify acceptance and affected-risk traceability, validate production/supporting path classification, confirm test integrity, run or reproduce every selected focused and scoped check, and record current orchestrator-assurance evidence bound to the implementation fingerprint. Forge SHALL NOT invoke the independent reviewer or separate tester for a `fast` TASK.

#### Scenario: Fast implementation passes assurance
- **WHEN** the implementation matches the approved fast scope, eligibility remains true, and every required focused and scoped check passes on the current fingerprint
- **THEN** the orchestrator records `PASSED` assurance and advances the TASK toward user acceptance without invoking reviewer or tester

#### Scenario: TDD is not applicable
- **WHEN** a fast TASK changes only documentation, generated evidence, or another approved surface for which behavior-first TDD is objectively not applicable
- **THEN** the orchestrator may accept a recorded not-applicable rationale while still requiring applicable deterministic checks

#### Scenario: Implementer evidence is not accepted on assertion alone
- **WHEN** the implementer reports passing checks but the orchestrator cannot reproduce the diff, fingerprint, command, or result
- **THEN** fast assurance fails and the TASK cannot advance

### Requirement: Standard preserves independent review and testing
A `standard` TASK SHALL follow implementer execution, independent production review, separate tester verification, user acceptance, and the existing evidence-freshness rules. Forge SHALL use `standard` whenever fast eligibility is absent, disqualified, uncertain, or invalidated.

#### Scenario: Standard implementation completes normally
- **WHEN** a standard implementation has a protocol-complete current `CLEAN` production review and current passing tester evidence
- **THEN** the orchestrator advances it to user acceptance under the existing standard lifecycle

#### Scenario: High risk selects standard
- **WHEN** a TASK has `standard` or `high` risk or any fast disqualifier
- **THEN** Forge requires the `standard` delivery track

### Requirement: Fast escalates automatically and cannot silently downgrade
If actual scope, affected surface, risk, test integrity, or verification violates fast eligibility at any point before acceptance, the orchestrator SHALL change the TASK to `standard`, record the trigger, invalidate fast assurance, and run every standard gate required for the current implementation. A TASK started as `standard` SHALL NOT downgrade to `fast`; changing its approved track before Task Start SHALL require Plan Approval or Replan.

#### Scenario: Actual production surface expands
- **WHEN** a fast implementation changes a disqualified path or affects an unapproved component or contract
- **THEN** the orchestrator escalates the TASK to `standard` before review and testing

#### Scenario: Focused check fails unexpectedly
- **WHEN** fast verification exposes an unexplained failure, missing coverage, or stale selection
- **THEN** the orchestrator returns the TASK to implementation and escalates it to `standard`

#### Scenario: Standard downgrade is attempted after start
- **WHEN** a standard TASK is already `IN PROGRESS` and a participant proposes skipping its independent gates
- **THEN** Forge rejects the downgrade and preserves the `standard` route

### Requirement: Lifecycle and completion are track-aware
A `fast` TASK SHALL move from `IN PROGRESS` directly to `AWAITING USER ACCEPTANCE` only after current passing orchestrator assurance. A `standard` TASK SHALL retain `IN REVIEW` and `IN TESTING`. Task completion, resume, evidence invalidation, and commit eligibility SHALL validate the evidence required by the recorded delivery track while preserving explicit Task Acceptance for both tracks.

#### Scenario: Fast task reaches user acceptance
- **WHEN** current fast assurance passes for the exact implementation fingerprint
- **THEN** the orchestrator transitions the TASK from `IN PROGRESS` to `AWAITING USER ACCEPTANCE`

#### Scenario: Fast task resumes with stale evidence
- **WHEN** a fast TASK is resumed and its recorded fingerprint does not match the current scoped implementation
- **THEN** prior assurance is stale and the orchestrator repeats eligibility validation and assurance before progression

#### Scenario: Fast task is accepted
- **WHEN** an eligible fast TASK has current passing assurance and the user explicitly accepts it
- **THEN** Forge may transition it to `DONE` and apply the configured post-acceptance Git policy

### Requirement: Epic assurance is unchanged by TASK track
Delivery-track selection SHALL NOT waive Epic Validation, the Epic fuzzing decision, aggregate fingerprint freshness, Epic Acceptance, or remediation requirements.

#### Scenario: Epic contains fast tasks
- **WHEN** all TASKs in an Epic are done and one or more used the fast track
- **THEN** Forge runs the same current aggregate Epic Validation and fuzzing gates required for an Epic containing only standard TASKs
