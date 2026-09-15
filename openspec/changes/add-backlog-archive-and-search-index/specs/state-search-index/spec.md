## Purpose

Ranked retrieval over the growing durable-record corpora (decisions, intents, investigations, execution history, Backlog rows) without loading record bodies into context, via a derived project-local index that holds no authority: canonical files remain the only evidence and the index is always rebuildable from them.

## ADDED Requirements

### Requirement: One derived index covers all durable record kinds

The search helper SHALL maintain a single project-local derived index under `.ai/local/` built exclusively from canonical files: ADR, INT, INV, TASK, and Epic plan records, plus Epic and Bug rows from the live `BACKLOG.md` and `BACKLOG-ARCHIVE.md`, including `execution/completed/` content. Each indexed record SHALL carry its identifier, kind, canonical path, subject, area, status or outcome, dates, references, and full text. The index SHALL NOT be a source of truth: it contains nothing that cannot be rebuilt from the canonical files.

#### Scenario: Cross-corpus question answered in one query
- **WHEN** the orchestrator searches for a topic that appears in an ADR, a completed TASK, and an archived Bug row
- **THEN** one query returns candidates from all three kinds ranked against each other

#### Scenario: Index loss is harmless
- **WHEN** the index file is deleted or corrupted
- **THEN** the next query rebuilds it deterministically from canonical files and answers normally

### Requirement: Queries return ranked pointers, never bodies

A query SHALL accept a free-text match plus optional mechanical filters (record kind, area, date floor) and return a ranked list of identifiers, kinds, canonical paths, scores, and short text snippets. It SHALL NOT return full record bodies. Ranking SHALL be deterministic for a fixed index state, with a stable tie-break by identifier, and the output SHALL report index freshness (last reconciled state).

#### Scenario: Candidate discovery without body loading
- **WHEN** intake asks whether a similar request exists
- **THEN** the query returns matching INT identifiers with paths and snippets, and the orchestrator reads only the relevant full records

#### Scenario: Scoped search
- **WHEN** a query filters to kinds `ADR,INV` and area `auth`
- **THEN** results include only ADR and INV records whose recorded area matches

### Requirement: Freshness is reconciled mechanically before answering

Before answering, the helper SHALL reconcile the index against the current canonical files using recorded file modification and content-hash signals, applying incremental updates, and falling back to a full deterministic rebuild when the index is missing, stale beyond incremental repair, or structurally invalid. Reconciliation and rebuild SHALL require no model call and no network access. A query SHALL NOT answer from content known to be stale.

#### Scenario: Edited record picked up before answering
- **WHEN** an ADR file changed since the last reconciliation and a query matches its new text
- **THEN** the answer reflects the updated content and the reported freshness matches the current files

#### Scenario: Deterministic full rebuild
- **WHEN** the index is absent and a query runs
- **THEN** the index is rebuilt from scratch with identical content on every repetition

### Requirement: The index participates in no gates or lifecycle decisions

Search results SHALL be candidates for the orchestrator to read, never evidence. Lifecycle gates, transitions, acceptance, and priority decisions SHALL NOT read the index. Workflows that consult search SHALL still honor explicit references first (research refs, linked records) and treat mechanical matches as suggestions to verify in the canonical files. Where Python is absent, workflows SHALL proceed unchanged using explicit references and directory listing without implying any search coverage.

#### Scenario: Match is a pointer, not evidence
- **WHEN** a query surfaces a prior investigation similar to a new bug
- **THEN** the orchestrator opens the canonical INV file before relying on any of its conclusions

#### Scenario: Native workflow unaffected by index absence
- **WHEN** a project runs without the Python helpers
- **THEN** intake, planning, and investigation workflows complete using explicit references, with no search step reported as missing coverage

### Requirement: Search uses only local deterministic mechanisms

The search helper SHALL run fully offline using standard-library local storage and ranking (SQLite FTS or equivalent), with no embedding model, no external ranking service, and no nondeterministic model calls. Ranking inputs SHALL be limited to index statistics of the canonical corpus. Any future semantic ranking SHALL remain optional and sit behind the same query interface without changing these requirements.

#### Scenario: Offline query
- **WHEN** a query runs on a machine with no network access
- **THEN** the query reconciles, ranks, and answers entirely from local files
