# Bootstrap Step 01 — Product Discovery

## Purpose

Create an approved `SPEC.md` that describes target product behavior in the user's communication language. This step discovers what the product must be; it does not design architecture or plan implementation.

Use `.ai/templates/SPEC.md` and the shared rules in `.ai/CONVENTIONS.md`. Do not reproduce or invent a competing document structure.

## Inputs

Required:

- the user's initial description, linked product brief, or interview answers;
- `.ai/CONVENTIONS.md`;
- `.ai/templates/SPEC.md`.

For an existing project, also inspect available code, tests, documentation, configuration, issue material, and Git state.

## Select the Discovery Path

### New Project

1. Extract facts and open questions from the user's prompt or referenced product description.
2. If the description is incomplete, conduct an iterative product interview.
3. Ask a small, focused set of questions at a time and adapt later questions to earlier answers.
4. Resolve product goals, users, journeys, scope, exclusions, observable requirements, domain invariants, constraints, assumptions, integrations, and success criteria.

### Existing Project

1. Analyze the repository before interviewing the user.
2. Build an evidence summary of apparent behavior, supported workflows, constraints, missing coverage, contradictions, and unclear intent.
3. Distinguish explicitly between:
   - behavior confirmed by the user as desired target behavior;
   - current implementation evidence that may be legacy or accidental;
   - documentation claims;
   - unresolved conflicts.
4. Present conflicts between code, tests, documents, and user intent. Ask which behavior is authoritative.
5. Treat discovered bugs, technical debt, missing tests, dependency risks, and architecture violations only as candidates. Do not add them to the product specification or Backlog without a user decision.

Repository behavior is evidence, not product truth.

## Shared Discovery Rules

- Describe target behavior, including approved behavior that is not implemented yet.
- Keep requirements observable and acceptance criteria verifiable.
- Use globally allocated `FR-*`, `NFR-*`, and `BR-*` identifiers.
- Record unknowns as questions; never silently invent product intent.
- Do not choose technologies, components, libraries, deployment, Tasks, Epics, estimates, or implementation status.
- Keep framework instructions in English, but write the generated canonical document in the language recorded for the project.

## Draft and Approval Workflow

1. Summarize the current understanding and unresolved questions.
2. Iterate with the user until material ambiguities are resolved.
3. Create or update `SPEC.md` from `.ai/templates/SPEC.md` with:
   - `document_status: draft`;
   - the project documentation language;
   - target-state requirements and acceptance criteria;
   - no architecture, backlog, tasks, or execution state.
4. Show the user the material assumptions, scope boundaries, and requirements.
5. Request explicit user approval of `SPEC.md`.
6. Only after approval, set `document_status: approved` and `approved_at`.

Corrections keep the document in `draft` and repeat the approval workflow.

## Completion Gate

This step is complete only when:

- product conflicts and unknowns are resolved or explicitly recorded;
- all retained requirements are testable at the product boundary;
- `SPEC.md` contains no architecture or implementation tracking;
- the user has explicitly approved the document;
- `SPEC.md` is marked `approved`.

Do not start Step 02 automatically. Report the result and request a separate user confirmation.

## Output

- `SPEC.md`

Do not modify other canonical documents in this step.
