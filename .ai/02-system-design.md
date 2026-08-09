# Bootstrap Step 02 — System Design

## Purpose

Create an approved target `ARCHITECTURE.md`, authoritative ADR records, and the generated `DECISIONS.md` navigation index in the user's communication language.

Use `.ai/templates/ARCHITECTURE.md`, `.ai/templates/ADR.md`, `.ai/templates/DECISIONS.md`, and `.ai/CONVENTIONS.md`. Reference these templates rather than duplicating their complete structures here.

## Preconditions and Inputs

Required:

- an explicitly approved `SPEC.md`;
- `.ai/CONVENTIONS.md`;
- the architecture and decision templates.

For an existing project, inspect relevant code, tests, configuration, deployment material, data schemas, interfaces, and existing decisions. Current implementation is evidence and a migration constraint, not automatic target architecture.

If `SPEC.md` is missing, still `draft`, or materially inconsistent, return to Step 01.

## Architecture Interview

1. Derive architectural drivers from functional requirements, NFRs, domain rules, constraints, integrations, scale, and trust boundaries.
2. For an existing project, compare target drivers with current structure and surface gaps, compatibility risks, and migration constraints.
3. Ask focused questions about system boundaries, ownership, deployment, data, security, reliability, observability, testing, and compatibility.
4. When more than one viable design exists, propose concrete alternatives with consequences and recommend one with a stated rationale.
5. Confirm decisions with the user instead of choosing silently.

The architecture describes target structure and may differ from the current implementation. It must not contain Task decomposition, execution status, estimates, or line-level implementation instructions.

## ADR Criteria and Approval

Create an ADR candidate when a decision is significant, long-lived, cross-cutting, difficult to reverse, or has multiple viable alternatives with meaningful trade-offs.

Do not create ADRs for local implementation details, obvious defaults, or easily reversible choices.

For each candidate:

1. allocate the next global `ADR-NNN`;
2. create the ADR from `.ai/templates/ADR.md` with `status: PROPOSED`;
3. present its context, drivers, alternatives, recommendation, consequences, migration, and verification;
4. invoke the **ADR Approval** gate and request explicit user approval;
5. change the status to `ACCEPTED` only after approval; use `REJECTED` when the user rejects the recorded proposal.

Never rewrite an accepted decision to change its meaning. A later change requires a new ADR with `supersedes`.

## Architecture Draft and Approval

1. Create or update `ARCHITECTURE.md` from its template with `document_status: draft`.
2. Link requirement drivers and relevant ADRs instead of duplicating their content.
3. Check component boundaries, dependency direction, data ownership, interfaces, trust boundaries, runtime, reliability, observability, testing, migration, compatibility, and known risks. Identify applicable quality profiles and critical paths without inventing repository commands or decomposing work into Tasks.
4. Present the target design, alternatives, unresolved risks, and current-to-target differences.
5. Request explicit user approval of the architecture.
6. Only after approval, set `document_status: approved` and `approved_at`.
7. Generate `DECISIONS.md` from ADR frontmatter. The index is navigation only; ADR files remain authoritative.

Corrections keep the architecture in `draft`. Unresolved required ADRs block architecture approval.

## Completion Gate

This step is complete only when:

- every approved requirement has an architectural response or an explicit non-architectural classification;
- target and current-state evidence are clearly distinguished;
- significant decisions passed the ADR Approval gate;
- `ARCHITECTURE.md` has explicit user approval and is marked `approved`;
- `DECISIONS.md` matches ADR frontmatter;
- no Task-level plan or execution state was created.

Do not start Step 03 automatically. Report the result and request a separate user confirmation.

## Outputs

- `ARCHITECTURE.md`
- `DECISIONS.md`
- `decisions/ADR-NNN-<short-name>.md` for significant decisions
