# Proposal: add-forge-migrate-command

## Why

Framework migration today is agent-driven end to end: the user manually stages `.ai-next/`, pastes a long English prompt into Codex or Claude Code, and the LLM performs discovery, hashing, router merging, configuration reconciliation, and the replacement itself by following prose instructions. The flow is token-heavy, non-deterministic, and its safety depends on the model re-deriving the same steps every time. Since the overlay architecture (`.ai/custom/router-shared.md`) and the deterministic transaction machinery (`Transaction`, preview/apply tokens, `render`) already exist, a modern-project migration is pure mechanics and can run as one Python command with the LLM reduced to relaying findings and collecting the few decisions that genuinely require judgment.

## What Changes

- Add a `migrate` subcommand to `.ai/tools/forge.py` run from the staged new bundle (`python .ai-next/tools/forge.py migrate`): read-only preview emitting a complete change set plus a `preview_token`, and `--apply TOKEN` guarded by a single `Transaction` with journal, recheck, automatic rollback, and `--recover`.
- Apply scope covers bundle replacement of manifest-declared framework-owned paths, proven-obsolete deletions, the deterministic `version` bump in `.ai/project.yaml`, explicit `--set key=value` configuration decisions, rendered root routers and adapters, and `.ai/framework.lock` — as one atomic logical operation followed by `validate` and protected-path re-hashing.
- Add a structured migration contract `.ai/framework/migrations.yaml` declaring per-version config decisions, breaking changes, and optional backfill commands; `migrate` computes findings mechanically for the actual old→new version range instead of relying on the agent reading prose.
- Extend `.ai/framework.lock` with `bundle_state` (framework-owned file hashes) so obsolete-file deletion is provenance-proven; unknown files inside framework-owned paths are preserved with an advisory finding, never deleted by inference. First migration without `bundle_state` conservatively preserves unknown files.
- Block migration with a named `router_extraction_required` finding when neither `.ai/custom/router-shared.md` nor an explicit `--router-shared <path>` input exists; legacy platform-specific overlays remain a separate blocking reconciliation. The skill or user performs the one-time judgment extraction, the command consumes the result.
- Parameterize `forge_adapters.render(bundle_root, root)` so the full post-migration state is computable as a pure function before any write; existing `adapters` command behavior is unchanged.
- Rewrite the `forge-migrate-framework` skill as a thin wrapper: stage the bundle (shell one-liner, no network in Python tools), run `migrate --diff`, relay findings, collect `--set`/`--router-shared`/collision decisions, apply, report.
- Replace the long migration prompt in `MIGRATION.md` with the staging one-liner chained to `migrate` (plus skill invocation guidance); shrink `.ai/MIGRATE.md` to a command-driven agent router that keeps the manual no-Python path documented as the fallback.
- Offline integration classification by `schema_version` against the staged contracts is preserved byte-for-byte and blocks only consumers, never the framework transaction.

## Capabilities

### New Capabilities

- `framework-migration`: deterministic one-command upgrade of a consumer repository from an active `.ai/` bundle to a staged `.ai-next/` bundle — preview/apply semantics, transactional replacement scope, version contract, router overlay handling, provenance rules, lock schema, and the skill/documentation surface.

### Modified Capabilities

(none — `python-automation` requirements already cover the general deterministic-tooling obligations that `migrate` inherits; the `render` parameterization is an implementation detail with unchanged externally observable adapter behavior)

## Impact

- **Code**: `.ai/tools/forge.py` (new subcommand), new `.ai/tools/forge_migration.py` module, `forge_adapters.py` (parameterized render), `forge_core.py` untouched except shared helpers if needed.
- **Framework bundle**: new `.ai/framework/migrations.yaml`; rewritten `.ai/framework/skills/forge-migrate-framework/SKILL.md`; rewritten `.ai/MIGRATE.md`; `manifest.yaml` framework-owned paths and skills list unchanged in membership.
- **Docs**: `MIGRATION.md` (runner instructions), `README.md` (migration section), `.ai/tools/USAGE.md` (new command).
- **Lock**: `.ai/framework.lock` gains `bundle_state`; unknown existing fields remain preserved.
- **Compatibility**: no removal of the manual migration path; projects without Python keep the documented fallback; consumer projects on versions without `migrate` in their old bundle are unaffected because the command runs from the staged new bundle.
- **Tests**: new `tests/test_forge_migrate.py`; updates to `tests/test_python_tools.py` for the parameterized render.
