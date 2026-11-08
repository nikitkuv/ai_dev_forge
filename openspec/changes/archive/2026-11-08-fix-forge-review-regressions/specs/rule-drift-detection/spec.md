## ADDED Requirements

### Requirement: Router conformance detects removed declarations

Conformance SHALL compare the router's Project Rules block with the current declaration even when no rules remain or the declaration file has been removed. Stale router statements SHALL be reported until adapter synchronization removes them. A project with neither declared nor rendered rules SHALL remain valid.

#### Scenario: Last rule removed
- **WHEN** the last declaration is removed but its statement remains in the router
- **THEN** conformance identifies the stale rule and synchronization removes it

#### Scenario: Declaration file removed
- **WHEN** the declaration file is removed while the router still contains rule statements
- **THEN** conformance reports those statements as stale rather than silently passing
