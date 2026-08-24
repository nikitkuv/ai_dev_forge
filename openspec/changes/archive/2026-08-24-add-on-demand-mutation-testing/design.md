## Context

Forge currently separates orchestration, deterministic test execution, strong review, canonical lifecycle ownership, and generated Codex/Claude adapters. Its tester is fast and mechanically executes selected checks; strong roles perform independent reasoning. Agents cannot invoke one another, only the orchestrator changes canonical state, concrete commands must come from repository or user evidence, and optional capabilities must not introduce mandatory dependencies. See `proposal.md` and `specs/on-demand-mutation-testing/spec.md` for the new behavior.

Mutation testing has two distinct workloads: a potentially long but mechanical backend campaign, and an optional semantic review of survivors and uncovered code. Combining both in the orchestrator would consume its context; combining both in one strong agent would spend strong-model tokens while external test processes run.

## Goals / Non-Goals

**Goals:**

- Preserve a small orchestrator context through structured packets, summaries, and artifact paths.
- Make fast execution and strong semantic analysis independently invocable and budgeted.
- Preserve reproducibility even for dirty working trees and failed attempts.
- Keep durable mutation history project-owned and separate from Backlog and execution state.
- Remain backend-neutral while allowing repository-specific adapters such as Python plus `mutmut`.

**Non-Goals:**

- Implement a mutation engine, generate permanent test code, or automatically remediate findings.
- Add a lifecycle transition, acceptance gate, quality-profile requirement, hook, CI mandate, or default external dependency.
- Guarantee that every equivalent mutant is decidable; classifications carry confidence and may remain unresolved.
- Retain large raw backend artifacts in Git by default.

## Decisions

### 1. Use one skill and two neutral agent roles

Add `forge-mutation-test` as the only user-facing workflow. The orchestrator invokes `mutation-runner` and, when authorized and applicable, `mutation-analyzer`; the agents never invoke each other.

`mutation-runner` uses the fast tier and `runtime_artifacts_only` writes. It validates the packet and fingerprint, runs the ordinary baseline, invokes the approved backend under resource limits, normalizes tool-specific output, and returns a compact summary plus artifact manifest.

`mutation-analyzer` uses the strong tier and `runtime_artifacts_only` writes. It receives a separate Analysis Packet containing the current run fingerprint, normalized result path, source and test scope, risk hints, prioritization rules, and analysis budget. It reads only relevant production code, tests, and artifacts, then produces classifications and a compact finding summary.

Alternative considered: one strong mutation agent. Rejected because the strong model adds no value while the mutation backend and test runner consume most elapsed time. Alternative considered: fast runner plus orchestrator analysis. Rejected because large or complex survivor sets pollute the orchestrator context and duplicate a reusable specialist contract.

### 2. Make semantic analysis opt-in and independently repeatable

A bare mutation request performs a metrics-only run. Immediate analysis requires an explicit analysis option or equivalent user instruction. Deferred analysis targets a recorded `MUT-NNNN` run and reuses its normalized artifacts when their fingerprint and integrity checks remain current.

The orchestrator skips the analyzer even after authorization when the runner reports no configured candidates. It also skips on baseline failure, setup-required, unusable or stale artifacts, cancellation, or an exhausted zero budget. Candidate analysis is bounded; excess candidates remain recorded as unanalyzed rather than silently dropped.

Alternative considered: automatically analyze every survivor. Rejected because users may want only a score or trend and strong-model cost is material.

### 3. Store independent project-owned records under `quality/mutation-testing/`

The capability creates this directory lazily on first request:

```text
quality/mutation-testing/
├── registry.yaml
├── runs/
│   └── MUT-0001.yaml
└── artifacts/
    └── MUT-0001/          # optional or ignored raw/runtime material
```

`registry.yaml` is a compact index and next-ID authority. Each run file is the durable record for both execution and any later analysis. The orchestrator owns atomic allocation and record updates; agents write only temporary/runtime artifacts and return their paths and checksums. Raw logs and backend-native databases are not tracked by default; compact normalized evidence required to understand the result is retained in the run record or an explicitly retained structured artifact.

The framework manifest declares `quality/mutation-testing/` project-owned and optional. Bootstrap and adapter sync do not create or overwrite it. Mutation history is not a source of Epic or TASK lifecycle truth.

Alternative considered: append every run to a single Markdown report. Rejected because it becomes difficult to validate, update deferred analysis atomically, and consume programmatically. Alternative considered: store records under `execution/`. Rejected because that implies lifecycle coupling.

### 4. Use backend-neutral configuration and normalized results

The project template exposes an empty optional mutation-testing configuration for evidenced commands, backend identity/version command, supported scope syntax, result adapter, timeouts, worker limits, and artifact policy. Absence is valid and produces `SETUP REQUIRED` only when the user requests a run. No mutation package is installed by bootstrap, migration, adapter sync, framework checks, or audit execution.

The runner normalizes at least: generated, killed, survived, no-coverage, timeout, invalid/error, duration, backend-reported score, and candidate references. Tool-specific score semantics remain labeled rather than recomputed as a falsely universal metric.

Python `mutmut` is a supported configuration example, not a framework dependency. Platform constraints such as a backend requiring WSL are explicit execution constraints and may block only that requested run.

Alternative considered: hard-code `mutmut`. Rejected because Forge supports multiple project profiles and languages and must remain usable with no optional CLI dependency.

### 5. Use exact packets and fingerprints across both roles

The Mutation Run Packet contains run ID, repository root, exact source/test paths, exclusions, base revision, scoped tree or diff fingerprint, baseline and backend commands, tool evidence, environment constraints, time/worker budgets, and runtime artifact destination.

The runner recomputes the scoped fingerprint before baseline, before mutation execution, and on completion. A mismatch produces `INCONCLUSIVE`. The analyzer receives the runner's fingerprint and artifact checksums and refuses stale or mismatched evidence.

Dirty working trees are allowed because the feature is independent of development state, but the exact scoped diff must be hashed. Changes outside the approved scope do not invalidate the run unless they are declared cache, dependency, fixture, or environment inputs.

### 6. Keep remediation outside the mutation workflow

The mutation skill records results and asks no lifecycle question unless the user separately requests disposition. A later user decision uses the existing bug, feature, or Replan skill. An unaccepted current TASK may absorb an approved finding only through its existing feedback rules; accepted-code defects use bug intake; broad test hardening uses an Epic. Optional references may be written into the mutation record after that separate workflow approves identities.

The record's own `run.outcome`, `analysis.status`, and `disposition` fields are mutation-history metadata and never map to framework lifecycle statuses.

## Risks / Trade-offs

- [Backend output formats differ or change] → Isolate parsing in backend adapters, retain backend name/version, validate normalized schemas, and report unsupported output as blocked rather than guessing.
- [Mutation runs are CPU- and time-intensive] → Require explicit scope and budgets, default to metrics-only, support cancellation and partial outcomes, and never start from implicit lifecycle routing.
- [Equivalent mutants are generally undecidable] → Require confidence and rationale, support `likely_equivalent` and `unresolved`, and avoid treating raw survivors as confirmed defects.
- [Runtime artifacts may be large or sensitive] → Retain only compact records by default, make raw retention explicit, prohibit network upload, and record artifact retention and checksums.
- [Source changes while a campaign runs] → Recompute scoped fingerprints and mark results inconclusive instead of attaching them to a mixed revision.
- [Two roles add framework surface] → Keep packet schemas explicit, prohibit agent-to-agent calls, and cover neutral/generated parity and role policy in conformance tests.
- [Strong analysis may still be expensive] → Require explicit authorization, skip when no candidates exist, cap candidate count, prioritize risk-bearing operators and paths, and support deferred batch analysis.

## Migration Plan

1. Add neutral contracts, templates, the optional project-owned path, and default-empty configuration without creating mutation state in existing projects.
2. Add the skill and two agent definitions, then regenerate both platform adapters from neutral sources.
3. Extend framework verification and migration tests so existing project-owned mutation records survive upgrades and unconfigured projects remain dependency-free.
4. Update framework documentation and runbook with setup-required, metrics-only, immediate-analysis, and deferred-analysis examples.
5. Roll back by removing the newly managed skill/agent IDs and generated adapters; preserve any `quality/mutation-testing/` records as project-owned data.
