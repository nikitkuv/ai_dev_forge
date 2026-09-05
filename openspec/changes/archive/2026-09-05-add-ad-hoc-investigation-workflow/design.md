## Context

Forge currently couples root-cause work to intake or TASK execution. Standalone diagnostics are read-only, while code changes normally require the full Epic/TASK route and generated roles. The requested workflow is intentionally simpler: the main agent investigates freely, stores the result, and either stops, promotes it, or fixes it directly. See `proposal.md` and `specs/ad-hoc-investigations/spec.md`.

## Goals / Non-Goals

**Goals:**

- Preserve useful investigations without forcing the standard lifecycle.
- Keep the same main agent and context from diagnosis through an optional fix.
- Make the record understandable and reusable by later planning.
- Record direct fixes clearly without copying the entire Git diff into Markdown.

**Non-Goals:**

- Define a prescribed research methodology or mandatory sequence of experiments.
- Add investigation subagents, independent review stages, or a new TASK-like state machine.
- Make investigation conclusions override product or architecture decisions.
- Automatically create Backlog work or commit changes.

## Decisions

### Use one flat document per investigation

Store each investigation at `investigations/INV-NNNN-<short-name>.md`. The document uses a small frontmatter block for ID, subject, area, relevant paths, baseline revision, linked work, and one outcome:

- `no_action` — nothing was changed; the reason and optional future recommendation are recorded;
- `promoted` — the result was handed to a Bug, Epic, Replan, or TASK;
- `fixed_directly` — the main agent implemented and verified the correction;
- `unresolved` — research stopped without a supported conclusion.

No separate registry, per-finding identifiers, or investigation state machine is required. Later agents can enumerate the directory, and users can cite an INV directly. Outcome history is appended when the disposition changes.

Alternative considered: an index plus packet directories, evidence-level states, and finding IDs. Rejected because it adds a second project-management system and makes a lightweight investigation expensive to maintain.

### Let the main agent choose how to investigate

`forge-investigate` defines required boundaries and recorded outcomes, not research steps. The strong main agent may inspect code and history, search locally, add temporary instrumentation, run tests, benchmarks, profilers, or other relevant tools, and iterate with the user. Generated Forge subagents are not invoked.

Material expansion such as production access, destructive actions, external effects, or new product/architecture decisions still uses existing permission rules.

### Support three useful paths after research

After the cause is established, the agent presents a concise conclusion and the user can do nothing, promote the result through existing Bug/Epic/Replan rules, or authorize the main agent to fix it directly. If no cause is established, the INV stays `unresolved` with useful next experiments.

Promotion updates `outcome: promoted` and stores the canonical work IDs. Direct correction updates `outcome: fixed_directly` only after verification. Choosing not to act stores `outcome: no_action` and the rationale.

### Record direct fixes as a path-level change ledger

When the main agent fixes the issue, the INV gains a `Direct Fix` section with:

- added, modified, and removed paths;
- a short description of what and why for each path;
- externally relevant behavior, contract, data, configuration, dependency, and documentation effects;
- commands and results used for verification;
- remaining risks, incomplete work, and manual checks;
- base and final commit IDs, or a scoped diff fingerprint while uncommitted.

Git remains the source of the exact line diff. The INV explains intent and evidence rather than embedding a large patch.

### Reuse investigations through explicit references and simple relevance checks

Bug/Epic/TASK records may carry `research_refs: [INV-NNNN]`. During intake or planning, the agent first reads explicitly referenced investigations, then checks `investigations/` for obvious matches by subject, area, and relevant paths. It presents uncertain matches to the user instead of relying on scoring or an automatic semantic registry.

The planner checks the recorded baseline and relevant paths for material change. If still applicable, it reuses the cause, proposed solution, risks, and verification suggestions. If not, it rechecks only what became doubtful. The approved work cites the INV, and the INV records the promoted work ID.

### Keep lifecycle effects separate

An INV is canonical research history, not an Epic/TASK gate. Direct changes can make existing evidence stale, and the normal resume/validation logic reports that. Investigation completion never implies acceptance or commit authorization.

## Risks / Trade-offs

- A free-form investigation may vary in depth. → Require a small set of outcome fields and sufficient evidence for every claimed cause.
- Direct fixes lack independent agent review. → Make authorization explicit, require scope control and proportionate verification, and record limitations honestly.
- Relevant investigations may be missed without an index. → Keep searchable frontmatter fields and allow explicit `research_refs`; present obvious candidates during planning.
- Old research may be reused after code changes. → Record baseline revision and relevant paths, then perform a quick applicability check before reuse.
- The change ledger may drift from Git. → Bind it to a commit or scoped diff and validate listed paths against the actual change.

## Migration Plan

1. Add minimal investigation identities, outcomes, record fields, reuse, direct-fix evidence, and lifecycle separation to framework contracts.
2. Add the flat investigation template and `forge-investigate` skill.
3. Update intake, planning, resume, router, bootstrap, migration, validation, and adapter guidance.
4. Add documentation, one end-to-end performance investigation scenario, and focused contract tests.
5. Increment the framework version and synchronize adapters after tests pass.

Existing projects gain the template and directory convention but no synthetic records. Migration preserves an existing project-owned `investigations/` directory and reports incompatible collisions rather than overwriting them.
