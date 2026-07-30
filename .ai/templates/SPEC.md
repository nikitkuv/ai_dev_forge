---
document_type: spec
document_status: draft
language: "<language-code>"
created_at: "<YYYY-MM-DD>"
approved_at:
---

# <Product Name> — Product Specification

## Document Contract

This document is the single source of truth for the approved target product behavior, including behavior that is not implemented yet.

It must not contain architecture, technology choices, task breakdowns, completion percentages, or implementation status. Update `document_status` to `approved` and set `approved_at` only after explicit user approval.

## Product Overview

<Describe the product and its purpose in one to three sentences.>

## Vision

<Describe the problem, desired future state, and why the product should exist.>

## Goals

- <Outcome the product must enable.>

## Scope

- <Capability included in the target product.>

## Out of Scope

- <Explicit exclusion or product boundary.>

## Users

### <User or actor>

- **Needs:** <What this actor needs.>
- **Primary value:** <What the product provides.>
- **Relevant constraints:** <Accessibility, permissions, environment, or other constraints.>

## Key User Journeys

### UJ-001 — <Journey name>

1. <Observable user or system step.>
2. <Observable response.>
3. <Expected outcome.>

## Functional Requirements

### FR-001 — <Short requirement name>

**Requirement:** <State observable product behavior without prescribing implementation.>

**Acceptance criteria:**

- <Given/when/then or another objectively verifiable condition.>

## Non-Functional Requirements

### NFR-001 — <Quality attribute>

**Requirement:** <State a measurable performance, reliability, security, accessibility, privacy, scalability, or operability target.>

**Measurement and acceptance criteria:**

- <Metric, measurement conditions, threshold, and allowed exclusions.>

## Domain Rules

### BR-001 — <Invariant name>

**Rule:** <State the business or domain invariant that must always hold.>

**Acceptance criteria:**

- <Example or testable condition that proves the invariant.>

## External Integrations

### <System or provider>

- **Purpose:** <Why the integration exists.>
- **Product-facing contract:** <Observable inputs, outputs, and failure behavior.>
- **Constraints:** <Business, legal, availability, or compatibility constraints.>

## Constraints

- <Business, legal, regulatory, operational, budget, schedule, or mandated-platform constraint.>

## Assumptions

- <Assumption that requires confirmation or may affect scope.>

## Success Criteria

- <Measurable product outcome, target, observation window, and data source where known.>

## Glossary

| Term | Meaning |
| --- | --- |
| <Term> | <Project-specific definition> |
