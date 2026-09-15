# Local Python automation

Use the helper without reading its source. Read only the section relevant to the operation. All paths are relative to `--root` (default current directory). Helpers never call a model except explicit `role`. Read-only helpers never write. Mutating helpers execute only explicitly requested, already-approved transitions through preview/apply with backup journals and rollback; they never decide, infer, or replace a gate. No helper establishes user approval or acceptance.

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

Source mode checks manifest uniqueness, source IDs and YAML/frontmatter syntax. Project mode adds Task/Epic enums, duplicate IDs/workspaces, planned definitions, single-writer state, Backlog/workspace consistency, plus structural conformance: root `AGENTS.md` line budget and exact `CLAUDE.md` import, generated agent files UTF-8 without BOM starting frontmatter at byte zero, `DECISIONS.md`/`decisions/` ADR parity, plan Task order versus workspace TASK files, Workflow State block shape for started Tasks, investigation record structure, mutation-registry structure, and the Backlog archive invariant — no terminal rows in the live `BACKLOG.md`, and `BACKLOG-ARCHIVE.md` (when present) holds only terminal rows under `## <YYYY>` year sections. Adapter mode compares deterministic expected outputs. Inspect coverage and requires_judgment: this is not a complete semantic conformance verdict. Review protocol, test integrity, risk/scope, historical transitions, integration/mutation provenance and evidence applicability still need interpretation.

## Identifier allocation

```text
python .ai/tools/forge.py next-id --kind task|bug|inv|epic|adr|mut
```

Returns the max-plus-one identifier for the kind, the scanned canonical locations, and the current maximum. It never fills numbering gaps and never reuses retired identifiers; `mut` honors the registry's declared `next_id` when it exceeds every retained run. Row-declared kinds (`bug`, `epic`) scan the live `BACKLOG.md` and `BACKLOG-ARCHIVE.md` together, so an archived maximum still bounds allocation.

## Evidence freshness and gate inputs

```text
python .ai/tools/forge.py evidence-check execution/active/EPIC-001-example/tasks/TASK-001.md
python .ai/tools/forge.py evidence-check --epic EPIC-001
```

Reads the TASK's recorded Workflow State block, recomputes fingerprints for the recorded path sets, and reports mechanical verdicts: review freshness (`fresh`/`stale`/`insufficient`), testing currency, fast-assurance currency, and standard/fast acceptance eligibility; `--epic` aggregates all-DONE coverage, final fuzz evidence presence, and the union aggregate fingerprint. Placeholder values (`<...>`, `pending`, empty) are reported as insufficient, never guessed. Verdicts are computed, not judged: review-protocol completeness, test integrity, coverage quality, and acceptance remain orchestrator work (see `requires_judgment`).

## Review packet assembly

```text
python .ai/tools/forge.py review-packet execution/active/EPIC-001-example/tasks/TASK-001.md
```

Builds the compact Review Packet JSON from the recorded path classification, base revision, and evidence references: recomputed whole-implementation and production-surface fingerprints, bounded scoped Git diffs from the base revision to the working tree for both surfaces, missing-path and untracked-path reports, and classification warnings. The path classification is recorded input; the helper never classifies paths or judges review focus. Missing recorded inputs fail with the exact field name.

## Writing check packets

```text
python .ai/tools/forge.py checks-new .ai/local/checks-focused.json --stage task \
  --input src/service.py --input tests/test_service.py --cacheable --inputs-complete \
  --id focused --timeout 60 -- python -m unittest tests.test_service
```

Writes (or, when the file exists, extends) an approved-checks packet from explicit argv arrays and input paths without shell interpolation. The written packet is accepted by `checks --execute` unchanged; duplicate check ids are rejected.

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

Read the full neutral role contract and supply it with the exact assignment. With `--assignment-file <path>` the helper reads the complete neutral contract from `.ai/framework/agents/<role>.yaml` itself and concatenates it with the assignment exactly once into a transient prompt file that is removed after use — the contract never needs to pass through orchestrator context. `--prompt-file` remains for full manual prompts. A missing, malformed, or ID-mismatched contract fails before any model invocation. Keep prompt and assignment files private, in the project, and remove them after use. Output is bounded; empty/error/malformed Claude results fail. The orchestrator still validates protocol completeness and packet integrity. Legacy `.mjs` launchers remain supported for projects without Python; new helper logic lives in Python.

## Record scaffolding and Backlog rows

```text
python .ai/tools/forge.py inv-create --subject "Slow login" --area auth --paths src/login.py
python .ai/tools/forge.py backlog add-bug --problem "Crash on save" --severity high --priority P0
python .ai/tools/forge.py backlog update-row --id BUG-001 --set Status=SCHEDULED --set "Scheduled TASK=TASK-001"
python .ai/tools/forge.py backlog update-row --id EPIC-002 --set Priority=P0 --move-before EPIC-001
python .ai/tools/forge.py backlog archive-row --id EPIC-003
python .ai/tools/forge.py backlog archive-all
python .ai/tools/forge.py backlog stale-rows --older-than 90
```

`inv-create` allocates the next `INV-NNN`, instantiates the canonical template, and records the baseline revision and dirty working-tree disposition; pass `--name` when the subject has no ASCII slug. `backlog add-bug` inserts exactly one `OPEN` Defect Queue row from the approved fields (the next `BUG-NNN` is allocated automatically; pass `--id` to use an explicit approved identifier). `backlog update-row` changes only the named cells (`--set Column=Value`, repeatable) and optionally moves one row before another; header, separator, and unrelated rows stay byte-identical, and `|` in values round-trips through escaping. A `--set` that leaves the row in a terminal status archives the row in the same mutation — apply the other cell edits first, then set the terminal Status alone. `backlog archive-row` moves one legacy terminal row verbatim to `BACKLOG-ARCHIVE.md` (one-time backfill; refuses non-terminal rows); `backlog archive-all` moves every legacy terminal row in one preview/apply transaction and reports without a mutation when none qualify. All mutating commands default to a preview; apply only the reviewed `--apply TOKEN`. The user owns priority and row order — never reorder without an explicit decision.

`backlog stale-rows` is read-only: it reports live non-terminal rows whose last change in the Git history of `BACKLOG.md` is older than `--older-than` days, keyed by the exact padded row identity so one ID never matches another's history; rows without Git history are listed under `unknown` instead of being guessed. The report is suggestion-only mechanical evidence — closing any row stays an explicit approved user transition.

## Lifecycle transitions and acceptance

```text
python .ai/tools/forge.py transition task execution/active/EPIC-001-example/tasks/TASK-001.md --to "IN PROGRESS"
python .ai/tools/forge.py transition epic EPIC-001 --to VALIDATING
python .ai/tools/forge.py epic-start EPIC-001
python .ai/tools/forge.py epic-complete EPIC-001
python .ai/tools/forge.py accept-record execution/active/EPIC-001-example/tasks/TASK-001.md \
  --by user --decision-ref "chat decision 2026-09-10" --notes "verified manually" --resolve-bug BUG-001
```

Every mutating command defaults to a preview (exact diffs, preconditions, a token bound to current inputs) and executes only with `--apply TOKEN`; a changed input invalidates the token. `transition task` rewrites only the frontmatter status and Workflow State `current_gate`/timestamps; it validates enums, transition legality per `contracts.yaml`, the single-writer invariant, and project consistency, and refuses `DONE` (use `accept-record`). `transition epic` edits exactly one Backlog row; terminal targets (`COMPLETED`, `CANCELLED`) move the row to `BACKLOG-ARCHIVE.md` in the same mutation. `epic-start`/`epic-complete` move the workspace directory and update the Backlog as one logical transition with rollback, including the move-back; completion archives the Epic's row atomically with the workspace move, so the live Backlog never retains a terminal row. `accept-record` appends only the explicitly supplied acceptance facts and refuses missing decision inputs; `--resolve-bug` resolves exactly one named `SCHEDULED` Bug as an explicit input and archives its row in the same transaction. Backups live under `.ai/local/lifecycle-transaction/`; a caught failure restores everything, an interrupted operation leaves the journal, and recovery never overwrites later user edits. The helpers execute decisions; authorization, semantic gates, and acceptance remain with the user and orchestrator.

## Search index

```text
python .ai/tools/forge.py query "auth token latency" --kind INV,ADR --area auth --since 2026-06
python .ai/tools/forge.py index rebuild
python .ai/tools/forge.py index status
```

`query` returns ranked pointers — identifier, kind, canonical path, BM25 score, and a short snippet — never record bodies. It searches one derived index over all durable records (ADR, INT, INV, TASK, plan, plus live and archived Backlog rows, including `execution/completed/`), so results rank against each other across kinds. Filters: `--kind` (comma-separated `TASK,INV,INT,ADR,PLAN,EPIC,BUG`), `--area` (exact recorded area), `--since` (`YYYY-MM` or `YYYY-MM-DD` floor on recorded dates; undated records drop out only when the filter is set). The index lives at `.ai/local/index.db`, is rebuilt automatically whenever missing, stale, or corrupt, and is refreshed incrementally (modification time plus content hash) before every query — no maintenance ritual. It is a cache, never evidence: read the canonical file behind a result before relying on it. Results are fully offline, standard-library only, and deterministic; a Python build without SQLite FTS5 reports search as unavailable and nothing else breaks. Read explicit references first; query only surfaces mechanical matches.

## Scoped commits

```text
python .ai/tools/forge.py commit-scoped execution/active/EPIC-001-example/tasks/TASK-001.md --authorized
```

Stages exactly the TASK's recorded `review_packet.changed_paths` plus the TASK file (or an explicit `--paths` list), reports unrelated working-tree changes it excludes, and proposes the commit message. Under `manual` policy or without `--authorized` it commits nothing and reports what it would stage. Under `auto_commit_after_acceptance` with `--authorized` it requires the TASK to be `DONE` and commits only the staged scope. It never uses `git add -A`; unrelated user work stays out of the commit by construction.

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
