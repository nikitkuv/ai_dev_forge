## Context

See `proposal.md` for motivation and the two delta specs for required behavior. Forge is documentation-first and has no executable CLI: behavior is defined by neutral skills, generated platform adapters, project configuration, canonical Markdown, and validation scenarios. Existing conventions explicitly keep hooks and MCP configuration project-owned, while `BACKLOG.md` and execution files own lifecycle state.

The design therefore needs a provider- and domain-neutral way to make local capabilities discoverable without turning connector configuration into framework output. The work-source profile additionally needs durable external identity without allowing Kaiten—or any future board—to become a second Backlog. Framework upgrades must remain safe whether the project has no integrations, supported integrations, or project-defined types unknown to the framework core.

## Goals / Non-Goals

**Goals:**

- Provide one provider-neutral registry for work sources, knowledge sources, data sources, analysis services, and project-defined capabilities.
- Keep a clean Forge project with no integration directory as a first-class default configuration with no additional runtime or upgrade requirements.
- Make ticket selection, interpretation, split/merge decisions, and provenance inspectable and recoverable from repository state.
- Compose external intake with existing Forge skills and approval gates instead of creating a parallel lifecycle.
- Keep integration use read-only, least-privilege, and resistant to instructions embedded in ticket content.
- Preserve project-owned integration definitions, consumers, and state across framework upgrade, schema migration, and rollback.

**Non-Goals:**

- A generic plugin SDK, background worker, polling daemon, webhook receiver, or Forge-owned connector runtime.
- Built-in business semantics for every possible integration type; custom semantics remain in explicitly bound project-owned skills.
- Bidirectional synchronization, moving cards, posting comments, or reflecting Forge status into Kaiten.
- Automatically accepting external priorities, statuses, assignees, estimates, or labels as canonical Forge decisions.
- Persisting full ticket bodies or attachments when stable references, mapped fields, and content fingerprints are sufficient.

## Decisions

### 1. Store generic integration definitions under a project-owned `.ai/integrations/` namespace

Add `.ai/integrations/` to the manifest's project-owned paths. Each integration uses a small versioned YAML definition with a stable ID, capability profile and profile version, enablement, resource scope, operation allowlist, access/data policy, allowed consumers, and optional per-platform bindings. Credentials and raw MCP configuration are forbidden. Profile-specific blocks carry only the fields needed by that capability; `work_source` adds field mapping, candidate filters, and optional label hints.

The directory itself is optional. The project template documents the registry but bootstrap does not create the directory or an enabled example. A sanitized Kaiten example belongs in user documentation or test fixtures, not in generated project state. Absence is valid and causes every integration-aware workflow to short-circuit without preflight or connector discovery.

This is preferable to putting the full definition in `.ai/project.yaml`: integrations evolve independently, can contain provider-specific mappings, and should not make the core project configuration noisy. It is preferable to `.ai/custom/`, whose current purpose is router text overlay rather than structured runtime contracts.

### 2. Bind capability profiles and semantic operations to explicit consumers

A profile defines semantic operations independent of transport or provider. A framework or project-owned skill declares the profile and minimum operations it consumes; effective authority is the intersection of the consumer contract, integration allowlist, active-platform binding, resource scope, and current user authorization. Registration alone never makes an integration callable by arbitrary workflows.

For example, `work_source` exposes `list_candidates` and `get_item`, with optional `get_relationships` or `get_attachment_metadata`. A knowledge profile might expose `search` and `get_document`, while a project-defined analysis profile can be used only by its project-owned skill. Each active-platform binding identifies the already configured local connector and concrete operation names.

Codex and Claude bindings may differ. Adapter parity means both generated routers and the portable skill describe the same contract; it does not require a local MCP installation on both platforms. Static framework validation checks schema and ownership, while live connector availability is a runtime preflight.

This explicit binding is chosen over provider-specific logic in Forge because it avoids baking Kaiten or any future provider into the framework. It is chosen over free-form integration instructions because structured fields are testable and constrain tool authority. Unknown profiles are preserved but not invoked by the core unless an explicit project-owned consumer supplies their contract.

### 3. Implement external boards as one `work_source` consumer

The new neutral `forge-intake-external-work` skill is the framework consumer of `work_source`. It owns connector preflight, scoped retrieval, normalization, trust-boundary enforcement, repository/canonical investigation, decomposition, provenance checks, and presentation of an intake proposal. It does not duplicate canonical mutation rules:

- supported defects hand off to `forge-intake-bug`;
- product changes hand off to `forge-intake-feature`;
- changes to approved planned/active scope use Replan;
- Epic preparation and execution continue through their existing skills.

The root router selects the skill for requests to inspect, import, triage, or take work from a configured external work source. A request to “take the next ticket” authorizes retrieval and recommendation, but not silent canonical mutation or lifecycle start; the exact decomposition remains a reviewable gate because one card may imply several Epics or several cards may form one Epic. Non-work-source integrations do not enter this workflow or acquire ticket relationships.

### 4. Normalize records before reasoning about Forge scope

The skill converts provider output to a stable internal evidence shape: integration ID, external ID, title, description, source reference, retrieved/update markers, labels, relations, and optional attachment metadata. It then separates source facts, repository evidence, agent assumptions, and unresolved decisions.

Label mappings return affected-area and candidate-capability hints only. For the motivating project, `Расчет запасов -> reserves/`, `UI -> frontend/`, and `ИИ агент -> agent/` can be configured, while `RAG` and `Рекомендации по бурению` may point to candidate domains without claiming directories already exist.

This normalization layer is preferred to invoking feature/bug intake directly on raw MCP output because it enables consistent deduplication, prompt-injection handling, and provider-independent scenarios.

### 5. Persist bidirectional canonical references plus a compact provenance ledger

For integrations implementing `work_source`, use `.ai/integrations/work-items.yaml` as project-owned intake provenance. Its versioned entries key on `(integration_id, external_id)` and record source reference, latest reviewed version/fingerprint, disposition, canonical `EPIC-*`/`BUG-*` and—only after approved planning—`TASK-*` mappings, grouping relationships, and decision timestamp. Add a compact `Sources` field to Epic and Defect Queue rows in `BACKLOG.md`, and an `external_sources` field to TASK frontmatter. Epic plans summarize the source-to-TASK coverage matrix. These canonical-side references let an agent discover ticket relationships while reading normal lifecycle state; the ledger provides the reverse index and source snapshot metadata needed for deduplication and many-to-many traversal. Other capability profiles neither use this ledger nor need synthetic work-item identities.

The ledger and canonical-side references are written together only with an approved intake, Plan Approval, or Replan result. Proposal-only retrieval does not create a durable “imported” record. Rejected or deferred dispositions may be persisted only when the user explicitly approves that decision. Before applying a diff, the skill re-fetches versioned records and invalidates stale proposals. Resume, Epic planning, TASK execution, and Epic Validation read both directions and report uncovered sources or mismatches.

Compact source keys use provider-neutral references such as `kaiten-board:card-123`; provider details remain in the integration definition. The relationship layer is not a second lifecycle source: conflicts are resolved in favor of `SPEC.md`, `ARCHITECTURE.md`, `BACKLOG.md`, plans, and TASK files, with the reverse ledger repaired through an explicit reconciliation step.

### 6. Treat intake writes as one validated logical transition

The orchestrator stages the approved canonical diff and corresponding provenance update, validates unique Forge IDs, references, Backlog/execution invariants, source mappings, and unchanged unrelated state, then applies them as one logical transition. On failure it restores only the staged intake changes. This follows the existing atomic conventions used for planned workspace creation and Epic Start.

One-to-many and many-to-one mappings are represented in both the plan coverage matrix and reverse ledger; no source record may vanish merely because it is grouped. Task creation or Replan updates source references and reverse mappings in the same transition. A source update is a new intake/Replan candidate, never an automatic canonical edit.

### 7. Keep generic managed outputs independent from local definitions

Add the generic registry contract and work-source skill to the manifest and both adapter outputs, then update routers and documentation. Generated files contain only generic routing and profile contracts; they never embed project integration IDs, provider names, scopes, tool names, or credentials. Bootstrap creates no integration directory or enabled integration. Migration preserves an existing `.ai/integrations/` directory and does not synthesize bindings from MCP files.

Integration definitions and state are excluded from framework-lock hashing unless a future project-owned input actually participates in rendering a managed output; their changes are validated as project state rather than framework drift. Framework checks validate definitions, unique IDs, operation/consumer policy, absence of obvious secret fields, active-platform binding diagnostics, and profile-specific invariants such as work-item ledger identity and bidirectional references. Live connector calls remain opt-in diagnostics because clean, offline, and partially configured projects must still validate normally.

### 8. Separate framework upgrade from integration-schema migration

Framework upgrade stages framework-owned release files and generated adapters under the existing migration model while copying or referencing project-owned `.ai/integrations/` unchanged. Preflight builds a compatibility matrix for every definition and state file: absent, current-supported, older-migratable, unsupported-future, malformed, or colliding. Connector availability is not checked during this structural phase.

The framework upgrade may complete when integrations are absent, supported, unsupported-future, or malformed, provided there is no ownership/path collision and unrelated framework invariants pass. Unsupported or malformed entries are preserved byte-for-byte and disabled only for consumers that require them. This failure isolation prevents an optional local facility from making clean Forge lifecycle work unusable.

An older schema transformation is a separate project-owned migration gate. The orchestrator shows the exact diff, keeps a recoverable copy, stages and validates all related definitions/state/references, requests approval, and atomically applies only that set. A failure restores the prior integration state without rolling back a successfully installed compatible framework. Conversely, framework rollback does not delete project-owned integrations; it selects the latest mutually supported schema representation or reports an explicit compatibility blocker before relationship-dependent work.

This two-transaction design is chosen over rewriting integration files during framework replacement because ownership and rollback boundaries stay clear. It is chosen over refusing the whole upgrade on unknown profiles because project extensions must be forward-preserved even when the core cannot consume them.

## Risks / Trade-offs

- [A repository-controlled binding could try to broaden agent tool authority] → Require explicit read-only operation allowlists, active-platform resolution, source scope, and refusal of undeclared operations; treat integration files as project configuration that the user reviews.
- [Ticket text can contain prompt injection or secrets] → Delimit connector output as untrusted data, map only declared fields, never execute embedded instructions, and avoid persisting raw bodies in provenance.
- [External records change between proposal and approval] → Store version/fingerprint evidence and re-fetch before applying the canonical diff.
- [The provenance ledger can drift from Backlog, plan, or TASK references] → Validate both directions during resume/check and every relationship-changing gate, make canonical Forge lifecycle documents authoritative, and require explicit reconciliation rather than guessing.
- [Read-only intake cannot keep Kaiten status synchronized] → Document this as a deliberate first-version boundary; a future change can add separately authorized write-back semantics.
- [Different platforms may expose different MCP tool names or only one configured connector] → Support per-platform bindings and make runtime availability a local preflight rather than a framework installation requirement.
- [Large boards can exceed context or connector limits] → Require configured filters, honor pagination, report incomplete retrieval, and work from bounded candidate batches without claiming global completeness.
- [A future Forge release may not understand a project-defined or newer profile] → Preserve unknown content byte-for-byte, isolate only its consumers, and require an explicit compatible consumer/schema before invocation.
- [Automatic integration migration could damage project-owned state] → Separate it from framework upgrade, require preview and approval, stage atomically, retain a recoverable copy, and test rollback across relationship files.
- [Hashing frequently changing local state could create false framework drift] → Keep integration content outside managed-output lock inputs and report its schema/referential health through separate project validation.

## Migration Plan

1. Increment the framework release and add optional `.ai/integrations/` ownership/schema conventions, extensible capability profiles, explicit consumer contracts, the neutral work-source intake skill, manifest membership, and generic router routing.
2. Update bootstrap, migration, adapter sync, lock calculation, framework checks, final validation, templates, and docs so a project with no integrations follows the unchanged clean Forge path.
3. Add an offline upgrade compatibility scan and fixtures for absent, current-supported, older-migratable, malformed, unsupported-future, custom-profile, and path-collision cases; do not invoke connectors during framework update.
4. Upgrade framework-owned sources and adapters atomically while preserving `.ai/integrations/`, MCP configuration, custom consumers, canonical documents, and execution state unchanged.
5. When an older supported integration schema needs conversion, present and separately approve its staged diff, migrate definitions/provenance/canonical references atomically, and verify rollback from the saved pre-migration state.
6. Add runtime fixtures for valid/invalid Kaiten-like work sources, non-board profiles, platform-local availability, untrusted output, pagination, stale snapshots, deduplication, and split/merge mappings.
7. Roll back managed framework files independently; retain project-owned integrations and choose a mutually compatible schema representation before allowing affected consumers. Canonical work approved from external sources remains ordinary Forge work.
