## Context

See proposal.md for the seven review findings. Forge ships instructions and deterministic Python helpers as a copied bundle; consumer state is project-owned. Git commands run through git_capture. Existing tests provide isolated consumer and Git fixtures. The user requested implementing the reviewed fixes through OpenSpec, covering planning and implementation in this change.

## Goals / Non-Goals

**Goals:** Restore the specified workflow and helper behavior with regressions that reproduce the reported failures. Keep Git/index changes within the accepted scope and retain migration preview freshness.

**Non-Goals:** Redesign lifecycle authority, add model-driven tests, backfill consumer history, auto-archive the change, commit this repository, or relax migration version guards.

## Decisions

1. Ship 4.13.0 in the manifest and project template, retaining the existing 4.13 migration entry and documenting the interview and fixes there. Test the unmodified shipped target against a consumer fixed at 4.12.0. Synthetic newer-version fixtures remain useful for generic migration mechanics but cannot establish release installability.
2. For scoped commits, fail before git add when the index contains paths outside scope. Use NUL-delimited Git listings and disable rename folding so both endpoints are checked; pass literal pathspecs and inspect Git failures. Recognize deletions from the union of index and HEAD paths (HEAD can be absent only for an unborn repository). Recheck the staged path set after git add. Rejecting a dirty unrelated index is simpler and more transparent than temporary-index commits or automatically unstaging work. Directory scope, if supplied, includes its descendants; Git path names must be normalized relative to the root.
3. Keep the interview in forge-prepare-epic as the authoritative sequence. The numbered bootstrap workspace step explicitly routes through it and supplies the confirmed inputs before planner invocation. Both bootstrap skills and final plan checks state the route; do not duplicate four full stages across documents.
4. Match the normalized recorded User Validation result exactly to `changes requested`; the existing recorded-value helper filters placeholders. Preserve real rejection and legacy tests. Add a clean-acceptance test retaining the actual template row.
5. Remove the empty-declaration early return from router divergence checking. Continue treating missing AGENTS.md as unverifiable. Test the clear/delete/sync lifecycle, not only isolated string parsing.
6. Allow load_rules to receive the rendering contract while retaining the active contract default for ordinary rule checks. Adapter rendering loads that contract through bundle_source so it is part of render freshness. Test with an active contract missing the new enum, and prove changes in the staged contract change the render fingerprint.

## Risks / Trade-offs

- [Unrelated staged work now blocks automatic commit] → report exact paths, preserve the index, and document this intentional refusal.
- [Git path parsing varies by filename and platform] → use NUL-delimited output, literal pathspecs, and tests for spaces/non-ASCII names, renames, staged/unstaged deletions, and unborn HEAD.
- [Concurrent external index changes] → check immediately before mutation and again before commit; do not claim protection against arbitrary external Git writers between commands.
- [Instruction checks cannot prove model behavior] → check that all bootstrap entry points route through the same workflow and retain human confirmation; no live model calls in tests.

## Migration Plan

Consumers stage the 4.13.0 bundle and use the existing preview/apply migration. Project declarations and execution history are preserved. Existing rollback journals restore failed migrations. No lifecycle backfill is required; keep this change active after implementation until the user requests sync/archive.
