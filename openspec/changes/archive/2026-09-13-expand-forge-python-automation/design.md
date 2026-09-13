## Context

The helper bundle (`.ai/tools/forge.py` + `forge_core.py` + `forge_adapters.py` + `forge_runtime.py`, ~1000 lines) already implements read-only inventory/extraction/validation, adapter transactions, check execution, role transport, and metrics. Two existing mechanisms are reused heavily by this change:

- **Preview/apply transactions** (`forge_adapters.preview`/`apply`/`recover`): a token bound to input fingerprints + observed + candidate outputs, a guard directory `.ai/local/adapter-transaction/` with per-file backups and `journal.json`, atomic per-file `_replace`, full re-check before the first write, rollback on caught failure, recovery that refuses later user edits.
- **Structured evidence in TASK files**: the TASK template's `Workflow State` section holds a YAML block (`review_packet`, `review`, `testing`, `fast_assurance`, `current_gate`, `implementation_revision`) that is already machine-shaped; `forge_core.inventory`/`backlog_rows` already parse frontmatter and the Epic Roadmap table.

The framework docs (`USAGE.md`, skill contracts) currently state helpers never change Task/Epic status. This change refines that contract: helpers never *decide or infer* transitions, but execute explicitly requested ones transactionally. Authorization, semantic gates, and evidence judgment stay with the user and orchestrator.

## Goals / Non-Goals

**Goals:**
- One consistent transaction pattern for all mutating commands, provable by the same test strategy as adapters.
- Every new read-only command degrades explicitly (missing Python, missing evidence → clear error, manual workflow stays available).
- Keep `forge.py` a single CLI entry point; new logic in modules, not a monolith.
- Skills updated so the orchestrator calls helpers instead of performing mechanical edits/comparisons itself.

**Non-Goals:**
- No new external dependencies; standard library + existing pinned `pyyaml`/`jinja2` only.
- No semantic automation: review protocol, test integrity, track eligibility, authorization, acceptance decisions are never scripted.
- No changes to evidence formats, fingerprint algorithm, adapter rendering inputs, or contracts.yaml enums.
- No hooks/MCP/tool integrations; consumers without Python keep the manual workflows.

## Decisions

### D1: New module `forge_lifecycle.py`; shared transaction primitives move to `forge_core.py`

Mutating commands (transition, epic-start/complete, accept-record, backlog rows, inv-create, commit-scoped) get their own module. The reusable pieces of the adapters transaction — atomic `_replace`, guard-directory journal write/rollback/recover — are extracted into `forge_core` and re-imported by `forge_adapters` (behavior-identical, covered by existing tests). Each lifecycle command uses its own guard directory `.ai/local/lifecycle-transaction/` so an interrupted adapter sync and an interrupted transition cannot entangle each other.

*Alternative:* duplicate the transaction code per command — rejected: three copies of rollback logic is exactly the kind of drift the journal exists to prevent. *Alternative:* put mutations into `forge_adapters` — rejected: adapters render from templates; lifecycle edits target canonical files with different precondition logic.

### D2: Lifecycle preview tokens bind to target-file hashes, planned outputs, and precondition results

`transition`/`accept-record`/`backlog`/`epic-start`/`epic-complete` previews compute: current hashes of every file/directory they will touch, the planned post-edit byte content, mechanical precondition results (enum validity, source status, single-writer, Backlog consistency), and derive a token exactly like `preview()` does (digest of canonical state). Apply re-runs the preview, requires token equality, journals originals, writes atomically, re-validates structurally (`validate --project` equivalent) after the last write, and rolls back on any failure. Directory moves (epic-start/complete) journal the rename itself (move back on failure) plus the BACKLOG row backup.

*Alternative:* optimistic writes without tokens (edit-in-place like a normal CLI tool) — rejected: concurrent edits and stale decisions are the top failure mode the framework already guards against in adapters; consistency wins over a two-command saving.

### D3: Frontmatter and Workflow State edits are section-preserving re-serializations

TASK transitions rewrite only the YAML frontmatter block and, when the transition requires it, specific keys of the `Workflow State` YAML block (`current_gate`, `implementation_revision`, timestamps such as `started_at`). The Markdown body outside those two regions stays byte-identical; the preview diff shows unified diffs of exactly those regions. Precondition: the parsed frontmatter/Workflow State must exist and be valid YAML; a TASK whose Workflow State block is absent or unparsable fails the preview with the exact parse error (legacy TASKs get an explicit "record Workflow State first" instruction instead of silent body mutation).

*Alternative:* regex line-level field patching — rejected: fragile against key ordering/comments; re-serialization of the two machine-written YAML regions is deterministic and diffable. Body prose is never touched by scripts.

### D4: BACKLOG edits are single-row line replacements

`backlog_rows` parsing is extended to the Defect Queue table. Row insertion appends one rendered row after the last data row; row update re-renders exactly one row from its parsed cells (escaping `|`), leaving the header, separator, and all other rows byte-identical. The preview diff is the one-line change. Reordering rows (reprioritize) is a multi-row move expressed as an explicit row-order list; the preview shows before/after row order and the apply is transactional.

*Alternative:* full-table re-render from parsed data — rejected: it would normalize user column widths/whitespace across the whole table, violating "unrelated rows remain byte-identical".

### D5: `evidence-check` reads the Workflow State YAML block as its only input format

The command parses the TASK's `Workflow State` block, recomputes `snapshot()` fingerprints for `review_packet.changed_paths` (whole implementation) and `review_packet.production_review_paths` (production surface), and reports per-record comparisons: `review.production_fingerprint` vs current production set, `testing.implementation_fingerprint` vs current whole set, `fast_assurance.implementation_fingerprint` vs current whole set, plus Epic-level aggregation (all TASKs DONE, `Fuzzing impact`/smoke fields non-placeholder, aggregate fingerprint = union snapshot of all TASK surfaces). Empty/placeholder values (`<>`, `pending`, missing) are reported as "insufficient recorded evidence", never as pass. Output includes a `requires_judgment` block identical in spirit to `validate`'s.

*Alternative:* parse the human-oriented `Implementation Summary` bullet fields — rejected: two sources of truth; the Workflow State block is the machine contract the template already defines.

### D6: `review-packet` computes; the orchestrator records

`review-packet <task>` reads the recorded path classification and base revision from the Workflow State block, then outputs compact JSON: recomputed whole/production fingerprints, `git diff <base>..HEAD -- <paths>` for both surfaces (bounded, with `--no-color`, porcelain options pinned), packet field validation, and the canonical TASK/plan path list. It does not write into the TASK — recording the packet stays an orchestrator action because packet completeness is partly judgment (ambiguous-path rationales, review focus). This still removes the expensive part: hashing, diffing, and assembly.

*Alternative:* have the script write the Workflow State `review_packet` block itself — deferred (see Open Questions); recording keeps one writer for canonical evidence during this change.

### D7: `role --assignment-file` concatenates the contract inside the helper

`role` gains `--assignment-file <path>` as the alternative to `--prompt-file`. The helper reads `.ai/framework/agents/<role>.yaml` itself, extracts the contract body, concatenates contract + assignment into a `tempfile` under the project, invokes the external CLI, and removes the file in a `finally`. The orchestrator supplies only the assignment. `--prompt-file` remains for full manual prompts (backwards compatible). Skills for external routes switch to `--assignment-file`, deleting the "read the contract and include it exactly once" instruction — that instruction currently forces the contract through orchestrator context twice (read + echo).

### D8: `next-id` scans canonical declarations, not filenames only

Per kind: TASK ids from `inventory()` records plus plan files' task lists; BUG from the Backlog Defect Queue; INV from `investigations/`; EPIC from the Backlog Epic Roadmap; ADR from `decisions/` + `DECISIONS.md`; MUT from `quality/mutation-testing/registry.yaml` (`next_id` cross-checked against max retained id). Output: `{kind, next_id, current_max, scanned: [locations]}`. Gap-filling is forbidden by design (max+1).

### D9: `commit-scoped` stages explicit paths only and refuses ambiguity

Reads `git.policy` from `.ai/project.yaml`; takes the path list either from the TASK's recorded `review_packet.changed_paths` (+ canonical TASK/plan file edits) or an explicit `--paths` list (direct-fix INV); verifies with `git status --porcelain` that every modified tracked file is either in the staged set or explicitly reported as excluded-unrelated; commits with `git add <paths> && git commit -m <message>` (message from `--message` or template `TASK-NNN: <goal>`); never uses `git add -A`/`.`. Under `manual` policy or missing authorization flags it only prints the exact staged set and proposed message.

### D10: `validate` extensions stay behind existing flags

The new checks (router line budget, CLAUDE.md import, generated-agent BOM/frontmatter-at-byte-zero, ADR parity, plan order vs TASK files, INV structure, mutation registry structure) fold into `validate --project` / `--adapters` where their inputs already live, with each finding carrying the violated invariant string so skills can quote it. `forge-check-framework` and `forge-resume-development` are rewritten to consume `validate` output plus `evidence-check` and only perform the genuinely semantic residual checks.

## Risks / Trade-offs

- [Scripts gain write access to canonical files — the highest-value attack surface of the framework] → Every mutation is transactional with journal + rollback + recovery identical to adapters; previews show exact diffs; single guard directory prevents concurrent transactions; recovery never overwrites newer user edits. The authorization model is unchanged: no script decides anything.
- [Workflow State YAML parsing is the fragile core of `evidence-check`/`review-packet`] → The block is part of the TASK template and `validate --project` gains a structural check for its presence/shape (D10), so drift is caught mechanically before it reaches evidence commands. Placeholder values are treated as missing, never guessed.
- [Markdown table edits can corrupt user-formatted Backlogs] → D4 single-row replacement keeps unrelated bytes identical; previews make every edit reviewable; `validate --project` runs inside the transaction before commit of the logical transition.
- [Skill instructions get thinner — an agent without the updated skills may still hand-edit files] → Skills remain authoritative workflow descriptions; manual edits stay legal (they are today's workflow). `validate` detects resulting inconsistencies, and USAGE documents both paths.
- [Windows/POSIX path and encoding edge cases in new git/diff code] → Reuse `git_status`-style subprocess invocation (`safe.directory`, `-z`, explicit encodings); CI already runs both OS families for the Python tests.
- [Token-bound previews add ceremony to trivial edits (e.g. one status cell)] → The preview/apply pair is one extra command, and the alternative — silent corruption of a canonical table — costs more; `accept-record` and `transition` bundle several mechanical edits into one token so the ratio stays favorable.

## Migration Plan

1. Implement read-only commands first (`next-id`, `validate` extensions, `evidence-check`, `review-packet`, `checks-new`, `role --assignment-file`) — zero risk to existing behavior; skills can adopt them immediately.
2. Implement scaffolding (`inv-create`, `backlog` row ops) behind D2 transactions.
3. Implement lifecycle mutations (`transition`, `epic-start`, `epic-complete`, `accept-record`, `commit-scoped`) and update the corresponding skills in the same change so no skill instructs hand-edits for operations that now have a helper.
4. Update `USAGE.md`, README, RUNBOOK, FRAMEWORK wording ("helpers never change status" → "helpers execute only explicitly requested transitions transactionally; they never decide or infer").
5. Rollback strategy: the new commands are additive; reverting the bundle revert is enough because no persisted format changes. Existing projects' evidence and lock files remain valid.

## Open Questions

- Whether `review-packet` should later write the `Workflow State.review_packet` block itself (auto-recording). Deferred: does not change the command surface or specs; recording stays manual until field experience shows the orchestrator step is pure ceremony.
- Exact guard-directory layout for directory-move transactions (rename journal representation) is an implementation detail settled during coding; the recovery contract is fixed by the specs.
