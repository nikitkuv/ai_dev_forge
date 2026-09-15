## ADDED Requirements

### Requirement: External-work intake records an intent for each product-change candidate

For every normalized external record classified as a product-change candidate, external-work intake SHALL create an intent record before any canonical change, populating its narrative sections from the normalized source evidence and the intake interview. The record SHALL carry the provider-neutral source keys it originated from. Candidates classified as defects, investigations, or duplicates follow their existing dispositions; a rejected product-change candidate SHALL be retained as a `rejected` intent record with rationale and MUST NOT create an Epic.

#### Scenario: Ticket becomes an Epic

- **WHEN** an external ticket is approved as a new Epic
- **THEN** intake records an intent whose `outcome` moves to `promoted` with `promoted_to` set to the new Epic, the Backlog row links the intent, and the source keys are preserved in the record

#### Scenario: Ticket is rejected

- **WHEN** an external ticket is judged out of scope or a duplicate during intake
- **THEN** intake retains a `rejected` intent record with the rationale and source keys, and no Backlog row is created for it

#### Scenario: Underspecified ticket feeds the interview

- **WHEN** a ticket provides only a title and a brief description
- **THEN** intake fills the intent template by investigating repository evidence and asking the user only for material product decisions the ticket cannot resolve
