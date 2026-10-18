# Tasks: Add Backlog archive and search index

## 1. Archive foundations in `forge_core.py`

- [x] 1.1 Add `BACKLOG-ARCHIVE.md` parsing and writing to `forge_core.py`: parse year sections and Roadmap/Defect tables, append a row verbatim under the current year, create the file with the canonical header on demand. Verify with new cases in `tests/test_python_tools.py` (round-trip row move on an isolated consumer project).
- [x] 1.2 Extend identifier allocation so row-declared kinds (`BUG`, `EPIC`) scan the live `BACKLOG.md` and `BACKLOG-ARCHIVE.md`, with both listed in the auditable scanned-sources output. Verify with a test where the archive maximum (`BUG-0010`) exceeds the live maximum and `BUG-0011` is returned.
- [x] 1.3 Extend `validate --project`: report terminal rows in the live Backlog naming the backfill mutation as remediation, and check `BACKLOG-ARCHIVE.md` structure (terminal-only rows, well-formed year sections) when present. Verify with conformance tests for both violations.

## 2. Lifecycle mutations in `forge_lifecycle.py`

- [x] 2.1 Add the `backlog archive-row` preview/apply mutation: exact live+archive edits in the preview, token bound to both files, journal and rollback, refusal of non-terminal rows. Verify with mutation tests including stale-preview rejection and rollback on caught failure.
- [x] 2.2 Extend terminal Epic transitions (`epic-complete`, Epic `CANCELLED`) to move the row to the archive inside the same journal transaction, creating the archive file if absent; apply token binds workspace, live row, and archive; rollback restores all three. Verify with tests for the happy path, validation-failure rollback, and no terminal Epic row remaining in the live Backlog.
- [x] 2.3 Route Bug `RESOLVED` through the same atomic archival: the reviewed row edit that sets the terminal status also archives the row; an archive change between preview and apply invalidates the token. Verify with tests for atomic resolution and the stale-archive preview rejection.

## 3. Search index in a new `forge_index.py`

- [x] 3.1 Implement the schema and deterministic full rebuild: single `records` table plus one FTS5 table built from the `inventory(include_completed=True)` corpus plus live and archive Backlog rows; identical bytes for repeated rebuilds of the same tree. Verify with a determinism test on a fixture project.
- [x] 3.2 Implement reconcile-at-query-time: per-file mtime/content-hash incremental upserts and deletions; missing or structurally invalid `.ai/local/index.db` triggers full rebuild. Verify with tests for edited-record pickup, deleted-record removal, and deleted-database recovery.
- [x] 3.3 Implement `query`: free text plus `--kind`/`--area`/`--since` filters mapped to SQL, BM25 ranking with a stable identifier tie-break, bounded snippets, reported freshness, pointers only (no bodies). Verify with cross-corpus ranking, scoped-filter, and offline determinism tests.
- [x] 3.4 Detect FTS5 unavailability at first use and report search as unavailable with the reason, without touching any other workflow. Verify with a test that simulates an FTS5-less build.
- [x] 3.5 Wire the CLI in `forge.py` (`query`, `index rebuild|status`) and document both in `.ai/tools/USAGE.md`. Verify with subprocess smoke tests of each command against a fixture project.

## 4. Skills, contracts, and documentation

- [x] 4.1 Update skills: `forge-complete-epic` and `forge-intake-bug` route terminal transitions through the archiving mutations; `forge-reprioritize-backlog` surfaces stale `OPEN`/`PAUSED` rows as suggestion-only candidates and performs no compaction step; `forge-intake-feature`, `forge-intake-external-work`, `forge-prepare-epic`, `forge-investigate`, and `forge-resume-development` may call `query` for the obvious-matches step with explicit references still first. Verify that affected `tests/*.test.mjs` contract suites are updated and pass.
- [x] 4.2 Update `FRAMEWORK.md` (consumer structure with `BACKLOG-ARCHIVE.md`, sources-of-truth table, identifier scan scope, automation section with `query`/`index`), `RUNBOOK.md` (archive flows and a search-driven resume/intake scenario), and `MIGRATION.md` (one-time legacy backfill note). Verify by reading the three docs against the shipped behavior with no stale claims left.
- [x] 4.3 Run the full verification pass: `python tests/test_python_tools.py` and every touched `tests/*.test.mjs`, all green, and `openspec validate add-backlog-archive-and-search-index --strict` passes.

## 5. Deterministic backfill sweep and staleness report

- [x] 5.1 Implement `backlog archive-all` in `forge_lifecycle.py`: discover every terminal live row with the same classification `validate` uses, compose the single-row moves into one preview/apply transaction over both files, report without a mutation when nothing qualifies. Verify with tests for the batch move, the no-op report, and stale-preview rejection.
- [x] 5.2 Implement `backlog stale-rows --older-than <days>`: read-only report keyed by exact row identity (`git log -S "| <ID> |" --format=%cI -- BACKLOG.md`), with an explicit `unknown` bucket for rows without history and no writes. Verify with tests using fixed commit dates (old row reported, fresh row not) and a no-Git fixture (unknown, never guessed).
- [x] 5.3 Wire both commands in `forge.py`, document them in `.ai/tools/USAGE.md` and `RUNBOOK.md` (backfill sweep + mechanical stale report in the reprioritization flow), and rerun the full verification pass (`tests/test_python_tools.py`, touched `tests/*.test.mjs`, `openspec validate --strict`).
