# Project-local integrations

AI Development Forge does not require local integrations. A clean project has no `.ai/integrations/`, performs no connector preflight, and uses the standard bootstrap, development, adapter-sync, validation, migration, and rollback paths.

An integration definition is project-owned. Forge never creates the connector, installs software, authenticates, stores credentials, or copies local bindings into generated adapters. Definitions follow `.ai/templates/integration.yaml`; the normative contract is `.ai/framework/integrations/contracts.yaml`.

Bindings may target `codex`, `claude`, or `opencode`. Adding OpenCode platform support does not synthesize a binding: a definition remains inert on OpenCode until the project supplies an explicit compatible local connector mapping.

## Capability and consumer model

An integration declares a provider-neutral profile, semantic operations, resource scope, access/data policy, allowed consumers, and platform-local bindings. A definition is inert until the orchestrator selects a compatible framework-owned or project-owned skill. Effective authority is the intersection of the integration allowlist, consumer contract, active-platform binding, scope, and current user authorization.

Built-in profile names include `work_source`, `knowledge_source`, `data_source`, and `analysis_service`. Only `work_source` currently has a bundled consumer: `forge-intake-external-work`. Custom profiles are preserved but require a project-owned consumer.

## Knowledge-source example

```yaml
schema_version: 1
id: geology-knowledge
profile: knowledge_source
profile_version: 1
enabled: true
access: read_only
consumers: [project-search-knowledge]
scope:
  resource: approved-geology-library
operations:
  - {semantic_name: search, access: read_only}
  - {semantic_name: get_document, access: read_only}
bindings:
  codex:
    connector: project-knowledge
    operations: {search: search_docs, get_document: read_doc}
  opencode:
    connector: project-knowledge
    operations: {search: search_docs, get_document: read_doc}
profile_config: {}
```

Forge core preserves this definition but does not invoke it because the consumer is project-owned. It creates no Epic/Task relationship.

## Project analysis-service example

```yaml
schema_version: 1
id: reserves-scenario-analysis
profile: reserves_analysis
profile_version: 1
enabled: true
access: read_only
consumers: [project-analyze-reserves]
scope:
  resource: approved-local-scenario-store
operations:
  - {semantic_name: analyze, access: read_only}
bindings:
  claude:
    connector: local-reserves-tools
    operations: {analyze: calculate_scenario}
profile_config:
  result_contract: reserves-scenario-v1
```

An unknown custom profile remains usable only through its project-owned consumer. Other Forge workflows continue even if that binding is unavailable.

## Kaiten work-source example

This sanitized example illustrates a project such as `oilgas_reserves_calculation`. Values are logical aliases, not credentials or guaranteed MCP tool names.

```yaml
schema_version: 1
id: kaiten-product-board
profile: work_source
profile_version: 1
enabled: true
access: read_only
consumers: [forge-intake-external-work]
scope:
  resource: product-space/reserves-board
operations:
  - {semantic_name: list_candidates, access: read_only}
  - {semantic_name: get_item, access: read_only}
  - {semantic_name: get_relationships, access: read_only}
bindings:
  codex:
    connector: project-kaiten
    operations:
      list_candidates: list_cards
      get_item: get_card
      get_relationships: get_card_links
  claude:
    connector: project-kaiten
    operations:
      list_candidates: list_cards
      get_item: get_card
      get_relationships: get_card_links
  opencode:
    connector: project-kaiten
    operations:
      list_candidates: list_cards
      get_item: get_card
      get_relationships: get_card_links
profile_config:
  candidate_filters:
    board: reserves-board
  field_mapping:
    external_id: id
    title: title
    description: description
    labels: tags
    source_version: updated_at
  label_hints:
    "Расчет запасов": {areas: [reserves/]}
    "UI": {areas: [frontend/]}
    "ИИ агент": {areas: [agent/]}
    "RAG": {candidate_domains: [rag]}
    "Рекомендации по бурению": {candidate_domains: [drilling-recommendations]}
```

Labels are hints, not module or Epic boundaries. `forge-intake-external-work` may map one external item to several Epics/Tasks or combine several items into one Epic. Approved relationships use compact keys such as `kaiten-product-board:card-123` in Backlog `Sources`, TASK `external_sources`, the Epic coverage matrix, and `.ai/integrations/work-items.yaml`.

The bundled work-source consumer is read-only. It never moves a card, writes a comment, or mirrors Forge status to Kaiten.

## Upgrade compatibility

Framework migration scans integration structure offline and classifies it as absent, current-supported, older-migratable, malformed, unsupported-future, custom-profile, or ownership collision.

- `absent` follows the clean Forge path.
- `current-supported` is preserved and remains available.
- `older-migratable` can be transformed only through a separate preview, approval, backup, staged validation, atomic apply, and rollback.
- `malformed`, `unsupported-future`, and `custom-profile` content is preserved; only incompatible consumers are blocked.
- `ownership_collision` blocks migration until resolved.

Framework upgrade never calls connectors. Local definitions/state are not managed-output lock inputs, so routine project changes do not look like Forge drift. Framework rollback keeps external identities and canonical work records and restores or selects a mutually compatible schema representation before re-enabling affected consumers.
