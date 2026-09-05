---
name: forge-investigate
description: Investigate a material codebase problem outside the Epic/TASK workflow, preserve one canonical INV record, and either stop, promote the result, or fix it directly with the main agent.
---

# Investigate Ad Hoc

Use this workflow only when the user explicitly asks to investigate a concrete codebase problem outside normal Backlog execution, or explicitly names an existing `INV-NNNN`. The main orchestrator performs the work itself. Do not invoke `context-collector`, `documentation-researcher`, `implementer`, `reviewer`, `tester`, `epic-planner`, or any other generated subagent.

## Establish scope and create the record

1. Read relevant canonical documents, existing investigation files, current Epic/TASK state, repository instructions, code, tests, and Git status/diff. Preserve unrelated user work and report contradictions that affect the question.
2. Determine whether the request authorizes `research_only` or `research_and_fix`. A request such as "investigate", "find the cause", or "analyze" is research-only. A request such as "investigate and fix" authorizes a direct fix within the investigated problem scope. The user may authorize the fix later. Never infer production/test edits from research-only wording.
3. Allocate the next monotonic `INV-NNNN` from the maximum ID under `investigations/`; do not fill gaps or reuse retired IDs. Create `investigations/INV-NNNN-<short-name>.md` from `.ai/templates/INVESTIGATION.md` before the first material experiment or change. Record the subject, area, relevant paths known so far, baseline revision and dirty working-tree disposition, scope, exclusions, and authorization.
4. Creating and updating this record is inherent in invoking the workflow. It creates no Bug, Epic, TASK, Replan, lifecycle transition, gate evidence, acceptance, or commit permission.

## Investigate flexibly

Choose the methods that best answer the question. You may inspect code and history, trace data or control flow, run existing checks, add temporary instrumentation, create bounded experiments, benchmark, profile, compare alternatives, or use other repository-appropriate tools. There is no mandatory order and no subagent route.

Keep the INV useful rather than chronological: record material methods, exact commands or sources, measurement conditions, observations, and evidence. Separate observed facts from hypotheses and conclusions. Update relevant paths and baseline context when the scope becomes clearer.

Stay within user and repository permissions. Obtain applicable authorization before production or external access, destructive actions, secret use, new dependencies, broad resource consumption, or a material scope expansion. Remove temporary instrumentation and untracked diagnostic artifacts unless the user explicitly wants a bounded artifact retained.

## Present the cause and choose an outcome

When evidence is sufficient, present a concise cause, confidence, affected code, limitations, and recommended next action. Then record exactly one current `outcome`:

- `no_action`: no repository correction or planned work is chosen. Record why and include a practical future recommendation when useful.
- `promoted`: the user chooses normal work. Invoke the applicable feature intake, bug intake, or Replan workflow and its existing approvals; after approval, write reciprocal `research_refs` in the Bug/Epic/plan/TASK and the INV's Linked Work and Outcome History. Investigation alone never changes Backlog or execution state.
- `fixed_directly`: the main agent implements and verifies the correction under the rules below.
- `unresolved`: no sufficiently supported cause exists. Record eliminated and remaining hypotheses, blockers, limitations, and the next useful experiments.

Do not claim `fixed_directly` for partial implementation or failing/unrun required checks. Record partial work and remaining remediation explicitly, keeping the current outcome `unresolved` or promoting it through normal work as the user decides.

## Fix directly when authorized

When `research_and_fix` is authorized, the main orchestrator may edit code, tests, configuration, dependencies, and ordinary documentation required to correct the investigated problem. This route does not require Task Start and invokes no implementer, reviewer, tester, or planner.

Before editing, restate the supported cause and intended correction. Ask the user only when the fix requires a material product or architecture choice, expands beyond the investigated problem, needs new authority, or has destructive/external effects. Otherwise continue under the existing authorization.

Preserve unrelated changes. Use tests or another independent oracle appropriate to the problem; for a bug or meaningful behavior change, prefer focused RED/GREEN evidence. Run verification proportionate to the actual changed and affected surface. Do not weaken checks, adapt expected behavior to a defective implementation, hide failures, or claim completion from assertions alone.

After editing, reconcile the actual diff with the authorized problem. In the INV `Direct Fix` section record:

- every added, modified, and removed path;
- what changed and why for each path;
- material behavior, interface, data, configuration, dependency, and documentation effects;
- exact verification commands and results;
- remaining risks, limitations, incomplete work, and manual checks;
- base and final revisions or commit, or a reproducible scoped-diff fingerprint while uncommitted.

Git is authoritative for the exact line diff; do not paste the full patch into the INV. Set `outcome: fixed_directly` only when the recorded verification supports the complete claimed correction.

## Reuse and lifecycle boundaries

When later intake, Replan, or Epic planning cites an `INV-NNNN`, read it before repeating research. Also look for obvious relevant INV files by subject, area, and relevant paths; present uncertain matches to the user. Check whether the recorded baseline, relevant code, or material assumptions changed. Reuse applicable cause, risk, suggested fix, and verification context; recheck only what became doubtful. Approved Bug/Epic/plan/TASK work stores `research_refs`, and the INV stores the reciprocal work IDs.

An INV is canonical research evidence, not authority to rewrite `SPEC.md`, `ARCHITECTURE.md`, accepted ADRs, Backlog priority, or approved scope. Use their normal approval rules. Direct investigation edits never satisfy Epic/TASK gates or imply user acceptance. If they make existing evidence stale, report it through normal resume and validation behavior.

Never commit merely because the investigation is complete or fixed. Follow the configured Git policy and obtain every otherwise required explicit commit authorization. Commit only the exact investigation and direct-fix paths, excluding unrelated user work.

## Return

Return the INV path and ID, question, supported cause or unresolved hypotheses, evidence summary, current outcome, direct-change and verification summary when applicable, linked work when promoted, limitations, affected existing lifecycle evidence, and the next user decision if one remains.
