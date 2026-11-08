# agent-knowledge-reuse Specification

## Purpose

Enable agents to reuse verified experience across sessions while retaining canonical source ownership, bounded context, explicit uncertainty and compatibility with existing Forge records.

## Requirements

### Requirement: Findings are optional evidence attached to existing records

TASK and INV records SHALL support optional reusable findings with a stable record-local identifier, claim, applicability, evidence references, validation status, verification date or revision, and recheck conditions. Status SHALL be `hypothesis`, `verified`, or `obsolete`. A verified finding MUST have supporting evidence; repeated assertion alone SHALL NOT establish verification. Successful strategies, constraints and failed approaches SHALL all be eligible. Agents SHALL record only materially reusable knowledge, not readily reconstructible lifecycle state or routine activity. Missing findings SHALL NOT block any lifecycle gate or require backfill.

#### Scenario: Successful work reveals a reusable constraint
- **WHEN** a completed experiment supports a component constraint useful beyond the current task
- **THEN** the agent records a bounded finding in the owning TASK or INV with evidence and scope, within existing write authority
- **AND** no separate memory document or acceptance gate is created

#### Scenario: Speculation and legacy records
- **WHEN** an explanation has not been tested or an old TASK has no findings
- **THEN** the explanation remains a hypothesis and the old TASK proceeds unchanged
- **AND** neither condition is interpreted as a verified rule or a lifecycle failure

### Requirement: Relevant workflows check prior experience within a bounded scope

Investigation, Epic preparation, feature/external intake, bug intake for accepted-code defects, Task execution and resume with a concrete unresolved question SHALL check relevant prior experience. Explicit references SHALL be read first and SHALL satisfy the check when sufficient. Otherwise, available local search SHALL include relevant research, decisions, completed execution records and historical defects, rather than restricting all planning to INV/ADR. No-history and unavailable-search cases SHALL use explicit references and local file discovery without implying search coverage. This check SHALL add no approval gate and SHALL NOT run on every turn.

#### Scenario: Prior Task contains the useful experience
- **WHEN** an Epic concerns a component whose relevant failure was recorded only in a completed TASK
- **THEN** the experience check includes that record kind and reads the relevant canonical candidate before planning

#### Scenario: Links already answer the question
- **WHEN** linked records supply sufficient current evidence for the same unchanged task scope
- **THEN** the agent reuses those records without an obligatory duplicate query

#### Scenario: Search is unavailable
- **WHEN** Python or full-text search support is unavailable
- **THEN** the agent reports the limitation, uses bounded local discovery and continues the existing workflow without installing dependencies or claiming complete recall

### Requirement: Mechanical freshness and semantic applicability remain distinct

Selected findings SHALL be checked against recorded dependencies and assumptions before factual reuse. A deterministic check SHALL report `unchanged`, `changed`, or `unknown` for declared local inputs without executing evidence commands. Changed, missing, unreadable or incomplete dependency evidence SHALL require focused revalidation before the finding is treated as current. Unchanged inputs SHALL NOT be presented as proof of truth or dependency completeness. Conflicts with current authoritative sources SHALL be reported and SHALL NOT be silently resolved by memory. Hypotheses SHALL be usable as labeled experiment candidates only; obsolete findings SHALL NOT be current factual premises.

#### Scenario: Indexed note is current but its dependency changed
- **WHEN** a finding's text is unchanged and its recorded dependency file changed
- **THEN** the check reports changed applicability inputs and the agent revalidates the affected claim before relying on it

#### Scenario: Dependency evidence is incomplete
- **WHEN** a finding relies on an unrecorded environment version or an unavailable evidence source
- **THEN** the check reports unknown where applicable and the agent does not infer current verification from an unchanged source note

#### Scenario: Historical claim contradicts an accepted decision
- **WHEN** retrieved experience conflicts with the current SPEC or ADR
- **THEN** the agent reports the conflict, follows canonical authority and does not turn the old finding into a new instruction

### Requirement: Reused experience carries provenance through handoff

The orchestrator SHALL select only task-relevant findings for an agent assignment, preserving source references, applicability and uncertainty. When experience materially informs current work, the receiving TASK, plan, INV or INT SHALL retain compact references and the reuse rationale in its existing context/reference sections within normal write authority. References to record-local findings SHALL resolve by record identity without assuming execution directory paths remain unchanged. Existing INV reciprocal research references SHALL remain required where applicable. Search snippets SHALL NOT substitute for reading sources or satisfy review/testing gates.

#### Scenario: Scoped handoff
- **WHEN** prior experience changes the verification approach for a new TASK
- **THEN** the implementer receives the applicable conclusion, its evidence reference and limits, and the TASK records the source of that choice

#### Scenario: Epic moves to completed
- **WHEN** a source TASK moves between execution directories without changing identity
- **THEN** its recorded finding references still resolve or are repaired through existing identity/link mechanisms without changing the finding identity

### Requirement: Agent evaluations test usefulness and harmful reuse

The project SHALL provide fresh-session scenarios for rediscovery, successful-strategy transfer, changed dependencies, conflicting records, irrelevant experience and no-history fallback. Evaluation SHALL compare a recorded pre-change workflow baseline, retrieval with applicability checks, and retrieval after bounded consolidation using matched task/model settings. It SHALL report task outcomes, repeated mistakes, unnecessary investigation, retrieved and used sources, available usage and consolidation cost. Missing measurements SHALL remain unknown. Synthetic context-size reduction alone SHALL NOT be reported as evidence of improved agent performance.

#### Scenario: Expensive memory with no quality improvement
- **WHEN** consolidation increases total measured cost without improving evaluated outcomes
- **THEN** the readout exposes that trade-off rather than reporting success from smaller foreground prompts alone

#### Scenario: Wrong historical shortcut
- **WHEN** a scenario supplies a plausible but invalidated historical finding
- **THEN** evaluation checks that the agent detects or revalidates it rather than rewarding mere retrieval
