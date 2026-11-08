## 1. Release and migration

- [x] 1.1 Publish consistent 4.13.0 manifest/template metadata and complete migration notes; verify release metadata consistency and preview/apply from a fixed 4.12.0 consumer to the unchanged shipped target.
- [x] 1.2 Validate project rules using the rendering bundle's fingerprinted contract; verify old active contracts, preserved declarations, and stale render-input detection.

## 2. Scoped Git commits

- [x] 2.1 Refuse unrelated staged paths before writes, parse literal paths safely, and document the refusal; verify HEAD/index/worktree preservation for staged modifications and renames, plus normal scoped commits and Git read failures.
- [x] 2.2 Support scoped tracked deletions and reject unknown missing paths; verify staged/unstaged deletions, spaces/non-ASCII filenames, directory scope, and manual-policy behavior.

## 3. Workflow and conformance

- [x] 3.1 Route both bootstrap entry points and Step 05 through the planning interview before planner detail filling; verify routing/order and preserved Plan Approval/Epic Start/Task Start boundaries with focused contract tests.
- [x] 3.2 Ignore template choice rows when detecting rejected deliveries; verify clean template-based acceptance, real rejection alongside a placeholder, and existing legacy acceptance behavior.
- [x] 3.3 Detect stale router statements after clearing/removing the declaration; verify conformance reports the stale rule and adapter synchronization clears it without altering the custom overlay.

## 4. Integration verification

- [x] 4.1 Run all Python/Node tests, forge.py validate, strict OpenSpec validation, and final diff checks; record results and leave the implemented change available for explicit sync/archive.

## Verification results

- Environment: Windows, Python 3.13.15, Node 24.14.1.
- New Python regression suite: 15 tests passed. Bootstrap interview contract suite: 6 tests passed.
- Full Node suite: 104 tests passed. Historical feature tests now validate version syntax; the new release test checks manifest/template equality, migration-note coverage, and upgrade from 4.12.0.
- Full Python discovery: 162 tests executed; 160 passed, one symlink test skipped because Windows did not permit creating symlinks, and the old additive-rule-template fixture failed because it advanced from the current release instead of 4.12.0. Corrected that fixture to use the fixed historical source and unmodified shipped target; its targeted rerun passed. All 161 executable tests have passing evidence on the final implementation; the complete discovery command was not repeated after this test-only fixture correction.
- `python .ai/tools/forge.py validate`: passed; `openspec validate fix-forge-review-regressions --strict`: passed; `git diff --check`: passed.
- At implementation handoff, no live model calls, consumer-history backfill, repository commit, spec sync, or archive had been performed.

## Archive

- Archived on 2026-11-08 at the user's request after completing all eight tasks.
- Synced all seven added requirements into the five corresponding main specs and verified their content against every delta.
- Strict main-spec validation: 20 passed, 0 failed. No active changes remain after archival.
