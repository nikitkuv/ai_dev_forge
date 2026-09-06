# Local Python automation

Use the helper without reading its source. Read only the section relevant to the operation. All paths are relative to `--root` (default current directory). Helpers never call a model except explicit `role`; they never change Task/Epic status or infer approval.

## Setup

Python 3.11+ is supported. Create an isolated environment and install pinned dependencies:

```text
python -m venv .forge-venv
.forge-venv/Scripts/python -m pip install -r .ai/tools/requirements.txt
```

On POSIX use `.forge-venv/bin/python`. Commands below use `python` to mean that environment's interpreter. If Python/dependencies are absent, obtain installation authorization or use the manual workflows; Python is not required for native agent execution. Copying `.ai/` includes these tools. No global Forge installation is needed. Ignore `.ai/local/`, `.forge-venv/` and `__pycache__/` in the consuming project's Git configuration.

## Context and sections

```text
python .ai/tools/forge.py context
python .ai/tools/forge.py context --offset 30 --limit 30
python .ai/tools/forge.py section execution/active/EPIC-001-example/tasks/TASK-001-example.md
python .ai/tools/forge.py section execution/active/EPIC-001-example/tasks/TASK-001-example.md --heading "Verification Plan"
```

Context returns parsed metadata, content hashes, relevant paths, Git status and explicit errors. It does not interpret dependencies or choose the next Task. Read all inventory pages and require the same inventory_fingerprint across them; restart inventory if files changed. Use Backlog priority/row order, not path order. Completed work is excluded unless `--include-completed` is supplied. Read active evidence and relevant dependencies/INV records, not every planned Task body. Linked paths are rejected for manual inspection. Git status uses a per-command safe.directory for the explicitly selected root and disables fsmonitor; it changes no global Git settings.

Section without `--heading` lists headings and line numbers. Selection matches exact ATX headings, includes nested headings and returns all duplicates. Fenced-code headings are ignored. `--offset`/`--limit` paginate characters; continue until `next_offset` is null, verifying source_sha256 remains unchanged. Missing sections fail explicitly. This is a source extractor, not a summary or full Markdown parser.

## Fingerprints

```text
python .ai/tools/forge.py fingerprint src/service.py tests/test_service.py requirements.lock
```

The `forge-files-v1` fingerprint includes sorted normalized paths, exact file bytes, executable flags and explicit missing files (deletions). Inputs must be individual files; include additions and dependency/configuration files. It does not discover dependency closure, classify production paths or replace the base revision and reproducible Git diff. Existing evidence using another algorithm must be refreshed. Compare within the same platform when executable semantics differ. Changes while hashing fail; writes after hashing still require a fresh check before a gate.

## Validation

```text
python .ai/tools/forge.py validate
python .ai/tools/forge.py validate --project --adapters
```

Source mode checks manifest uniqueness, source IDs and YAML/frontmatter syntax. Project mode adds Task/Epic enums, duplicate IDs/workspaces, planned definitions, single-writer state, Backlog/workspace consistency. Adapter mode compares deterministic expected outputs. Inspect coverage and requires_judgment: this is not a complete semantic conformance verdict. Review protocol, test integrity, risk/scope, historical transitions, integration/mutation provenance and evidence applicability still need interpretation.

## Adapter rendering and recovery

```text
python .ai/tools/forge.py adapters --diff
python .ai/tools/forge.py adapters --apply PREVIEW_TOKEN
python .ai/tools/forge.py adapters --apply PREVIEW_TOKEN --approve-collision AGENTS.md
python .ai/tools/forge.py adapters --recover
```

Preview is read-only and returns exact diffs, collisions and a token bound to current inputs, outputs and lock. Apply only the reviewed token; approve each collision only with existing user authority. Renderer validates YAML/TOML, quotes arbitrary descriptions/instructions safely, copies skill resources, preserves unlisted files and updates `.ai/framework.lock` last. Its namespaced `python_adapter_state` preserves unrelated lock fields. Old/unknown lock formats require collision review rather than guessed ownership. Retired/disabled outputs are reported and preserved for a separately reviewed migration.

Writes use per-file atomic replacement and a backup journal at `.ai/local/adapter-transaction/`. A caught failure rolls back written files; a crash can leave a partial set and journal, so consumers must not use adapters until recovery completes. Recovery refuses to overwrite subsequent user edits. Never run two syncs concurrently. No multi-file filesystem transaction is claimed. Do not delete a failure journal to bypass recovery.

## Approved checks and reuse

The check packet is an explicit execution request, not proof of user authorization. Use only exact commands already approved in the Verification Plan. Commands use argument arrays, never an implicit shell. They retain the caller's OS permissions; this helper is not a sandbox. Network and writes still require applicable authority.

```json
{
  "schema_version": 1,
  "stage": "task",
  "inputs": ["src/service.py", "tests/test_service.py", "requirements.lock"],
  "inputs_complete": false,
  "cacheable": false,
  "checks": [
    {"id": "focused", "argv": ["python", "-m", "unittest", "tests.test_service"], "cwd": ".", "timeout_seconds": 60}
  ]
}
```

```text
python .ai/tools/forge.py checks approved-checks.json --execute
python .ai/tools/forge.py checks approved-checks.json --execute --reuse
```

Reuse requires both cacheable and inputs_complete explicitly true. Approve that only for deterministic checks whose complete dependencies, test discovery inputs, tool environment, lockfiles and configuration are covered. New discovered files must enter the path set. Disable reuse for external services, mutable databases, nondeterminism, incomplete dependency knowledge or side-effect validation. The key covers packet, input fingerprints, launch executables, helper code and environment hash (not exposed values). Integrity of retained logs is checked before reuse. Changes to the scoped files during execution invalidate the result. Failures are not cached, checks stop on first failure and no automatic retries occur. `stage: epic` always executes, ignoring reuse.

Success returns compact evidence and log references. Inspect warning tails and required log content; raw logs can contain project data and remain local. Failed output is bounded. Copy exact commands/results/fingerprints into the canonical TASK/plan; disposable local logs alone cannot satisfy a durable gate. Reuse only command evidence: reviewer/tester judgment, current fast assurance, acceptance and Epic Validation are unchanged. Never reuse a GREEN result as RED evidence.

## External roles

```text
python .ai/tools/forge.py role --orchestrator claude --role reviewer --prompt-file .ai/local/review-prompt.md
```

The existing approved role_execution.mode determines provider. Native mode stays native. The call performs one bounded preflight; use `--preflight` separately only for diagnosis, not before every role call. Timeout defaults to 900 seconds and can be reduced with `--timeout`. Set FORGE_CODEX_BIN or FORGE_CLAUDE_EXECUTABLE for an explicit installed executable. Windows native executables are preferred; known npm wrappers run through their Node entrypoint, never shell interpolation. No installation, authentication, provider fallback or persisted model session is performed.

Read the full neutral role contract and supply it with the exact assignment. Keep prompt files private, in the project, and remove them after use. Output is bounded; empty/error/malformed Claude results fail. The orchestrator still validates protocol completeness and packet integrity. Legacy `.mjs` launchers remain supported for projects without Python; new helper logic lives in Python.

## Bounded authorization

Strict mode is the default. To avoid repeating Task Start questions, a user may explicitly authorize exact approved definitions in `.ai/project.yaml`:

```yaml
automation:
  authorization:
    mode: bounded_task_starts
    decision_ref: "plan.md#recorded-user-decision"
    approved_by: "user"
    expires_at: "2026-12-31T23:59:00+03:00"
    task_starts:
      - task_path: execution/active/EPIC-001-example/tasks/TASK-001-example.md
        definition_fingerprint: "<forge-files-v1 fingerprint of this exact TASK file>"
```

Do not invent or auto-enable this grant. `task-start-check <path>` checks definition identity and expiration; the orchestrator still verifies actual user authorization, dependencies, blockers, scope and track eligibility. Changing the definition invalidates it. It grants only Task Start, never acceptance, commit, Replan or Epic Start. The script does not transition state.

## Budgets and metrics

`budget <files...>` reports bytes, lines and a characters/4 token estimate, explicitly not a model tokenizer or billed usage. Use it to keep shared routers compact and detect prompt growth. Do not discard required evidence merely to hit a budget.

`metrics-record <event.json>` stores only supplied metrics under `.ai/local/metrics/`; `metrics` aggregates by track/stage without a model. Supported fields: task, track, stage, model, duration_seconds, input_tokens, output_tokens, cached_input_tokens, reused_checks, review_iterations, escalation_reason, post_acceptance_fix. Missing usage stays unknown, never estimated as zero cost. Do not put prompts, credentials or repository content in metrics. Compare similar task classes and quality outcomes before changing role policies.
