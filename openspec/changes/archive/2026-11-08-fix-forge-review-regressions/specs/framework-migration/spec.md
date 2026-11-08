## ADDED Requirements

### Requirement: Shipped release metadata supports the advertised upgrade

The shipped manifest and project configuration template SHALL declare the same release version, newer than the preceding 4.12.0 bundle. Version-specific migration entries SHALL NOT exceed that shipped version. Consumers on 4.12.0 SHALL be able to preview and apply the current bundle without editing its target version; equal-version and downgrade guards SHALL remain in force.

#### Scenario: Upgrade to the actual shipped release
- **WHEN** a consumer on 4.12.0 stages the current shipped bundle
- **THEN** preview offers an upgrade including the 4.13 notes and apply updates the bundle and project version while preserving project-owned data

### Requirement: Staged rendering validates rules against the staged contract

Migration rendering SHALL interpret preserved project rule declarations using the staged bundle's rule contract, independently of the active bundle's support for rules. The render input fingerprint SHALL cover the rule contract used.

#### Scenario: First upgrade with a prepared rule declaration
- **WHEN** the active contract predates rule support and the project has a valid rule declaration
- **THEN** preview renders its statements using the staged contract and apply preserves the declaration byte-for-byte

#### Scenario: Rule contract changes after preview
- **WHEN** the rendering bundle's rule contract changes after preview
- **THEN** its render input fingerprint changes and stale apply is refused
