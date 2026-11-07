# Human Review Focus

## Purpose

Focuses the human's residual acceptance effort on project-declared critical surfaces, so spot-checks land on the places that matter most and everything else is already covered by independent verification.

## ADDED Requirements

### Requirement: The project declares its critical surfaces

A project SHALL be able to declare critical surfaces — named areas such as architecture boundaries, billing, or the data model — in a project-owned canonical document, each with a reference to the canonical source that defines it. The declaration SHALL persist across epics and SHALL be editable only as an explicit project change.

#### Scenario: Critical surface declared
- **WHEN** the project declares billing as a critical surface with a reference to its architecture section
- **THEN** later planning and acceptance flows can resolve that surface and its reference

#### Scenario: Declaration persists across epics
- **WHEN** one epic completes and another is planned
- **THEN** the declared critical surfaces remain in effect without redeclaration

### Requirement: Planning folds critical surfaces into Task Review Focus

When a planned Task's affected surface intersects a declared critical surface, the Epic planning output SHALL name that surface in the Task's Review Focus. When no declared surface is affected, the Review Focus SHALL record that explicitly.

#### Scenario: Task touching a critical surface
- **WHEN** a Task's planned change map touches the declared data model surface
- **THEN** its Review Focus names the data model surface as the human spot-check target

#### Scenario: Task outside all critical surfaces
- **WHEN** a Task's affected surface intersects no declared critical surface
- **THEN** its Review Focus records that no declared surface is affected

### Requirement: Acceptance presentation groups manual verification by critical surfaces

When presenting a Task or Epic for human acceptance, the orchestrator SHALL group Manual Verification steps by the declared critical surfaces they exercise and present touched surfaces first. Verification steps outside declared surfaces remain present after the grouped ones.

#### Scenario: Manual steps grouped at acceptance
- **WHEN** a Task touches a declared critical surface and has manual verification steps
- **THEN** the acceptance presentation groups those steps under that surface and presents them first

### Requirement: Critical surfaces never replace independent verification

The declared surfaces SHALL focus human attention only. They SHALL NOT reduce reviewer or tester scope, change production-surface gating, or waive any assurance requirement on any delivery track.

#### Scenario: Assurance unchanged by declaration
- **WHEN** critical surfaces are declared and a standard Task touches one
- **THEN** independent review, testing, and production gating run exactly as without the declaration

### Requirement: Empty declaration falls back to current behavior

When the project declares no critical surfaces, planning and acceptance flows SHALL behave exactly as before, and an empty or missing declaration SHALL NOT block any gate.

#### Scenario: No declaration present
- **WHEN** a project has no critical-surface declaration
- **THEN** Review Focus and acceptance presentation follow the existing per-Task Manual Verification flow with no additional requirements
