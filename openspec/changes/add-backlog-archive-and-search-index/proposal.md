# Add Backlog archive and search index

## Why

Durable state grows monotonically by design: an Epic completion only edits its Backlog row to `COMPLETED` and the row stays forever, so every reprioritization and resume pays context for the entire project history. Append-only evidence corpora (`decisions/`, `intents/`, `investigations/`, `execution/completed/`) are correct to keep, but retrieval over them relies on directory listing and subject matching performed by the agent, which weakens as records accumulate. These are two distinct problems — context pollution and retrieval — and they need two distinct mechanisms, not a storage migration: files remain the single source of truth.

## What Changes

- Terminal Backlog rows (Epic `COMPLETED`/`CANCELLED`, Bug `RESOLVED`) move automatically to a new project-owned `BACKLOG-ARCHIVE.md` inside the same journal transaction that performs the terminal transition. The archive uses the same table format, is split into year sections, and is append-only; rows are moved, never rewritten or deleted.
- `next-id` allocates from live Backlog plus archive so identifiers stay monotonic and are never reused; this is load-bearing for `BUG-*` ids, whose only record is the Backlog row.
- A new conformance invariant: the live `BACKLOG.md` contains no terminal rows.
- A manual `backlog archive-row` preview/apply mutation for one-time legacy cleanup, plus `backlog archive-all` moving every legacy terminal row in one batch transaction — one reviewed preview instead of one per row.
- `backlog stale-rows --older-than <days>`: a read-only mechanical staleness report over live non-terminal rows, computed from each row's Git history in `BACKLOG.md` (exact-identity pickaxe); rows without history are reported unknown. `forge-reprioritize-backlog` presents such candidates — a suggestion only; priorities and closures remain explicit user decisions.
- A derived SQLite FTS5 search index at `.ai/local/index.db`: one `records` table plus one FTS table covering ADR/INT/INV/TASK/PLAN/EPIC/BUG records including `execution/completed/` and Backlog archive rows. `forge.py query` returns ranked id + path + score + snippet, never full bodies.
- Index freshness is checked mechanically at query time (mtime/content-hash incremental refresh, deterministic full rebuild as fallback). The index is a rebuildable cache: it never participates in gates, lifecycle transitions, or evidence, and losing it loses nothing.
- Intake, planning, investigation, and resume skills may call `query` for candidate discovery; results are pointers (explicit links first, mechanical matches second), and evidence is still read from the canonical files. No embeddings, no network, stdlib `sqlite3` only; native workflows without Python keep working unchanged.

## Capabilities

### New Capabilities
- `backlog-archive`: compaction of terminal Backlog rows into an append-only year-sectioned `BACKLOG-ARCHIVE.md`; archival is part of the terminal transition itself, not a separate ritual; identifier allocation spans live and archive; live Backlog carries no terminal rows; legacy backfill works one row at a time or as one batch mutation; stale-row surfacing is a mechanical suggestion-only report from Git row history.
- `state-search-index`: derived local SQLite FTS index and the `query` contract — corpus coverage, ranked snippet output, mechanical freshness with deterministic rebuild, and strict non-authority boundaries (search candidates only; files remain the evidence).

### Modified Capabilities
- `lifecycle-scripting`: terminal transitions (Epic completion/cancellation, Bug resolution) atomically move the row to the archive in the same reviewed journal transaction; `archive-row` becomes a preview/apply mutation.
- `python-automation`: identifier allocation must consider archive rows to preserve monotonicity; structural conformance gains the no-terminal-rows invariant.

## Impact

- `.ai/tools/forge.py` (CLI surface: `query`, `index` lifecycle, `backlog archive-row`), `forge_core.py` (Backlog/archive parsing, next-id scope, inventory), `forge_lifecycle.py` (terminal transitions + archive-row mutation), a new `forge_index.py` module, `.ai/tools/USAGE.md`.
- Skills: `forge-complete-epic`, `forge-intake-bug` (resolution path), `forge-reprioritize-backlog`, and optional `query` usage in `forge-intake-feature`, `forge-intake-external-work`, `forge-prepare-epic`, `forge-investigate`, `forge-resume-development`.
- Docs: `FRAMEWORK.md` (consumer structure, sources-of-truth table, identifier rules), `RUNBOOK.md`, `README.md` where the structure is described.
- No new external dependencies (stdlib `sqlite3`, FTS5); Python-optional workflows unchanged. Existing consumer projects adopt the archive lazily on their first terminal transition or explicit backfill; no data migration is required.
