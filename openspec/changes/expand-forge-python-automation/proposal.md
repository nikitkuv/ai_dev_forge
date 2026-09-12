## Why

Forge principles already push deterministic operations into local Python helpers, but a large share of mechanical work still runs through orchestrator tokens: lifecycle status edits in `BACKLOG.md`/TASK frontmatter, evidence-fingerprint comparisons, review-packet assembly, ID allocation, and the structural checklists of `forge-check-framework` and `forge-resume-development`. Each of these costs thousands of input/output tokens per session, is fully deterministic, and is error-prone when performed by a model editing Markdown tables by hand.

## What Changes

- Add read-only helpers: `next-id` (monotonic allocation for TASK/BUG/INV/EPIC/ADR/MUT identifiers) and `evidence-check` (recompute recorded fingerprints and report eligibility/freshness verdicts for Task acceptance, review freshness, and Epic gates).
- Extend `validate` with the mechanical portion of the `forge-check-framework` checklists: router/adapters shape (AGENTS.md line budget, `CLAUDE.md` import, UTF-8/BOM/frontmatter-at-byte-zero of generated agents), ADR index parity, plan-order vs TASK files, INV record structure, and mutation-registry structure.
- Add assembly helpers: `review-packet` (build the compact Review Packet JSON from a TASK's recorded paths, recomputed fingerprints, and scoped Git diffs) and `checks-new` (write an approved-checks packet from explicit argv/inputs).
- Extend `role` with `--assignment-file`: the helper concatenates the neutral role contract itself, so the orchestrator no longer reads and echoes the contract for external routes.
- Add scaffolding helpers: `inv-create` (allocate `INV-NNNN`, instantiate the template, record baseline revision and dirty-tree disposition) and `backlog` row operations (`add-bug`, `update-row`) as exact row edits.
- Add lifecycle mutations under a preview/apply pattern (like `adapters --apply TOKEN`): `transition task|epic`, `epic-start`, `epic-complete`, `accept-record`, and `commit-scoped`. The scripts execute only explicitly approved transitions; authorization stays with the user and the orchestrator.
- Update the framework skills (`forge-run-task`, `forge-complete-task`, `forge-complete-epic`, `forge-prepare-epic`, `forge-intake-bug`, `forge-investigate`, `forge-reprioritize-backlog`, `forge-check-framework`, `forge-resume-development`), `.ai/tools/USAGE.md`, README, and RUNBOOK to route these operations through the helpers. **BREAKING** for the documented helper contract: helpers stop being purely read-only; the "never change Task/Epic status" guarantee is refined to "never decide or infer transitions, only execute explicitly requested ones".

## Capabilities

### New Capabilities
- `lifecycle-scripting`: deterministic execution of already-approved lifecycle mutations (status transitions, workspace moves, acceptance recording, scoped commits) through preview/apply with journals and rollback; scripts never authorize, infer, or decide transitions.

### Modified Capabilities
- `python-automation`: new read-only commands (`next-id`, `evidence-check`, extended `validate` coverage), packet assembly (`review-packet`, `checks-new`), external role prompt assembly without contract echo (`role --assignment-file`), and record scaffolding (`inv-create`, `backlog` row operations).

## Impact

- `.ai/tools/forge.py`, `forge_core.py`, `forge_runtime.py`, possibly a new `forge_lifecycle.py` module and `.ai/tools/USAGE.md`.
- Framework skills listed above change their mechanical steps to invoke helpers; semantic gates (review protocol, test integrity, acceptance, authorization) remain with the orchestrator and user.
- `tests/test_python_tools.py` extended for every new command; existing Python tests must keep passing.
- README.md (automation section), RUNBOOK.md operational scenarios, FRAMEWORK.md helper-contract wording.
- No changes to agent contracts, adapter rendering inputs, delivery-track semantics, or evidence rules; fingerprints and evidence formats stay compatible.
