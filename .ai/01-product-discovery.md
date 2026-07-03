# Bootstrap Step 01 — Product Discovery



---



## Purpose



The purpose of this step is to collaboratively build a complete and unambiguous understanding of the product before any architecture, planning or implementation begins.



The output of this step is a **SPEC.md** document.



This is a discovery process, not a documentation or design task.



The goal is to eliminate ambiguity and define **what the product is**, not how it is built.



---



# Inputs



Required:



- BOOTSTRAP.md

- CONVENTIONS.md



Optional:



- Existing repository

- Existing documentation

- README.md

- Issues / tickets

- Prior requirements

- User notes



---



# Core Principle



> Do not design the system. Understand the product.



---



# Overview



This step consists of five phases:



1. Repository analysis

2. Product discovery interview

3. Ambiguity resolution

4. Understanding validation

5. SPEC.md generation



All phases are mandatory.



---



# Phase 1 — Repository Analysis



Before asking questions:



Analyze existing materials:



- README.md (if exists)

- existing codebase (if exists)

- existing documentation

- existing issues / notes



Identify:



- apparent product purpose

- existing functionality

- implicit constraints

- current system behavior (if any)



Do NOT create SPEC.md yet.



Goal: reduce unnecessary questions.



---



# Phase 2 — Product Discovery Interview



Conduct a structured but adaptive interview with the user.



Do NOT ask exhaustive questionnaires.



Only ask questions that improve understanding.



---



## 2.1 Product Vision



Clarify:



- What problem does the product solve?

- Why does it exist?

- What value does it provide?

- Why now?



---



## 2.2 Target Users



Identify:



- primary users

- secondary users

- system operators

- external systems (if relevant)



---



## 2.3 Functional Requirements (WHAT the product does)



Clarify behavior:



- core functionality

- expected workflows

- user interactions

- system behaviors



Explicitly capture:



- in-scope functionality

- out-of-scope functionality



Do NOT discuss implementation.



---



## 2.4 Non-Functional Requirements



Clarify constraints:



- performance expectations

- scalability requirements

- reliability expectations

- security requirements

- observability needs

- compliance constraints



Only include what is relevant.



---



## 2.5 External Dependencies



Identify integrations:



- APIs

- databases

- LLM providers

- authentication systems

- third-party services

- messaging systems



---



## 2.6 Constraints



Capture constraints:



- technical

- business

- legal

- operational



---



## 2.7 Success Criteria



Define how success is measured:



- user success metrics

- business outcomes

- system-level outcomes



---



## 2.8 Existing System Behavior (if applicable)



If a system already exists:



- what currently works

- what must not change

- known limitations

- pain points

- desired evolution direction



---



# Phase 3 — Ambiguity Resolution



If any uncertainty exists:



- ask follow-up questions

- iterate until clarity is reached



Rules:



- never assume

- never infer silently

- never fabricate missing information



---



# Phase 4 — Understanding Validation



Before generating SPEC.md:



Provide a structured summary:



- Product overview

- Target users

- Core functionality

- External integrations

- Constraints

- Success criteria



Then ask the user:



> “Is this understanding correct?”



Do NOT proceed until user confirms.



If corrections are provided:



- update understanding

- repeat validation



---



# Phase 5 — Generate SPEC.md



After confirmation, generate SPEC.md.



SPEC.md defines:



- what the product is

- what problems it solves

- who uses it

- what behavior it provides

- constraints

- success criteria



---



## SPEC.md MUST NOT contain:



- system architecture

- technology choices

- implementation details

- backlog or epics

- task breakdown

- development workflow

- execution planning



---



## Recommended Structure of SPEC.md



- Product Overview

- Vision

- Goals

- Scope

- Out of Scope

- Users

- Functional Requirements

- Non-Functional Requirements

- External Integrations

- Constraints

- Assumptions

- Success Criteria



Additional sections allowed only if they improve clarity.



---



# Restrictions



During this step, strictly prohibit:



- system design

- architecture decisions

- tech stack selection

- backlog creation

- planning implementation

- task decomposition

- coding

- estimation

- execution modeling



---



# Definition of Done



This step is complete only if:



- product understanding is complete

- ambiguities are resolved

- user confirms understanding

- SPEC.md is generated

- SPEC.md contains only product-level information

- SPEC.md contains no design or implementation details



---



# Outputs



Create or update:



- SPEC.md



No other files may be modified.



---



# Next Step



Recommend:



Bootstrap Step 02 — System Design



Do NOT proceed automatically.



Wait for user confirmation.



---

