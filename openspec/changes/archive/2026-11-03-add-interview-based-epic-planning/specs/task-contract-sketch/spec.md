# Task Contract Sketch

## Purpose

Captures the human-approved shape of public contracts before implementation, so implementation is delegated behind a designed interface instead of discovering the contract shape in code.

## ADDED Requirements

### Requirement: Interface-touching tasks carry a contract sketch

A TASK whose affected contracts include public interfaces SHALL carry a contract sketch naming each changed contract and its intended shape — signatures or endpoints, schema fields, and error behavior — sufficient to judge the interface without implementation detail. A TASK touching no public contracts SHALL record explicitly that no sketch applies. Sketches are prepared with the task definition, before Plan Approval.

#### Scenario: Sketch prepared for a public API change
- **WHEN** a planned TASK changes a public API
- **THEN** its definition includes a sketch of the changed shape before Plan Approval

#### Scenario: Non-interface task records no sketch
- **WHEN** a TASK affects no public contracts
- **THEN** its definition records that no contract sketch applies

### Requirement: Sketches are approved with the plan and bound at Task Start

Contract sketches SHALL be confirmed through Plan Approval alongside the task definition. At Task Start the implementer SHALL treat the approved sketches as boundary constraints on contract shape. Changing a contract's shape away from the approved sketch SHALL require the Replan gate before implementation adopts the new shape.

#### Scenario: Shape change requires Replan
- **WHEN** implementation needs a different contract shape than the approved sketch
- **THEN** the change goes through Replan before code adopts the new shape

#### Scenario: Task Start binds the approved sketch
- **WHEN** a Task Start runs for a TASK with an approved sketch
- **THEN** the sketch is handed over as a boundary constraint together with the task assignment

### Requirement: Independent review checks sketch conformance

Independent review SHALL report a sketch-conformance result for each changed contract as part of acceptance traceability. A delivered contract shape that differs from the approved sketch without a recorded Replan SHALL be reported as a production finding. The sketch constrains contract shape only and SHALL NOT constrain internal implementation.

#### Scenario: Conformance reported per contract
- **WHEN** an independent review runs on a TASK with a sketch
- **THEN** the review outcome includes a conformance result per changed contract

#### Scenario: Unapproved shape difference is a finding
- **WHEN** the delivered contract shape differs from the approved sketch and no Replan recorded the change
- **THEN** the review reports it as a production finding

#### Scenario: Internal implementation stays unconstrained
- **WHEN** internal code structure differs from anything implied by the sketch
- **THEN** the sketch conformance result is unaffected as long as the contract shape matches

### Requirement: Legacy tasks without sketches keep current behavior

A TASK created before this capability existed SHALL proceed without a sketch requirement, and its review SHALL follow the existing affected-contracts flow. A missing sketch SHALL NOT block Task Start, review, testing, or acceptance.

#### Scenario: Legacy task accepted without sketch
- **WHEN** a legacy TASK with public contract changes reaches review without a sketch
- **THEN** review proceeds under the existing affected-contracts flow with no sketch requirement
