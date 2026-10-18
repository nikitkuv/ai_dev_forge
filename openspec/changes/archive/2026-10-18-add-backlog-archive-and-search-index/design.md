# Design: Backlog archive and search index

## Context

See `proposal.md` — Why. The constraints that shape this design: files stay the single source of truth ("execution state is recovered from files, not chat history"); Git owns file history; Python helpers are optional and mechanical; every mutation goes through preview/apply with journals; records are never deleted. Existing machinery to build on: `forge_core.py` already parses Backlog tables and record frontmatter and walks record corpora (`inventory`, with `execution/completed/` opt-in), `forge_lifecycle.py` already runs terminal Epic transitions as atomic logical operations (directory move + row edit in one journal transaction), and `forge.py backlog` already performs exact-row edits through preview/apply.

## Goals / Non-Goals

**Goals:**
- Live `BACKLOG.md` sized to the active horizon, without a compaction ritual anyone must remember.
- Ranked, offline, deterministic retrieval over all durable records with pointers instead of bodies.
- Zero new runtime dependencies; native (no-Python) workflows unchanged.

**Non-Goals:**
- No storage migration: nothing moves into a database of record; SQLite is a cache only.
- No semantic/embedding search; the query interface is the seam where it could later sit, nothing more.
- No generated per-folder `INDEX.md` navigation files (e.g. an intents index mirroring `DECISIONS.md`); with `query` available they are redundant, and the no-Python path already has directory listing plus `DECISIONS.md`.
- No changes to gates, acceptance, priorities, or any semantic authority.

## Decisions

### D1: Archive is one sibling root file with year sections

`BACKLOG-ARCHIVE.md` sits next to `BACKLOG.md`, uses the same table columns as the section the row came from, and is split into `## <year>` sections. Rows move verbatim; the file only ever appends.

Alternatives: per-year files (more file juggling, one more naming scheme to lock, no benefit at this scale); a "Closed" section inside `BACKLOG.md` (the live file keeps growing — the problem itself); trusting Git history alone (bug rows have no other record on disk, and `next-id` would need slow `git log -S` archaeology to stay monotonic).

### D2: Archival happens inside the terminal transition, automatically

The journal transaction that performs Epic Acceptance/`epic-complete` (already moving the workspace and editing the row) and every reviewed mutation setting a terminal status (Bug `RESOLVED`, Epic `CANCELLED`) also performs the row move and, if needed, creates the archive file. The preview shows both edits; the apply token binds both files; rollback restores both. A dedicated `backlog archive-row` preview/apply mutation exists only for backfilling legacy terminal rows and refuses non-terminal rows.

Alternative rejected: grace window / periodic compaction during `forge-reprioritize-backlog` — keeps recent completions visible in the live file but reintroduces a ritual; hygiene that depends on remembering eventually stops. "What did we ship this year" is served by the archive's current-year section.

### D3: One SQLite database, one records table, one FTS table

`.ai/local/index.db` holds a single `records` table (id, kind, path, subject, area, status, outcome, created_at, updated_at, epic_id, refs, mtime, content_hash) discriminated by a `kind` column, plus a single FTS5 virtual table over subject and body. The "folder" a record came from is the `path`/`kind` columns — a WHERE clause, not a schema.

Alternatives rejected: one DB per folder (BM25 scores from separate FTS corpora are not comparable, so cross-corpus ranking degenerates into merging incomparable lists; plus N files to manage and no SQL joins); one table per folder (identical schema everywhere means `UNION ALL` anyway — same data, more SQL, zero benefit).

### D4: Reconcile-at-query-time, self-healing, no index command ritual

`forge.py query` reconciles the index before answering: walk canonical locations, compare recorded mtime/content-hash per file, apply incremental upserts/deletions, and fall back to a deterministic full rebuild when the DB is missing or structurally invalid. On this corpus (hundreds of small files) the walk is milliseconds. The same walker feeds a `forge.py index rebuild|status` subcommand for explicit maintenance, but correctness never depends on anyone running it.

### D5: FTS5 BM25, no embeddings

Ranking uses SQLite FTS5 BM25 over one corpus, giving comparable scores across ADR/INT/INV/TASK/PLAN and Backlog rows. Standard-library only, fully offline, deterministic for a fixed index state (stable tie-break by identifier). Tokenization is `unicode61`, which handles the user-language (e.g. Russian) canonical documents; no stemming — acceptable for ID/term/subject lookups, partially mitigated by structured filters (`--kind`, `--area`, `--since`) over rich frontmatter. The known weakness is paraphrase recall; that is the documented trade-off, and the `query` interface (free text + filters → ranked pointers) is deliberately the seam where optional semantic ranking could be added later without touching callers.

### D6: Query output is pointers with bounded snippets

`query "<text>" [--kind ADR,INV] [--area auth] [--since YYYY-MM]` returns identifier, kind, path, score, and a short snippet per hit plus reported freshness — never full bodies. This preserves the framework's metadata-first pattern: search narrows candidates, the orchestrator reads the two or three canonical files that matter.

### D7: Corpus enumeration reuses the inventory walker

Indexing walks exactly what `inventory(include_completed=True)` already walks — frontmatter is mandatory in every template, so the structured columns come free — plus live and archive Backlog rows (Epic Roadmap and Defect Queue, both files). Skills change minimally: intake/prepare-epic/investigate/resume *may* call `query` for the "obvious matches" step that today is directory scanning; explicit references still come first, and results are candidates to verify in files. Where Python is absent, those skills run unchanged.

### D9: Batch backfill composes the single-row machinery

`backlog archive-all` discovers every terminal live row mechanically (the same classification `validate` uses), then composes the existing single-row move helper sequentially into one updates set — one preview, one token binding both files, one journal transaction, full rollback. With zero terminal rows it returns a report and performs no mutation, so a clean project can run it idly. Alternative rejected: N sequential `archive-row` calls (N previews, N transactions, N chances to stop halfway through a legacy cleanup).

### D10: Staleness from Git pickaxe, not new Backlog fields

Backlog rows carry no timestamps and adding them would change the row format every consumer edits by hand. The last change of a row is already deterministic in Git: `git log -S "| <ID> |" --format=%cI --max-count=1 -- BACKLOG.md`, with the padded cell as the pickaxe key so `EPIC-001` never matches `EPIC-0010` history. Rows without Git history land in an explicit `unknown` bucket — fail-visible, never guessed fresh or stale. The threshold is an explicit per-call argument; the report is read-only and changes no row.

### D8: Code placement

- `forge_core.py`: Backlog-archive table parsing and writing; archive-aware ID scan scope.
- `forge_lifecycle.py`: archive step inside terminal transitions; `backlog archive-row` and `backlog archive-all` mutations; `backlog stale-rows` report.
- New `forge_index.py`: schema, reconcile/rebuild, FTS querying, snippet extraction.
- `forge.py`: CLI wiring (`query`, `index`, `backlog archive-row|archive-all|stale-rows`).
- `.ai/tools/USAGE.md`, `FRAMEWORK.md`, `RUNBOOK.md`: contracts and flows.

## Risks / Trade-offs

- [BM25 misses paraphrases] → structured filters over rich frontmatter cover most intake/planning lookups; semantic ranking remains an optional future stage behind the same interface.
- [FTS5 unavailable in an exotic Python build] → detect at first use and report search as unavailable with the reason; no other workflow depends on the index.
- [Concurrent sessions racing on `index.db`] → reconcile is idempotent and cheap; worst case is a wasted rebuild. SQLite's own locking prevents corruption; a corrupt DB is rebuilt.
- [Archive merge conflicts across branches] → append-only same-format rows make conflicts textual, rare, and resolvable like any Backlog conflict today; no structured merge is attempted.
- [Legacy projects fail the new no-terminal-rows conformance check] → the violation names the backfill mutation as remediation; MIGRATION/RUNBOOK document a one-time backfill sweep.
- [Archive file grows forever] → it is never loaded into context as a whole; search covers it; year sections keep it browsable. Splitting into per-year files can be a purely mechanical later step if ever needed.

## Migration Plan

1. Framework bundle ships through the existing `forge-migrate-framework` update; generated adapters and neutral sources update as usual.
2. Consumer projects need no immediate action: the archive file is created by the first terminal transition (or explicit backfill). The new conformance check reports existing terminal rows with the backfill command as remediation; running one backfill sweep per legacy row clears it.
3. `.ai/local/index.db` needs no migration — it does not exist before this change and is disposable at any time.
4. Rollback: reverting the framework version restores prior behavior; `BACKLOG-ARCHIVE.md` is valid plain Markdown and can be merged back into `BACKLOG.md` by ordinary row edits if a project chooses to.

## Open Questions

- Exact snippet length and result-page size for `query` output — tunable during implementation without touching the specs.
