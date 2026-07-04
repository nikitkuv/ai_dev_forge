<!-- TEMPLATE: ARCHITECTURE.md — HOW the system is organized. Derived strictly from SPEC.md. -->
<!-- Created in: Bootstrap Step 02 (System Design). No implementation details, no tasks. -->

# ARCHITECTURE.md — <Product Name>

## System Overview

<1 short paragraph: how the system is structured at a high level.>

## Design Goals

- <Goal>

## Architectural Principles

- <Principle>

## High-Level System Architecture

<Diagram or textual description of major components and their relationships.>

## Components

- **<Component A>** — <responsibility>
- **<Component B>** — <responsibility>

## Component Responsibilities

- <Component>: <boundary, single responsibility>

## Data Flow

<user → entry point → internal services → background → external>

## External Integrations

- <LLM provider / DB / storage / auth / third-party API>

## Cross-Cutting Concerns

- Auth, logging, monitoring, config, secrets, error handling, retries, rate limiting

## Deployment Overview

<Where and how it runs.>

## Scalability Strategy

<Expected scale, bottlenecks, horizontal scaling.>

## Reliability Strategy

<Failure modes, fault tolerance, recovery, degradation.>

## Security Considerations

<High-level only. Do not implement mechanisms here.>

## Risks & Trade-offs

- <Risk / trade-off>

## Future Evolution

<Direction the architecture may take.>

<!--
Significant trade-offs in this document should be captured as ADRs
in decisions/ (see DECISIONS.md template).
-->
