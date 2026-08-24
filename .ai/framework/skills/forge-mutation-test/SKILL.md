---
name: forge-mutation-test
description: Run or analyze an explicitly requested lifecycle-independent mutation-testing audit, preserve a durable MUT record, and never change development state automatically.
---

# Run On-Demand Mutation Testing

## Establish the independent request

1. Require an explicit user request and exact repository scope. Mutation testing may run with no Epic or TASK and during any Epic or TASK status.
2. Distinguish three requests:
   - a new metrics-only run, which is the default;
   - a new run with explicitly authorized immediate analysis;
   - deferred analysis of one existing `MUT-NNNN` record.
3. Read `.ai/project.yaml`, the mutation contracts and templates, the independent registry and requested run when present, repository/build/CI evidence, relevant code and tests, and Git state. Do not treat Backlog, Epic or TASK status as an invocation precondition.
4. Require exact production paths, test paths, exclusions, baseline and backend commands, backend identity/version evidence, execution constraints, time/worker budget, and an exact scoped fingerprint including dirty diff and declared dependency inputs. Never invent a command or widen scope.

## Allocate and persist every attempt

For a new run, lazily create `quality/mutation-testing/registry.yaml` from the framework template and `runs/` only when absent. Allocate the next monotonic `MUT-NNNN` without reusing gaps. Stage the registry update and new run record together, preserving every required field even when setup or execution later fails. Agents never edit these records; the orchestrator owns atomic writes.

Do not create a Markdown report. Keep raw backend artifacts untracked by default. Retain compact normalized evidence in the run record or an explicitly retained structured artifact with path and checksum.

## Run the fast mechanical stage

1. If a separately approved backend configuration or reproducible command is unavailable, record `SETUP REQUIRED` and the exact missing capability. Do not install a package or edit dependency/configuration files; setup requires a separate user-authorized repository change.
2. Build a complete Mutation Run Packet and invoke `mutation-runner` at fast tier.
3. Validate the returned run ID, fingerprint checks, commands, exit evidence, metrics, artifact paths and checksums. Malformed or mismatched output makes the attempt `INCONCLUSIVE`; do not infer missing values.
4. Atomically update the same run record with baseline, outcome, normalized metrics, artifact retention and `analysis.status`.

Metrics-only is the default. Without explicit analysis authorization, set `analysis.authorized: false` and `analysis.status: not_requested`, present the compact metrics, persist the record, and stop without invoking a strong model.

## Invoke strong analysis only when authorized and useful

For immediate analysis, continue only when the user explicitly authorized it and current normalized results contain surviving, no-coverage, or explicitly configured candidates. Skip the analyzer and record `skipped_no_candidates` when all mutants are killed or no configured candidate exists. Also skip it after baseline failure, SETUP REQUIRED, cancellation, unusable or stale artifacts, or zero analysis budget.

For deferred analysis, read the requested existing run, verify its fingerprint and retained normalized artifact checksum against current scope, and never repeat the mutation campaign. If evidence is stale or missing, record `stale` or `blocked` and ask whether the user wants a new run; do not invoke the analyzer.

Build one bounded Analysis Packet and invoke `mutation-analyzer` at strong tier. Validate classifications, confidence, locations, relevant tests, rationales, candidate counts, budget, fingerprint and artifact checksum. Record `completed` or `partial`, compact findings and exact remaining count in the same `MUT-NNNN` file. Never allocate another run ID for deferred analysis.

## Preserve lifecycle isolation and route later decisions

Starting, running, cancelling, blocking, recording or analyzing mutation testing must not create or change a Bug, Epic, TASK, Replan, priority, lifecycle status, review result, test result, validation/fuzzing evidence, acceptance gate, commit permission or framework quality gate. Mutation outcomes and analysis statuses belong only to the independent run record.

Present scope, fingerprint, commands, budgets, backend version, baseline, normalized metrics, analysis invocation or skip rationale, compact findings, limitations and record path. Do not automatically remediate anything.

Only after a separate user request may accepted follow-up use an existing Forge workflow: current unaccepted Task feedback, bug intake for an observable defect in accepted code, Replan into compatible work, or a new test-hardening Epic. Update `disposition` with informational references only after that workflow approves the identities; mutation history never controls their state.
