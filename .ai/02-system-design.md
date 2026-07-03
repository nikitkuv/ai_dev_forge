# Bootstrap Step 02 — System Design

---

## Purpose

The purpose of this step is to design the high-level architecture of the system.

The output of this step is **ARCHITECTURE.md**.

This step defines **how the system is structured and organized**, not how it is implemented.

Architecture is derived strictly from **SPEC.md**.

---

# Inputs

Required:

- BOOTSTRAP.md
- CONVENTIONS.md
- SPEC.md

Optional:

- Existing repository
- Existing documentation
- Existing system diagrams
- Existing deployment setup

---

# Core Principle

> Architecture is a translation of requirements into system structure.

Not implementation.

Not planning.

Not execution.

---

# Overview

This step consists of five phases:

1. Analyze SPEC.md
2. Design system architecture
3. Resolve architectural uncertainties
4. Validate architecture with user
5. Generate ARCHITECTURE.md

All phases are mandatory.

---

# Phase 1 — Analyze SPEC.md

Read SPEC.md completely.

Extract:

- system goals
- functional requirements
- non-functional requirements
- constraints
- external dependencies
- expected scale

Identify implicit architectural requirements.

Do NOT design yet.

Do NOT propose solutions.

---

# Phase 2 — System Design

Design the system at a **high level of abstraction**.

Focus on:

- structure
- responsibilities
- boundaries
- communication patterns

---

## 2.1 System Components

Identify major system components such as:

- API layer
- Backend services
- AI agents / orchestration layer
- Workers / async processing
- Databases
- Caches
- Vector stores
- External integrations
- Observability stack

Only include components that are necessary.

---

## 2.2 Component Responsibilities

For each component:

- define its responsibility
- define its boundaries
- ensure single responsibility per component

Avoid overlapping responsibilities.

---

## 2.3 Communication Model

Define how components interact:

- synchronous vs asynchronous
- request/response flows
- event-driven flows
- external API interactions

Focus on **data flow**, not implementation.

---

## 2.4 Data Flow

Describe how data moves through the system:

- user → system entry point
- internal service communication
- background processing
- external integrations

---

## 2.5 External Dependencies

Identify external systems:

- LLM providers
- databases
- storage systems
- authentication providers
- third-party APIs
- infrastructure services

---

## 2.6 Cross-Cutting Concerns

Define system-wide concerns:

- authentication
- authorization
- logging
- monitoring
- configuration
- secrets management
- error handling
- retries
- rate limiting

---

## 2.7 Scalability Model

Define:

- expected system scale
- bottlenecks
- horizontal scaling strategy
- state management approach

---

## 2.8 Reliability Model

Define:

- failure modes
- fault tolerance strategy
- recovery behavior
- degradation strategies

---

## 2.9 Security Model

High-level only:

- authentication approach
- authorization model
- data protection strategy
- secret management approach

Do NOT implement security mechanisms.

---

# Phase 3 — Resolve Architectural Questions

If any ambiguity exists:

Ask the user before proceeding.

Rules:

- do NOT assume requirements
- do NOT invent constraints
- do NOT choose architecture based on preference

Architecture must reflect SPEC.md only.

---

# Phase 4 — Architecture Validation

Before generating ARCHITECTURE.md:

Provide a structured summary:

- System components
- Responsibilities
- Communication model
- Data flow overview
- External dependencies
- Key architectural trade-offs

Then ask:

> “Is this architecture correct?”

Do NOT proceed without explicit confirmation.

If changes are requested:

- update architecture
- re-validate if necessary

---

# Phase 5 — Generate ARCHITECTURE.md

After approval:

Generate ARCHITECTURE.md.

The document must describe:

- system structure
- component responsibilities
- communication patterns
- architectural decisions
- constraints
- trade-offs

It must be understandable by:

- developers
- maintainers
- AI coding agents

---

# Recommended Structure of ARCHITECTURE.md

- System Overview
- Design Goals
- Architectural Principles
- High-Level System Architecture
- Components
- Component Responsibilities
- Data Flow
- External Integrations
- Cross-Cutting Concerns
- Deployment Overview
- Scalability Strategy
- Reliability Strategy
- Security Considerations
- Risks & Trade-offs
- Future Evolution

---

# Restrictions

During this step, strictly prohibit:

- creating backlog items
- defining Epics or tasks
- writing implementation details
- designing classes or functions
- selecting libraries without justification
- estimating work
- planning execution
- duplicating SPEC.md content
- referencing execution layer

---

# Definition of Done

This step is complete only if:

- architecture fully covers SPEC.md requirements
- system components are clearly defined
- responsibilities are non-overlapping
- communication model is clear
- user has approved the architecture
- ARCHITECTURE.md is generated
- document contains no implementation details

---

# Outputs

Create or update:

- ARCHITECTURE.md

No other files may be modified.

---

# Next Step

Recommend:

Bootstrap Step 03 — Backlog Generation

Do NOT proceed automatically.

Wait for user confirmation.

---

# End of Step
