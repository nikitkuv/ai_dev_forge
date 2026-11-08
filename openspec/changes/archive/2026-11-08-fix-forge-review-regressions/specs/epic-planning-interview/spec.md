## ADDED Requirements

### Requirement: Bootstrap uses the same interview before planner invocation

New-project and existing-project bootstrap preparation SHALL route through the staged Epic preparation workflow. The numbered workspace step SHALL require confirmed skeleton and Interface Delta before invoking the planner, and SHALL require interview consistency before Plan Approval. Bootstrap SHALL retain separate Plan Approval, optional Epic Start, and Task Start gates and SHALL NOT require re-interview for previously approved plans.

#### Scenario: First Epic during bootstrap
- **WHEN** either bootstrap mode reaches workspace preparation for a new Epic
- **THEN** the orchestrator conducts the staged interview before planner detail filling and checks the filled plan against its confirmed artifacts
