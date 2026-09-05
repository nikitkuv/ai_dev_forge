## Why

Forge currently lets the strong reviewer turn defects in tests and other non-production files into actionable findings. Every such finding returns the TASK to implementation and requires another full strong-model review, even when the production surface has not changed. This makes late test cleanup create expensive review loops without increasing confidence in the already reviewed production behavior.

## What Changes

- Define a production review surface containing code and runtime or delivery artifacts whose contents can change shipped behavior.
- Keep tests and other non-production artifacts available to the reviewer as supporting evidence, but report their defects in a separate non-blocking observations section.
- Make only production findings affect the review outcome or return a TASK from `IN REVIEW` to `IN PROGRESS`.
- Bind clean review evidence to a production-surface fingerprint. Test-only and other non-production changes invalidate testing evidence but preserve a current clean production review and do not invoke the strong reviewer again.
- Keep Review Packet integrity failures as review blockers and keep the tester responsible for executable test, coverage, selection, and scoped-check gates.
- Update lifecycle guidance, TASK evidence fields, framework contracts, maintained documentation, and automated contract coverage to enforce the boundary consistently.

## Capabilities

### New Capabilities

- `production-review-gating`: Defines production-only blocking findings, advisory treatment of non-production defects, and fingerprint-based reuse of a clean production review.

### Modified Capabilities

None.

## Impact

- Affects the neutral reviewer contract, TASK execution workflow, TASK evidence template, framework contracts and version, adapter guidance, user-facing documentation, scenarios, and contract tests.
- Reduces repeated strong-model invocations when remediation changes only tests or other non-production support files.
- Does not weaken the tester gate, permit failing selected checks, change lifecycle states, or make packet-integrity failures non-blocking.
