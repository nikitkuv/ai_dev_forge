## 1. Renderer parameterization

- [x] 1.1 Refactor `forge_adapters.render(root)` into `render(bundle_root, root)` reading framework sources (manifest, contracts, templates, neutral agents, skills, launcher templates) from `bundle_root` and project state from `root`; update the `adapters` preview/apply/recover call sites to pass the active `.ai` bundle root, and verify `python -m unittest tests.test_python_tools -v` passes unchanged plus `.forge-venv/Scripts/python .ai/tools/forge.py adapters` reports no drift
- [x] 1.2 Add a unit test rendering the same project state against two different bundle roots (one with a modified template) and verify the outputs differ exactly by the template change, proving the split is complete

## 2. Migration contract and lock schema

- [x] 2.1 Create `.ai/framework/migrations.yaml` with `schema_version: 1`, a `4.12` entry (config additions/decisions for this release, breaking changes, backfill commands), and best-effort historical entries for 4.3–4.11 derived from the current `MIGRATION.md` prose; verify `load_yaml` parses it with duplicate-key rejection and a unit test round-trips the structure
- [x] 2.2 Add contract loading and range filtering (`(old, new]`) to the migration module with a unit test covering inclusive upper bound, exclusive lower bound, and skipped older entries
- [x] 2.3 Extend the lock writer to record `bundle_state: {schema_version: 1, files: {path: sha256}}` for framework-owned files while preserving unknown fields from a prior lock; verify with a unit test that an old lock with extra fields keeps them byte-identical after an adapter apply

## 3. Migration preview

- [x] 3.1 Create `.ai/tools/forge_migration.py` with `preview_migrate(root, staged_root, router_shared=None, include_diff=False)` implementing layout gates (distinct resolved paths, valid staged manifest, every staged file under a declared framework-owned path, unexpected staged file refusal) and version gates (downgrade refusal, equal-version no-op finding); verify with unit tests over synthetic tmp bundles including the downgrade and stray-staged-file cases
- [x] 3.2 Implement router handling in preview: carry `.ai/custom/router-shared.md` byte-for-byte, emit blocking `router_extraction_required` when absent, validate the `--router-shared` input (within root, non-empty, no unresolved markers, router line budget), and block on legacy platform-specific overlays; verify each case with a unit test
- [x] 3.3 Implement configuration reconciliation in preview: deterministic `version` update, mechanical application of `config_additions` defaults, blocking `config_decisions` findings with suggestions, and refusal of `--set` keys outside the declared decision/allowlist set; verify with unit tests for the blocking-missing-key, `--set` accepted, `--set` unknown-key rejected, and approved-value-preserved cases
- [x] 3.4 Implement provenance rules in preview: deletions only for files whose hash matches the prior `bundle_state` record and that are absent from the staged bundle; unknown files under framework-owned paths preserved with advisory findings; `__pycache__` ignored; verify with unit tests for recorded-obsolete, hash-mismatch preserved, and no-lock conservative cases
- [x] 3.5 Implement offline integration classification against the staged integration contracts (`absent`/`current_supported`/`older_migratable`/`malformed`/`unsupported_future`/`custom_profile`/`ownership_collision`) with byte-for-byte preservation and consumer-scoped blocking only; verify with unit tests using fixture integration files per class
- [x] 3.6 Compose the full preview result (replacements, deletions, preserved unknown files, rendered routers/adapters via parameterized render, updated config, findings with backfill commands, protected-path snapshot, `preview_token` bound to all inputs and observed bytes) and verify with a unit test that mutating any input after preview changes the token and that no file is written

## 4. Migration apply and recovery

- [x] 4.1 Implement `apply_migrate(root, staged_root, token, sets, router_shared, approved_collisions)` under one `Transaction("migrate")`: claim guard, backup journal over the full update map, post-backup token recheck, atomic writes with lock last, then `validate` against the new bundle and protected-path re-hash; verify with a happy-path unit test asserting final state (bundle replaced, config version bumped, routers/adapters rendered, lock contains `bundle_state`, `.ai-next/` removed)
- [x] 4.2 Implement failure semantics: stale token rejection before the first write, unapproved collision refusal, validation-failure rollback restoring the exact pre-migration state with `.ai-next/` retained, and post-apply protected-path tamper detection triggering rollback; verify each with a unit test
- [x] 4.3 Implement `recover_migrate(root)` delegating to `Transaction.restore` with an allowlist of migration-managed paths, refusing subsequent user edits; verify with a unit test simulating an interrupted transaction and a conflicting later edit

## 5. CLI wiring

- [x] 5.1 Add the `migrate` subcommand to `forge.py` (bare preview, `--diff`, `--apply TOKEN`, `--set`, `--router-shared`, `--approve-collision`, `--recover`) with the existing exit-code and canonical-JSON conventions and a dirty-Git-tree warning in preview; verify via subprocess invocation in a unit test that exit codes are 0/1/2 as specified and output is compact JSON
- [x] 5.2 Document the command in `.ai/tools/USAGE.md` (preview/apply examples, finding glossary, recovery) and verify the documented examples run as written against a synthetic fixture in the test suite

## 6. Skill and documentation rewrite

- [x] 6.1 Rewrite `.ai/framework/skills/forge-migrate-framework/SKILL.md` as a thin wrapper (stage via shell one-liner when `.ai-next/` is absent, run `migrate --diff`, relay findings, collect `--set`/`--router-shared`/collision decisions, apply with the token, report) and verify it contains no step that re-implements a migration mechanical action
- [x] 6.2 Rewrite `MIGRATION.md`: replace the long kickoff prompt with the staging one-liner chained to `migrate` (GitHub sparse-clone && migrate; local copy + migrate) plus skill-invocation guidance, and keep per-version prose notes as human documentation; verify the shell blocks are syntactically valid PowerShell and POSIX sh
- [x] 6.3 Shrink `.ai/MIGRATE.md` to a command-driven agent router (verify layout, run the command, interpret named findings, one-time router extraction as the only judgment task) with the manual no-Python path explicitly preserved as fallback; verify it no longer instructs the agent to perform mechanical migration steps itself
- [x] 6.4 Update `README.md` migration references and the framework version to `4.12.0` in `.ai/framework/manifest.yaml` and `.ai/templates/project.yaml`; verify `validate --project --adapters` passes on this repository and rendered adapters show no drift

## 7. Integration verification

- [x] 7.1 Create `tests/test_forge_migrate.py` end-to-end scenario building a synthetic consumer (active 4.11-style bundle with lock, overlay, project config, canonical docs, integrations) and a synthetic 4.12 staged bundle, then verifying: preview completeness, apply success, byte-for-byte protected paths, rollback on induced validation failure, and recovery after simulated interruption; verify the full suite `python -m unittest discover -s tests -p "test_*.py" -v` and `node --test tests/*.test.mjs` pass
- [x] 7.2 Run the real migration of this repository's own `.ai/` against a staged copy as a smoke check in a disposable worktree (not in the source repository) and verify the resulting tree passes `validate --project --adapters` with no protected-path differences
