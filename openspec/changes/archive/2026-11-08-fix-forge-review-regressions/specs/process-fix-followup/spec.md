## ADDED Requirements

### Requirement: Acceptance distinguishes recorded rejections from template choices

Acceptance SHALL treat only a recorded rejection result as rejection evidence. Template choice lists and placeholders SHALL NOT be interpreted as user feedback. A real recorded `changes requested` result SHALL continue requiring the existing follow-up facts for a TASK carrying that block; legacy TASK compatibility SHALL remain unchanged.

#### Scenario: Clean acceptance retains the template example
- **WHEN** a TASK retains the template's User Validation example row and has no actual rejection
- **THEN** explicit acceptance proceeds without requiring a process follow-up

#### Scenario: Real rejection alongside the example
- **WHEN** the table contains both the example row and a real `changes requested` result
- **THEN** acceptance requires the follow-up before DONE
