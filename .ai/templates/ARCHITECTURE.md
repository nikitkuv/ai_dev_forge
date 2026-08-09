---
document_type: architecture
document_status: draft
language: "<language-code>"
created_at: "<YYYY-MM-DD>"
approved_at:
---

# <Product Name> — Architecture

## Document Contract

This document is the single source of truth for the approved target architecture. It explains how the system satisfies the drivers in `SPEC.md`, including architecture that is not implemented yet.

It may define technical boundaries and decisions, but it must not contain task-level implementation steps, task status, completion percentages, or execution summaries. Significant long-lived or difficult-to-reverse decisions belong in ADR files.

## System Context and Boundaries

<Describe the system, its actors, external systems, responsibilities, and explicit boundary. Add a context diagram when useful.>

## Requirement Drivers

| Requirement | Architectural implication |
| --- | --- |
| <FR-/NFR-/BR-ID> | <Constraint or capability the architecture must provide> |

## Architectural Principles

- <Principle and the behavior it requires from the design.>

## Components and Boundaries

### <Component>

- **Responsibility:** <Owned capability.>
- **Boundary:** <What is inside and outside.>
- **Owned data:** <Data this component authoritatively manages.>
- **Interfaces:** <Exposed commands, queries, APIs, or events.>

## Dependency Rules

- <Allowed dependency direction and prohibited coupling.>
- <How boundary violations are detected or prevented.>

## Data Ownership

| Data or aggregate | Authoritative owner | Readers and writers | Retention or consistency rules |
| --- | --- | --- | --- |
| <Data> | <Component or external system> | <Access rules> | <Rules> |

## Data Flow

### <Flow name>

1. <Source and input.>
2. <Processing boundary.>
3. <Persistence, event, or external call.>
4. <Result and failure path.>

## Interfaces and Events

### <Interface or event>

- **Owner:** <Component.>
- **Consumers:** <Components or external systems.>
- **Contract:** <Request/event and response/result shape.>
- **Compatibility:** <Versioning and change policy.>
- **Failure behavior:** <Timeout, retry, idempotency, rejection, or degradation rules.>

## Trust Boundaries and Security

- <Trust boundary, protected assets, actor or threat, and required control.>
- <Authentication, authorization, secret handling, privacy, audit, or supply-chain constraint.>

## Runtime and Deployment

- **Runtime topology:** <Processes, services, workers, clients, or devices.>
- **Environments:** <Development, test, staging, production, or other environments.>
- **Deployment model:** <Hosting, packaging, rollout, configuration, and rollback.>
- **External dependencies:** <Required infrastructure and operational ownership.>

## Reliability

- **Failure modes:** <Expected failures and impact.>
- **Resilience:** <Timeouts, retries, idempotency, isolation, degradation, and recovery.>
- **Continuity targets:** <Availability, recovery, durability, or data-loss targets linked to NFRs.>

## Observability

- **Signals:** <Logs, metrics, traces, events, or audit records.>
- **Health and alerting:** <What is monitored and when action is required.>
- **Diagnostic context:** <Correlation, identifiers, and privacy constraints.>

## Testing Strategy

- **Quality profiles:** <Applicable backend, frontend, ml, data_pipeline, infrastructure, or library_cli profiles and why.>
- **Unit and component:** <Boundaries and important invariants.>
- **Integration and contract:** <Interfaces, data stores, and external systems.>
- **End-to-end:** <Critical user journeys.>
- **Non-functional:** <Performance, reliability, security, fuzzing, or other required validation.>
- **Verification lifecycle:** <What can be checked selectively per Task and what must be validated project-wide at Epic Validation.>

## Migration and Compatibility

- <Current-to-target migration, data changes, compatibility window, rollout, and rollback.>

## Risks and Known Limitations

| Risk or limitation | Impact | Mitigation or decision needed |
| --- | --- | --- |
| <Risk> | <Impact> | <Mitigation> |

## ADR References

| ADR | Decision | Affected components |
| --- | --- | --- |
| <ADR-NNN> | <Short decision title> | <Components> |
