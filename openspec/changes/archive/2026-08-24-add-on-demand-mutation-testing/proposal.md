## Why

Forge can execute ordinary and fuzz tests, but it cannot independently measure whether an existing test suite detects plausible changes in production code. Users need an explicitly requested mutation-testing audit that can run at any repository state without affecting Epic, TASK, Backlog, review, testing, validation, or acceptance state.

## What Changes

- Add a user-invoked `forge-mutation-test` workflow that runs mutation testing for an exact user-approved source and test scope.
- Add a fast `mutation-runner` role that performs baseline tests, invokes a configured mutation backend, normalizes results, and writes runtime artifacts without changing tracked source or tests.
- Add a strong `mutation-analyzer` role that is invoked only after explicit analysis authorization and only when actionable candidates exist.
- Add independent, project-owned `MUT-NNNN` records and a registry that preserve fingerprints, scope, commands, budgets, metrics, analysis state, findings, and optional later dispositions.
- Keep mutation testing entirely outside the development lifecycle: it creates no implicit Bug, TASK, or Epic, changes no lifecycle status, satisfies no quality gate, and invalidates no existing evidence.
- Support metrics-only runs, immediate conditional analysis, and deferred analysis of an existing current run without repeating the mutation campaign.
- Treat backend installation or configuration as a separately authorized repository change; a mutation-test request alone never installs tools or edits configuration.

## Capabilities

### New Capabilities

- `on-demand-mutation-testing`: Explicit, lifecycle-independent mutation campaigns, conditional semantic analysis, durable run history, and safe routing of user-approved follow-up work.

### Modified Capabilities

None.

## Impact

- Neutral framework manifest, contracts, agent definitions, skill definitions, templates, documentation, migration behavior, and dual-platform adapter generation.
- Framework verification tests for ownership, generated parity, role policies, registry schema, lifecycle isolation, and mutation workflow routing.
- Consumer projects may opt into a language-appropriate mutation backend; Python support can use a configured tool such as `mutmut`, but no backend is installed or required by default.
