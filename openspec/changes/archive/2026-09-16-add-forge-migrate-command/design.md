# Design: add-forge-migrate-command

## Context

See `proposal.md` for motivation. The relevant current state:

- `forge_adapters.py` already implements the deterministic transactional pattern this design reuses: pure-function `render(root)` over framework templates plus project config, `preview()` binding a token to inputs/observed/candidate/lock, and `apply()` guarded by `Transaction` (backup journal, post-backup recheck, rollback on failure, explicit `recover()`).
- `forge_core.py` provides `Transaction`, `snapshot`/`digest`, `within` path safety, YAML loading with duplicate-key rejection, and `validate`.
- Root routers are already generated artifacts: `AGENTS.md` = staged template + `{{ custom.router_shared }}` overlay; `CLAUDE.md` = exact `@AGENTS.md` import. A project with `.ai/custom/router-shared.md` needs zero judgment to migrate its routers.
- `.ai/framework.lock` today records generated adapter outputs (`python_adapter_state`) and preserves unknown fields; it does not record the bundle itself.
- The current migration is an agent-driven flow documented in `MIGRATION.md` (long kickoff prompt) and `.ai/MIGRATE.md` (agent router), backed by the `forge-migrate-framework` skill that performs every step by interpretation.
- Python tools are optional for consumers (v4.9); the manual flow must remain available.

## Goals / Non-Goals

**Goals:**

- One deterministic command for the full migration transaction of a modern consumer project, with the LLM reduced to relaying findings and collecting explicit decisions.
- Preview that is a pure function of repository state and covers the complete final state — bundle, configuration, routers, adapters, lock — before any write.
- Reuse the established preview/apply-token and journal/rollback semantics unchanged in spirit.

**Non-Goals:**

- No network access, git cloning, provider installation, or authentication inside the Python tools; staging stays a shell one-liner.
- No automatic extraction of project content from legacy hand-written or platform-specific routers; that judgment work stays with the skill/user and enters the command only through an explicit overlay input.
- No integration-schema migration, canonical edits, backfill execution, or any post-migration remediation inside the migrate transaction; those remain separate gates (backfills are reported with exact commands, not run).
- No new migration behavior for consumers that never stage the new bundle; the manual documented path remains the fallback.

## Decisions

### D1. The command lives in the staged bundle and is the single entry point

`python .ai-next/tools/forge.py migrate` runs from the project root against the active `.ai/` and the staged `.ai-next/`. The old bundle needs nothing — first deterministic migration happens when migrating *to* a version that ships the command. Alternatives considered: running the old bundle's tool (impossible — it lacks the command), or a standalone script outside `.ai/tools/` (duplicates transaction/snapshot machinery and creates a second entry point).

Subcommands/flags: bare `migrate` (preview), `--diff` (adds unified diffs), `--apply TOKEN`, `--set key=value` (repeatable), `--router-shared PATH`, `--approve-collision PATH` (repeatable), `--recover`. Exit codes follow the existing convention (0 ok, 1 findings/failed checks, 2 usage/system error).

### D2. Preview is a pure function via a parameterized renderer

`forge_adapters.render(root)` becomes `render(bundle_root, root)`: framework sources (manifest, contracts, templates, neutral agents, skills) read from `bundle_root`, project state (`.ai/project.yaml`, `.ai/custom/`) from `root`. The existing `adapters` command calls `render(root_ai, root)` with unchanged observable behavior. Migration preview composes the *virtual* post-migration state — staged bundle files, updated project config, overlay, then the rendered routers/adapters/launchers and the new lock — entirely in memory, and derives the token from all inputs plus observed on-disk bytes, exactly like `adapters.preview`.

This avoids temp-directory mutation and two-phase applies; the alternative (write bundle first, then run `adapters apply` as a second transaction) was rejected because it creates a visible intermediate state and two tokens for what must be one approval.

### D3. One `Transaction("migrate")` covers the whole change set

The update map contains: every framework-owned replacement, proven-obsolete deletions (entries with `None` after-value are not possible in the current journal — deletions are journaled as file-with-backup → unlink on write; `Transaction.write` already restores by backup and removes added files on rollback), the updated `.ai/project.yaml`, rendered `AGENTS.md`/`CLAUDE.md`/adapters/launchers, and the lock written last. Post-write phases run inside the same command: `validate` (against the new bundle's rules), protected-path re-hash comparison, then `.ai-next/` removal on success. Any failure triggers journal rollback and leaves `.ai-next/` intact.

The transaction guard lives at `.ai/local/migrate-transaction`; `.ai/local/` is project-owned and never part of the replacement set, so the journal survives the bundle swap.

### D4. `migrations.yaml` is the version contract

New framework-owned file `.ai/framework/migrations.yaml`:

```yaml
schema_version: 1
versions:
  "4.12":
    config_additions:      # mechanical: key -> default added when absent, shown in preview
      automation.authorization.mode: strict
    config_decisions:      # blocking until --set; never auto-written
      - key: role_execution.mode
        suggest: native_subagents   # informational only
    breaking: []
    backfill_commands:      # advisory, quoted verbatim in findings, never executed
      - description: Archive legacy terminal Backlog rows
        command: python .ai/tools/forge.py backlog archive-all
```

Entries apply strictly for versions in `(old, new]`. `--set` accepts only keys declared as decisions in that range (plus explicit allowlist of safe keys like `documentation_language`) — arbitrary config injection is refused. Historical entries (4.3–4.11) are backfilled from the existing `MIGRATION.md` prose so direct jumps from older versions compute their decisions mechanically; prose remains human documentation. Alternative considered — deriving findings from prose at runtime — rejected as non-deterministic by definition.

### D5. Lock gains `bundle_state`; deletion requires provenance

The new lock records `bundle_state: {schema_version: 1, files: {<framework-owned path>: sha256}}` alongside the existing `python_adapter_state`, preserving unknown fields. Deletion rule: a file under an old framework-owned path is deleted only if the prior lock's `bundle_state` recorded its hash and the current bytes still match. Otherwise it is preserved byte-for-byte and reported as an advisory. Consequence: the first migration onto a `bundle_state`-aware version never deletes unknown files — conservative by design (matches "never infer permission to delete"). `__pycache__` directories are ignored in both inventory and findings.

### D6. Router overlay: block, then accept an explicit input

If `.ai/custom/router-shared.md` exists it is carried byte-for-byte into the rendered routers. Otherwise preview emits blocking finding `router_extraction_required`; the only input is `--router-shared PATH` (file validated: non-empty, within root, no unresolved template markers, rendered router within the line budget). Legacy `.ai/custom/codex-router.md` / `claude-router.md` block with a reconcile-first finding, mirroring the existing renderer guard. Alternative considered — deterministic overlay recovery by diffing the old generated `AGENTS.md` against a render of the old bundle's template — deferred as YAGNI; the extraction is one-time per legacy project and the skill already does it.

### D7. Skill and documents become the thin shell

- `forge-migrate-framework` SKILL.md is rewritten: stage `.ai-next/` if absent (shell one-liner), run `migrate --diff`, relay findings verbatim, collect `--set` / `--router-shared` / collision decisions (the only judgment work), apply, report. It must not re-implement migration steps.
- `MIGRATION.md` loses the long kickoff prompt; the "Запуск" section becomes the one-liner (sparse clone && migrate for the GitHub path; copy + migrate for local) plus skill-invocation guidance.
- `.ai/MIGRATE.md` shrinks to a command-driven agent router: verify layout, run the command, interpret named findings, keep the manual no-Python path as an explicitly marked fallback.
- `.ai/tools/USAGE.md` documents the new command; `README.md` updates its migration references.

### D8. Module layout

New `.ai/tools/forge_migration.py` holding `preview_migrate(root, staged_root, ...)`, `apply_migrate(...)`, `recover_migrate(root)`, integration classification, and contract loading — mirroring how `forge_adapters.py` / `forge_lifecycle.py` isolate concerns. `forge.py` only wires the subcommand. `forge_core.py` receives only genuinely shared additions (e.g., a directory-tree helper if needed), keeping it read-only-generic.

## Risks / Trade-offs

- [First migration deletes nothing unknown] → Stale files from retired framework paths accumulate once; acceptable and visible as advisory findings. Once `bundle_state` exists, the *next* migration can prove and remove them.
- [`render` parameterization regresses adapter sync] → The `adapters` command's observable behavior and its existing tests must pass unchanged; the parameterization is a pure source-root split with the default preserving today's call shape.
- [Windows: removing `.ai-next/` while the running script lives inside it] → The interpreter has fully loaded the script before deletion; CI covers Windows. If removal fails, it is reported as a non-fatal follow-up instruction rather than a rollback trigger.
- [Historical `migrations.yaml` entries drift from prose] → Entries are derived once from the current `MIGRATION.md` sections and reviewed in this change; future releases update the contract first, prose second.
- [Contract key paths (`a.b.c`) vs YAML structures] → `--set` parses dotted paths against the config mapping only; no eval, no type coercion beyond scalars already present in the template defaults.
- [Token size/UX of a full-bundle preview] → Preview lists per-file hashes and sizes with diffs only under `--diff`, matching the existing `adapters` output style; no file bodies are emitted by default.

## Migration Plan

This change ships as the next framework version (manifest `4.12.0` plus the new contract's `4.12` entry). Adoption: consumers stage a `4.12` bundle and run the command; consumers on older bundles are unaffected until they stage it. Rollback for the framework itself is the ordinary release process; for a consumer, the transaction journal and documented manual path remain the recovery story. After the release, the old long-prompt instructions are deleted from `MIGRATION.md` in the same change so there is exactly one canonical entry point.
