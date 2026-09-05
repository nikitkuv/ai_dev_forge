## Context

Forge currently has one TASK state path and one assurance route. `risk_level` and `risk_flags` are planning context, while `model_tier` selects an agent model; neither changes lifecycle gates. The existing production-review optimization can reuse a clean strong review after supporting-only remediation, but still requires the tester gate. See `proposal.md` and the two delta specs for the new behavior contract.

The framework is documentation-first: lifecycle semantics live in `.ai/framework/contracts.yaml`, TASK evidence lives in the TASK file, neutral agent and skill sources drive adapters, and maintained documentation plus contract tests must remain synchronized. Existing active and planned work may not contain a delivery-track field, so migration must fail safely.

## Goals / Non-Goals

**Goals:**

- Make `fast` and `standard` explicit, mechanically distinguishable TASK routes.
- Make fast selection conservative, evidence-based, and automatically escalatable.
- Remove reviewer/tester agent overhead from eligible fast work without removing focused verification or user acceptance.
- Preserve current standard behavior and aggregate Epic assurance.
- Keep resume and migration deterministic without relying on session history.

**Non-Goals:**

- Add a third or configurable custom track.
- Let risk level alone choose a track.
- Let the primary orchestrator edit fast production scope instead of delegating it to implementer.
- Create standalone TASKs outside an Epic or collapse intake, Plan Approval, Epic Start, Task Start, Task Acceptance, or Epic Acceptance into one gate.
- Change model mappings, reviewer-provider routing, Epic Validation, or fuzzing applicability rules.

## Decisions

### Store delivery track as approved TASK data

Add `delivery_track: standard` to TASK frontmatter and a `Delivery Track` section containing rationale, eligibility evidence, disqualifier disposition, approval source, and escalation history. `standard` is the template and migration default. The planner may propose `fast`, but Plan Approval or Replan approves that proposal as part of the TASK definition.

This is separate from `risk_level`: risk is an input to routing, while delivery track is the selected route. It is also separate from agent `model_tier`, which continues to select execution cost/capability for a role.

Alternative considered: infer the route dynamically from `risk_level`. Rejected because risk labels do not describe reversibility, verification readiness, affected contracts, or disqualifying surfaces and would make resume nondeterministic.

### Represent fast eligibility as positive evidence plus disqualifiers

The planner records positive fast evidence for bounded scope, reversibility, low risk, unambiguous expected behavior, and deterministic focused verification. It also records an explicit disposition for every disqualifier named in the spec. Missing, unknown, or contradictory evidence selects `standard`.

The orchestrator rechecks eligibility twice: immediately before Task Start and against the actual diff before assurance. This prevents a reasonable planning estimate from becoming a permanent waiver after implementation expands.

Alternative considered: file-count or line-count thresholds. Rejected as primary criteria because a one-line migration, authorization change, or build edit can be high impact. Diff size may be supporting evidence but never overrides a disqualifier.

### Preserve implementer separation on both tracks

Both tracks invoke the balanced implementer for production and necessary test changes. Fast saves the independent reviewer and tester calls, not the implementation boundary. This leaves the strong primary orchestrator in a position to inspect work it did not author and avoids creating a second coding contract.

The implementer receives the selected track and eligibility constraints. Its implementation summary remains responsible for scope, fingerprints, RED/GREEN or not-applicable rationale, path classification, test oracles, test-change classification, and selected command results.

Alternative considered: let the orchestrator implement fast changes directly. Rejected because it combines authorship and approval, conflicts with the current code-writing delegation boundary, and makes the supposed assurance review self-review.

### Add one orchestrator-owned fast assurance gate

For fast work, the orchestrator performs a single assurance procedure after implementation:

1. reproduce the whole-implementation fingerprint and exact scoped diff;
2. revalidate eligibility against actual changed and affected surfaces;
3. inspect all production and supporting paths and trace acceptance criteria and risks;
4. validate independent test oracles and test-change classifications;
5. execute or reproduce all focused tests, selected affected checks, applicable scoped quality checks, and Task fuzz smoke or its not-applicable rationale;
6. record `PASSED` or escalate to standard.

The TASK gains a `Fast Assurance Summary` bound to the implementation fingerprint. Standard `Review Summary` and `Test Summary` remain authoritative only for standard work. Fast evidence never masquerades as `CLEAN` independent review or tester evidence.

Alternative considered: trust the implementer's passing commands. Rejected because a no-review/no-tester route still needs separation between implementation claims and acceptance eligibility.

### Use a direct fast lifecycle transition

Add a track-guarded transition `IN PROGRESS -> AWAITING USER ACCEPTANCE`. It is legal only for `delivery_track: fast` with current passing orchestrator assurance. Standard retains:

```text
IN PROGRESS -> IN REVIEW -> IN TESTING -> AWAITING USER ACCEPTANCE
```

Fast uses:

```text
IN PROGRESS -> AWAITING USER ACCEPTANCE
```

This avoids placing fast TASKs in states whose named gates and role evidence do not exist. Completion and commit rules replace the unconditional `current_review_and_testing_evidence` predicate with track-specific current assurance evidence.

Alternative considered: pass fast through `IN REVIEW` and `IN TESTING` without invoking agents. Rejected because it would make lifecycle states ambiguous and complicate resume diagnostics.

### Escalation is monotonic after Task Start

`fast -> standard` is always allowed before acceptance when the orchestrator records a concrete trigger. It is a safety increase, so it does not require user authorization or Replan when scope is unchanged. Scope changes still require Replan independently. Escalation invalidates fast assurance and sends the current implementation through standard review and testing.

`standard -> fast` is forbidden after Task Start. Before Task Start, changing an approved track requires Plan Approval or Replan because it weakens the approved assurance route.

The TASK iteration history records old track, new track, trigger, timestamp, current fingerprint, and whether scope also changed.

Alternative considered: allow bidirectional dynamic routing. Rejected because a late downgrade can become a pressure-release mechanism after standard gates expose cost or delay.

### Default legacy and ambiguous work to standard

Existing TASKs without `delivery_track` are interpreted as `standard`. Migration writes the explicit field without fabricating approval evidence. A planned or active legacy TASK can opt into fast only through Plan Approval or Replan and only before Task Start; already-started legacy work remains standard.

Current standard review/test evidence remains valid under existing fingerprint rules. No review evidence is converted into fast assurance and no fast assurance is synthesized from prior implementation results.

### Keep Epic-level gates track-neutral

Epic Validation consumes the exact aggregate fingerprint and all completed TASK evidence but does not reduce its command selection because a TASK used fast. The existing Epic fuzzing plan and final applicability decision also remain unchanged. Remediation created after Epic Validation receives its own delivery-track classification; it is not automatically standard or fast solely because it came from validation.

## Risks / Trade-offs

- Fast classification could underestimate a transitive affected surface. -> Require positive evidence, enumerate disqualifiers, recheck the actual diff, and escalate on uncertainty.
- The orchestrator may perform a shallower check than specialized agents. -> Define a reproducible assurance checklist and reserve fast for low-risk, deterministic work; Epic Validation remains unchanged.
- Fast assurance duplicates checks already run by implementer. -> Accept bounded duplication as the independent confidence mechanism replacing two agent calls.
- A failed fast check always escalates even for an obvious environment issue. -> Permit execution-limit handling to distinguish a reproducible environmental blocker, but do not permit acceptance on missing evidence; unresolved failure remains standard.
- Direct lifecycle transition can break existing validators or adapters. -> Update contracts, templates, resume/completion skills, final validation, adapters, scenarios, and contract tests atomically.
- Existing work lacks track data. -> Interpret absence as standard and prohibit inferred fast migration.
- Fast within a full Epic still carries planning and Epic-level ceremony. -> Keep this change focused on TASK delivery routing; standalone micro-work packaging can be evaluated separately after usage evidence exists.

## Migration Plan

1. Extend canonical enums, transition guards, quality gates, and invariants with delivery-track semantics while retaining current standard defaults.
2. Add track and assurance fields to TASK/plan templates and update planner, implementer, run, resume, complete, bootstrap/migration, and validation contracts.
3. Update maintained documentation and the development-pipeline scenario with parallel fast and standard flows plus escalation examples.
4. Add contract tests for selection, disqualifiers, direct transition, assurance freshness, escalation, legacy defaulting, standard preservation, and Epic-gate invariance.
5. Increment the framework version and synchronize generated Codex and Claude adapters.
6. Treat all existing TASKs without the field as standard. Offer explicit template migration; do not rewrite approved track semantics or synthesize fast evidence.
7. Run the repository test suite, framework consistency checks, adapter parity checks, and strict OpenSpec validation.

Rollback restores the previous framework bundle and adapters. TASKs already carrying `delivery_track` or fast-assurance fields remain project-owned unknown fields during rollback; any nonterminal fast TASK must be treated as standard before it can advance under the old lifecycle.
