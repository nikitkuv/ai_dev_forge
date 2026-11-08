## Why

Forge retains execution and research history, but future agents can miss relevant experience because retrieval is discretionary and planning searches primarily INV/ADR. Durable conclusions also need explicit evidence and applicability checks: an up-to-date SQLite index does not establish that an old conclusion still applies to current code.

## What Changes

- Add a bounded prior-experience check at investigation, Epic preparation, feature/external intake, Task execution and relevant resume points. Explicit references satisfy the check when sufficient; search covers missing context and includes completed TASK/PLAN and historical defects where relevant.
- Add optional evidence-backed reusable findings inside existing TASK/INV records, including successful approaches, limitations and hypotheses, without requiring a lesson after every task or creating another canonical memory store.
- Check dependencies of selected findings on reuse, distinguish mechanical freshness from semantic validity, and pass only applicable findings with provenance to the assigned agent.
- Extend existing SQLite search with an explicit any-term option while retaining the current all-term default and deterministic offline behavior.
- Record minimal local search telemetry and canonical references for actually reused experience, distinguishing search invocation from useful reuse.
- Add an explicitly invoked, bounded knowledge-consolidation skill that reviews selected history and proposes corrections or promotion into existing owned targets; it never automatically changes instructions or acceptance history.
- Add fresh-session evaluation scenarios comparing existing behavior with retrieval and consolidation, measuring quality as well as context and maintenance cost.
- Preserve legacy records, lifecycle gates, source authority and the compact router. Defer wikis, embeddings, automatic related-record injection and background agents.

## Capabilities

### New Capabilities

- `agent-knowledge-reuse`: Evidence-backed findings in TASK/INV, bounded retrieval and handoff, applicability checks, compatibility and fresh-session evaluation.
- `knowledge-consolidation`: Explicit, bounded cross-record review with source-backed proposals, existing ownership targets and no autonomous promotion.

### Modified Capabilities

- `state-search-index`: Explicit all/any-term matching and minimal non-authoritative query telemetry; canonical pointers, offline ranking and existing defaults remain intact.

## Impact

- Neutral skills and agent instructions, TASK/INV templates, framework contracts, conventions, manifest and additive migration declarations.
- `.ai/tools/forge_index.py`, CLI dispatch, bounded record readers and local metrics integration; existing SQLite FTS5 and Python standard-library mechanisms remain sufficient.
- Generated adapters through existing synchronization, without hand-editing generated outputs; documentation and regression/scenario coverage.
- Consumer projects continue without findings or SQLite FTS5. No external service, transcript ingestion, new lifecycle gate or automatic policy editing is introduced.

Research motivation: [Anthropic, The components of agent memory](https://www.anthropic.com/research/components-of-agent-memory). This change adapts selective recording, verification and bounded consolidation to Forge; improvement in Forge agent outcomes remains an evaluation question.
