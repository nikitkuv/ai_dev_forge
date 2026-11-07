# Rule Drift Detection

## Purpose

Keeps project-declared rules honest by deterministically reporting code that contradicts them, so agents follow the stated rule instead of copying the violating pattern.

## ADDED Requirements

### Requirement: Project rules are declared with checkable patterns

A project SHALL be able to declare its own rules in a project-owned declaration, where each rule has a stable identifier, a human-readable statement, an optional checkable pattern, and a scope of paths it applies to. Rule statements SHALL be visible to agents through the project router overlay, and the declaration SHALL remain project-owned content that framework updates preserve.

#### Scenario: Rule declared with pattern and scope
- **WHEN** the project declares a rule with a pattern and a path scope
- **THEN** the declaration stores the identifier, statement, pattern, and scope, and the statement is visible to agents through the router overlay

#### Scenario: Framework update preserves project rules
- **WHEN** a framework update replaces framework-owned files
- **THEN** the project rule declaration and router-overlay rule statements remain unchanged

### Requirement: Drift between declared rules and code is reported deterministically

A model-free check SHALL compare each rule's pattern against its scoped paths and report, per rule, the number of violations and the violating paths. The check SHALL perform no model calls, SHALL NOT modify any file, and SHALL NOT change lifecycle state. Rules without a pattern SHALL be reported as requiring judgment instead of silently passing.

#### Scenario: Violating code reported
- **WHEN** a rule's pattern matches files in its scope where the code contradicts the statement
- **THEN** the check reports the rule identifier, violation count, and violating paths without model calls

#### Scenario: Unverifiable rule reported as judgment
- **WHEN** a declared rule has no checkable pattern
- **THEN** the check reports that rule as unverifiable and requiring judgment

#### Scenario: Clean scope reported
- **WHEN** no file in a rule's scope violates its pattern
- **THEN** the check reports the rule as consistent and lists no paths

### Requirement: Reported drift always receives a disposition

Every rule reported as violated SHALL end with exactly one disposition: the code is fixed to comply, the rule is amended or removed, or the rule's scope is narrowed — each as an authorized change with a recorded rationale. A violated rule SHALL NOT remain silently in place across completed work.

#### Scenario: Code fixed to comply
- **WHEN** the user keeps a violated rule and the violation is real
- **THEN** the violating code is changed to comply and the rule remains declared

#### Scenario: Rule amended instead of code
- **WHEN** the user determines the rule itself is wrong
- **THEN** the rule statement or pattern is amended with a recorded rationale instead of forcing code changes

### Requirement: Drift findings integrate with conformance checking

The framework conformance check SHALL include the drift report in its coverage and keep separating mechanical matches from fields that require judgment, consistent with other deterministic helpers.

#### Scenario: Conformance run includes drift results
- **WHEN** the framework conformance check runs on a project with declared rules
- **THEN** its output includes per-rule drift results and marks unverifiable rules as requiring judgment
