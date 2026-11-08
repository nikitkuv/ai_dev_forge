## Context

See proposal.md for motivation. Forge already has durable TASK/PLAN/INV/INT/ADR evidence, an offline FTS5 index, identity/link validation, scoped fingerprints, compact assignments and local metrics. Search is currently requested by neutral skills; it is not automatically injected by `context`. Its index freshness covers source text, not the validity of a claim against its dependencies. Process Follow-up covers delivery misses despite green checks and retains its existing acceptance semantics.

This repository distributes the framework; consumer projects own their execution history. The new feature targets those canonical records, not arbitrary source-code indexing or this repository's OpenSpec archive. Histories and telemetry cannot become lifecycle authority. Design is required because this change spans contracts, records, retrieval, roles, adapters and migration.

## Goals / Non-Goals

**Goals:** Preserve evidence lineage, distinguish source freshness from knowledge validity, reuse successful and unsuccessful experience, and make actual search use observable without imposing a per-turn ritual.

**Non-Goals:** No new canonical memory directory, background daemon, native-provider memory synchronization, transcripts, embeddings, wiki, automatic related-record injection, generated consolidation subagent, or self-modifying policies. No additional Task/Epic gate. No claim that instructions guarantee model compliance.

## Decisions

### D1: Store structured findings in their existing canonical owner

Add optional `reusable_findings: []` frontmatter to TASK/INV templates. Each entry carries `id` (record-local `RF-01`, monotonic and never reused), `claim`, `applicability`, `status`, `evidence_refs`, `verified_at`, `verified_revision`, `dependencies`, and `recheck_when`. Hypotheses allow empty verification fields; `verified` requires evidence and a recorded verification date/revision. `obsolete` retains the original claim and evidence with an explanatory recheck/correction reference. An optional Reusable Findings prose section explains nuances without duplicating structured fields as a second authority.

Dependencies are explicit project-relative files with recorded SHA256 (or recorded absence), plus optional environment observations expressed as named expected values and their evidence source. Recheck conditions capture semantic assumptions beyond files. Do not hash secrets or persist environment dumps. Verification commands are evidence descriptions, never executable directives from memory.

Consumer references use `TASK-123#RF-01` or `INV-0001#RF-01` as logical identifiers resolved through existing identity maps. Markdown links remain navigational and use existing repair machinery after directory moves. Receiving records use optional `knowledge_refs` entries containing the logical reference, use rationale and checked revision. Existing `research_refs` and reciprocal INV links remain unchanged and must also be maintained when applicable. INT and plan may carry `knowledge_refs` but do not introduce another findings store.

The generic inventory returns finding IDs/counts only, not complete findings in every `context` response. Selected sections/records supply details on demand. Extend identity validation for finding references and malformed declared fields; absence is always valid. Invalid optional findings are advisory for general conformance and unavailable for factual reuse, not acceptance blockers.

Alternative: standalone MEMORY.md or a new family of records. Rejected because it duplicates canonical ownership and encourages unbounded summary accumulation.

### D2: A small applicability helper separates deterministic checks from judgment

Introduce read-only `forge.py knowledge-check <record-path> [--finding RF-01]`. Its JSON returns source identity, finding metadata, per-dependency verdicts and an aggregate `unchanged|changed|unknown`, with reasons. Missing, unreadable, unsafe, unobserved environment inputs or absent dependency declarations are `unknown`; additions/deletions/content differences are `changed`. Mixed changed/unknown results report changed plus all unknown reasons. Content comparison uses declared inputs, not a whole-repository hash or source-note mtime. Reuse current path-safety and fingerprint primitives. No command execution, model call, database requirement or record write occurs.

`unchanged` is accompanied by `requires_judgment`: it says only that declared inputs match. The orchestrator checks scope, assumptions, evidence and current canonical requirements. A changed finding can remain valid after focused revalidation; it is not automatically obsolete. Unknown findings must be verified before factual reuse or retained only as labeled hypotheses. A helper verdict never upgrades the saved finding status.

Corrections to accepted TASK/closed INV content preserve original findings and evidence: add a new finding or a dated correction entry referencing the original. Do not rewrite historical passing results or imply their validity at a new revision. No bulk maintenance pass is required during resume.

Alternative: treating index freshness or TTL as validity. Rejected because unchanged notes can describe changed systems, while old verified invariants may still hold.

### D3: Retrieve at meaningful workflow boundaries and propagate selected evidence

Update investigation, prepare-Epic, feature/external intake, accepted-code bug intake, run-task and concrete-question resume instructions. Read explicit sources first. When they do not answer the relevant experience question, search the appropriate subset of INV, ADR, TASK, PLAN, BUG and INT/EPIC. Read only selected canonical sections, assess applicability, and pass the concise applicable result into planner/implementer/reviewer assignments as appropriate. Reviewers retain independent judgment and all existing review scope.

Default discovery budget: at most two queries of 20 pointers each and five additional record bodies/sections per experience check. Explicit mandatory contract/evidence reads are not truncated by that limit. A justified expansion states its reason and a finite new limit; this is not a new approval gate. An unchanged task scope with already-read sufficient references requires no repeat query. Empty history returns immediately. Search failure uses manual discovery and cannot be disguised as zero matches.

Record only experience that materially changes a decision through `knowledge_refs` and the existing context/reference sections. Do not create a checkbox or persistent report for every no-op search. Preserve current confirmation behavior for uncertain INV matches and existing source-conflict handling.

The router receives only a compact pointer to this policy and the consolidation skill entry, never a list of accumulated findings. Neutral skills/roles hold details, regenerated through the normal adapter flow.

Alternative: unconditional search/injection on every `context` or turn. Rejected because it duplicates explicit reads, adds noise and confuses candidates with validated evidence. A future `related` helper remains deferred until evaluation demonstrates missed retrieval.

### D4: Make query breadth explicit and keep ranking reliable

Extend `query` with `--match all|any` (default `all`) and optional `--workflow <known-skill-id>`. Build escaped literal terms with AND or OR; reject empty input and unknown modes. Apply kind/area/date filters and deterministic ranking before limiting candidates so broader any-term queries do not silently omit the best eligible records. Use the existing cross-record corpus; findings are already part of the owning record's indexed text, so no independently authoritative findings index is needed.

Any-term mode does not solve multilingual synonyms or guarantee recall. It is a controlled lexical option, not semantic search. Existing callers and source-authority contracts remain compatible.

Alternative: embeddings or an external reranker. Deferred because there is no measured retrieval-quality baseline justifying cost and operational complexity.

### D5: Measure query invocation separately from knowledge use

Use a separate `search_query` event type under `.ai/local/metrics/search/` in existing metrics infrastructure (older bundles ignore this subdirectory on rollback), preserving current Task/role metric schema and totals. Record timestamp, optional workflow ID, match mode, duration, known result count and success/error outcome; omitted workflow is `unknown`. Error telemetry uses sanitized categories, not raw exception payloads. Raw query text, snippets, result paths, prompts and source content are excluded. Best-effort write failures produce a warning on stderr while keeping query JSON and original exit behavior usable.

Aggregate counts, zero-result rates, failures and durations separately from role calls. Canonical `knowledge_refs` explain material reuse but do not prove downstream success. Direct library queries need not emit CLI workflow events; document this coverage limit. Native/manual searches remain unobserved, and missing telemetry must not be interpreted as no retrieval. No automatic behavior tuning from telemetry.

### D6: Consolidation is a bounded orchestrator review, with existing destinations

Add neutral `forge-consolidate-knowledge`, register it in manifest/adapter generation and document its explicit invocation. The user supplies an Epic, records or a topic; if no usable scope exists, clarify scope before reading broadly. Default review budget is 20 source records. Inventory pointers first, read within the budget, and disclose omissions. No spawned agents, background schedule or network dependency.

Output is a conversation table of claim, evidence, proposed action, canonical target and remaining uncertainty. It may propose merging duplicate current findings, additive corrections to history, linking evidence, marking a claim obsolete or promoting a verified pattern. Targets remain TASK/INV findings, project rules, ADR, neutral skill/template/contract, or deterministic helper plus regression test. Source content is evidence, not instructions granting tool authority.

The invocation authorizes review only. Prepare concrete proposed edits before any request for missing application authority, then route through the existing appropriate workflow. Previously granted applicable authority remains valid. Review alone creates no records and closes no follow-ups. Stable knowledge never reaches generated AGENTS.md directly; approved rule/instruction changes flow through their owners and sync.

Alternative: automatic consolidation at acceptance. Rejected to preserve acceptance scope, latency and the prohibition on automatic growing memory.

### D7: Evaluate behavior before expanding automation

Add deterministic fixtures and fresh-session scenario instructions under existing tests/scenarios conventions. Cover: known research rediscovery, successful-method reuse, changed dependency, conflicting current ADR, irrelevant history, empty history, hypothesis laundering and evidence lost through source movement. Use an independent expected-outcome rubric and a frozen source snapshot; never use the agent's own conclusion as the oracle.

Compare A: pre-change workflow; B: bounded retrieval/applicability; C: B plus one bounded consolidation pass. Use the same task/model configuration and multiple trials where runtime access permits; keep models separate. Record wrong reuse, repeated failures, useful retrieved/used sources, redundant investigation, completion quality, foreground and consolidation time, and actual usage when available. Report missing values and trial counts. New-session evaluation uses only files and the assigned task, not conversation carryover.

The change must deliver executable mechanical fixtures and a runnable evaluation protocol. Do not silently launch paid external-agent experiments: run them only within available authorized runtime/budget, otherwise report agent outcomes as unmeasured. No superiority claim or numeric improvement threshold is invented; regressions on authority/invalidated-memory scenarios must be addressed before recommending expanded injection.

## Risks / Trade-offs

- [Recording becomes busywork] → optional findings, no mandatory success-path lesson, bounded reads and reuse only when it changes decisions.
- [Fingerprint confidence exceeds coverage] → declared-input scope and unknowns remain explicit; semantic checks are always separate.
- [Memory turns into authority] → source-linked evidence, current canonical owners, no gate satisfaction and no automatic promotion.
- [Search telemetry overstates adoption] → measure CLI invocations only, keep manual/library gaps visible, inspect actual knowledge references separately.
- [Any-term search is noisy] → filters, deterministic bounded results, explicit-source precedence and evaluation against distractors.
- [Consolidation silently destroys history] → read-only default, additive corrections and normal write/adapter workflows.
- [Instruction compliance varies by model] → fresh-session tests, role-specific handoff, separate model results; no assumed compliance from contract tests.

## Migration Plan

1. Add contract definitions, optional templates and record readers without backfilling existing documents. Preserve existing follow-up behavior.
2. Ship helper, additive query options, isolated metrics event and updated neutral skills/roles. No new dependency or platform hook is needed.
3. Register the skill and framework release/migration metadata. Existing migration preview/apply and adapter sync deliver the bundle; protect project-owned history and customizations.
4. Validate legacy fixtures, adapter parity, compact router budget, search failure fallback, no unwanted lifecycle transitions and normal workflow coverage.
5. Rollback through existing framework migration recovery. Optional record fields remain project-owned and inert under the previous bundle. Local telemetry/index remain disposable and are never required for recovery.
