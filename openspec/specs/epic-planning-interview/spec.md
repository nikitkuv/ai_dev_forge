# Epic Planning Interview Specification

## Purpose

Makes epic planning a staged interview where the human approves the epic's interface step by step before the planner fills in implementation details, so wrong directions are caught on small artifacts instead of a finished plan.

## Requirements

### Requirement: Epic preparation proceeds as a staged interview with confirmation gates

Epic preparation SHALL proceed through stages — objective and expected outcome, interface design, risks and critical paths, decomposition skeleton — where each stage's artifact is presented for user confirmation before the next stage begins. A stage rejected by the user SHALL be revised and re-confirmed before later stages proceed.

#### Scenario: Stage confirmed before proceeding
- **WHEN** the interface-design stage produces its artifact
- **THEN** the artifact is presented for user confirmation and the decomposition stage does not begin before that confirmation

#### Scenario: Rejected stage is revised first
- **WHEN** the user rejects a stage artifact
- **THEN** that stage is revised and re-confirmed while later stages remain untouched

### Requirement: The interface stage enumerates intended interface changes

The interface-design stage SHALL enumerate the contracts, schemas, data formats, and component boundaries the epic is expected to change, each with its intended shape at a level the user can judge without implementation detail. Interface decisions meeting the project's ADR criteria SHALL be flagged as ADR candidates rather than settled silently inside the plan.

#### Scenario: Public contract change reviewed at the interface stage
- **WHEN** the epic is expected to change a public API
- **THEN** the interface stage lists that API and its intended shape change for user confirmation

#### Scenario: Significant interface decision flagged as ADR candidate
- **WHEN** an interface decision is cross-cutting or hard to reverse
- **THEN** the stage flags it as an ADR candidate with its decision drivers

### Requirement: The decomposition skeleton precedes all detail filling

The skeleton stage SHALL name each planned TASK with exactly one independently verifiable outcome and its dependencies, without test cases, change maps, or verification detail. Detail artifacts — planned test cases, change maps, fuzz plans, delivery-track evidence — SHALL NOT be filled in before the user confirms the skeleton, and detail filling SHALL use the confirmed skeleton as its input.

#### Scenario: Details deferred until skeleton confirmation
- **WHEN** the skeleton has not been confirmed by the user
- **THEN** the planning flow produces no test cases, change maps, or fuzz-plan detail

#### Scenario: Revised skeleton drives detail filling
- **WHEN** the user changes the decomposition at skeleton confirmation
- **THEN** all detail filling proceeds from the revised skeleton

### Requirement: Plan Approval verifies consistency with the confirmed interview

The completed plan SHALL present its filled details against the artifacts confirmed during the interview. Plan Approval SHALL verify that consistency; an interface or scope change that was not confirmed during the interview SHALL return the plan to the interview stages instead of being approved silently.

#### Scenario: Unexpected interface change returns to the interview
- **WHEN** the filled plan contains an interface change absent from the confirmed interface stage
- **THEN** Plan Approval returns the plan to the interview instead of approving it

#### Scenario: Consistent plan proceeds to approval
- **WHEN** the filled plan matches the confirmed skeleton and interface changes
- **THEN** Plan Approval evaluates it as the design already agreed plus its details

### Requirement: Stage collapse is proportional and recorded

Interview stages SHALL be collapsed or merged only for bounded epics with a recorded rationale in the interview record. No stage SHALL collapse silently.

#### Scenario: Collapsed stages recorded with rationale
- **WHEN** planning merges the risks stage into the objective stage for a small epic
- **THEN** the interview record names the merged stages and the rationale

### Requirement: Already planned epics keep their approved plans

Epic plans approved before this capability existed SHALL continue their lifecycle without re-interview, and their planning artifacts SHALL remain valid.

#### Scenario: Existing approved plan unaffected
- **WHEN** an epic already holds an approved plan at migration time
- **THEN** it continues through execution and acceptance without any interview requirement
