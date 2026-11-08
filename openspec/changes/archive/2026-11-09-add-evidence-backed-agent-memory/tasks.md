## 1. Evidence and reference contracts

- [x] 1.1 Define optional finding and knowledge-reference contracts, status semantics, ownership, correction rules and non-gating legacy behavior in neutral contracts/conventions; verify agreement with agent-knowledge-reuse scenarios and unchanged Process Follow-up requirements.
- [x] 1.2 Add optional finding fields to TASK/INV and receiving knowledge references to TASK/INV/INT/plan templates; verify parsing examples for verified, hypothesis, obsolete and absent findings, with legacy fixture compatibility and no synthetic records.
- [x] 1.3 Extend bounded inventory and identity/reference inspection for logical record-local finding references; verify valid resolution across Epic moves, duplicate/missing finding IDs, malformed fields, advisory-only failure behavior and absence of full finding bodies in default context output.

## 2. Applicability checks

- [x] 2.1 Implement read-only `knowledge-check <record-path> [--finding RF-01]` using existing path/fingerprint primitives; verify unchanged files, changed content, additions/deletions, recorded absence, incomplete dependencies and mixed changed/unknown inputs against explicit expected JSON verdicts.
- [x] 2.2 Handle unreadable/unsafe inputs, unsupported or unobserved environment evidence and malformed findings conservatively; verify no command execution, writes, network or status promotion and explicit `requires_judgment` on unchanged inputs.
- [x] 2.3 Document and support dated additive corrections and stable source references within existing record writes; verify original accepted evidence survives a correction and no acceptance/test result is rewritten or implicitly renewed.

## 3. Retrieval and observability

- [x] 3.1 Extend `query` with backward-compatible `--match all|any` and literal term escaping; verify all-term compatibility, any-term recall, filters, empty/invalid input and operator-like text using representative cross-record fixtures.
- [x] 3.2 Ensure filtering and deterministic ordering occur before candidate limits; verify a corpus exceeding the old 500-candidate cap returns the highest-ranked eligible records, with stable ties and fresh pointers after edits/rebuilds.
- [x] 3.3 Add optional workflow labels and isolated best-effort CLI search events through local metrics; verify success, zero results, search errors and telemetry write failures preserve original JSON/exit outcomes and store no raw query/source/snippet/error content.
- [x] 3.4 Add separate search aggregates and document measurement coverage; verify counts/durations and unknown values without changing role/task totals or inferring useful reuse, success or ranking signals.

## 4. Agent workflow integration

- [x] 4.1 Update investigation, Epic preparation, feature/external intake and accepted-code bug intake with explicit-source-first bounded experience retrieval including relevant TASK/PLAN/BUG history; verify workflow examples find completed-task experience and skip redundant searches when links suffice.
- [x] 4.2 Update Task execution, concrete-question resume and planner/implementer/reviewer handoff instructions with applicability checks and provenance; verify hypotheses, obsolete findings, changed dependencies and current-source conflicts cannot become unsupported factual premises or assurance evidence.
- [x] 4.3 Add selective finding capture and receiving knowledge references within existing authorized records, preserving reciprocal INV links and Process Follow-up; verify successful discoveries can be retained while routine/no-op tasks require no lesson and incur no new gate.
- [x] 4.4 Wire a compact router policy pointer and document default discovery budgets and fallback; verify instruction/adapter contracts, existing router budget and Python/FTS5-unavailable scenarios without synthetic search coverage or required-contract truncation.

## 5. Bounded consolidation

- [x] 5.1 Create neutral `forge-consolidate-knowledge` for explicit scoped orchestrator review with a finite source budget; verify missing scope handling, budget exhaustion disclosure, no generated subagents and no background or automatic lifecycle actions.
- [x] 5.2 Define source-backed proposal output and routing to existing owned targets; verify duplicate hypotheses remain unverified, mechanical failures route to helper/test, historical corrections are additive, and review alone changes no instructions, records or follow-up disposition.
- [x] 5.3 Register the skill in manifest and adapter generation and add usage examples; verify Codex/Claude/OpenCode parity, preservation of unlisted project-owned entries and no direct edits to generated consumer adapters.

## 6. Evaluation and release integration

- [x] 6.1 Add deterministic fixtures and independent expected outcomes covering known research, successful strategy transfer, invalidated dependency, canonical conflict, distractors, empty history, repeated hypotheses and moved source records; verify fixtures exercise actual helper/search behavior rather than only instruction strings.
- [x] 6.2 Add a runnable fresh-session A/B/C evaluation protocol with frozen baseline, task/model settings, trial counts, source-use evidence and foreground/consolidation cost fields; verify its schema preserves unknown metrics and does not equate smaller context with better outcomes.
- [x] 6.3 Exercise the evaluation protocol using available authorized runtime/budget and record observed outcomes and omissions; verify each executed run starts without conversation carryover and unexecuted agent comparisons are explicitly marked unmeasured rather than passed.
- [x] 6.4 Update framework version/migration metadata and README, FRAMEWORK, RUNBOOK and tools usage; verify additive migration preview/apply and rollback fixtures preserve legacy canonical documents, project customizations and existing lifecycle behavior.
- [x] 6.5 Run affected Python and Node contract tests, adapter parity/budget checks and the repository's broader required checks for the final bundle; verify legacy query/metrics behavior, authority boundaries and `openspec validate add-evidence-backed-agent-memory --strict` before reporting implementation complete.

## Verification evidence

- Full Python discovery: 173 tests, OK, one OS symlink-permission skip.
- Final focused knowledge/search/adapter/evaluation suite: 14 tests, OK (includes three integration tests added after the full run).
- Node contract suite: 104 tests, all passed.
- Forge bundle validation and strict OpenSpec validation passed; router 9,225 bytes within the existing 9,500-byte budget.
- Eight mechanical evaluation scenarios passed; fresh-session A/B/C model outcomes and costs remain explicitly unmeasured.
- Search telemetry is isolated under `.ai/local/metrics/search/` for rollback compatibility. SQLite cache schema 2 rebuilds old caches and removes replaced FTS rows before updating.
