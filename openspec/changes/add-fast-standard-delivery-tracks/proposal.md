## Why

Forge currently has model tiers named `fast`, `balanced`, and `strong`, but every production TASK follows one delivery route through an independent strong reviewer and a separate tester. The existing `low`, `standard`, and `high` risk labels do not alter gates, so small, reversible changes pay the same orchestration cost as materially risky work.

## What Changes

- Introduce exactly two explicit TASK delivery tracks: `fast` and `standard`, kept separate from model tiers and risk levels.
- Define a fail-closed eligibility contract for `fast`: only bounded, reversible, low-risk work without disqualifying affected surfaces or risk flags may use it.
- Let a `fast` TASK retain implementer execution, focused TDD when applicable, explicit Task Start, user acceptance, and commit gates while replacing separate reviewer and tester invocations with recorded orchestrator assurance over the scoped diff and focused verification evidence.
- Keep the current implementer → independent reviewer → tester route as the `standard` track.
- Require automatic escalation from `fast` to `standard` when actual scope, risk, test integrity, or verification differs from the approved classification; forbid silent downgrade from `standard` to `fast` after Task Start.
- Add track-specific lifecycle transitions, evidence fields, planning guidance, resume behavior, completion rules, documentation, scenarios, adapter guidance, and contract tests.
- Keep Epic Validation and the Epic fuzzing gate unchanged so aggregate confidence is not weakened by TASK-level routing.

## Capabilities

### New Capabilities

- `task-delivery-tracks`: Defines selection, eligibility, execution, escalation, lifecycle, and evidence requirements for the `fast` and `standard` TASK delivery tracks.

### Modified Capabilities

- `production-review-gating`: Limits mandatory independent production review and separate tester execution to the `standard` track while defining orchestrator assurance and focused verification as the `fast` track gate.

## Impact

- Affects framework contracts, TASK and Epic-plan templates, planner and implementer contracts, task execution/completion/resume skills, generated adapter guidance, maintained documentation, development scenarios, validation rules, and contract tests.
- Changes TASK lifecycle behavior by permitting an eligible `fast` TASK to move from implementation directly to user acceptance after current orchestrator-assurance evidence, without entering independent-review or separate-tester stages.
- Does not create a third delivery track, allow untracked production edits, bypass explicit user acceptance, weaken Epic Validation/fuzzing, or make risk labels alone sufficient for fast eligibility.
