# knowledge-consolidation Specification

## Purpose

Review selected accumulated experience across records and propose evidence-backed corrections or promotion into existing Forge-owned knowledge and process targets without automatic policy changes.

## Requirements

### Requirement: Consolidation is explicit and bounded

The framework SHALL expose `forge-consolidate-knowledge` as an explicitly invoked orchestrator skill. It SHALL operate on a stated Epic, record set or topic, with a finite record budget and visible coverage. It SHALL inspect selected TASK/INV findings, relevant plans, ADRs and process follow-ups and identify duplication, contradictions, unsupported conclusions and missing references. It SHALL NOT start background work, invoke generated subagents, scan all transcripts, advance lifecycle state or require periodic execution.

#### Scenario: A completed Epic is reviewed
- **WHEN** the user requests consolidation for one Epic
- **THEN** the skill reviews a bounded selected corpus and reports checked sources, omissions and concrete findings without automatically expanding to all history

#### Scenario: The record budget is exhausted
- **WHEN** additional potentially relevant sources exceed the declared budget
- **THEN** the skill reports incomplete coverage and remaining candidates without claiming exhaustive review

### Requirement: Consolidation proposals retain evidence and owned destinations

Each proposed correction or promotion SHALL name the source claims, supporting or contradicting evidence, applicability, target owner and rationale. Mechanical recurring errors SHALL prefer deterministic helpers and regression tests; judgment errors SHALL prefer focused neutral-instruction corrections. Project rules and architectural decisions SHALL use their existing owned destinations. Unsupported hypotheses SHALL NOT become verified merely through summarization or repetition. Historical acceptance, test results and decisions SHALL NOT be silently overwritten.

#### Scenario: Repeated mechanical error
- **WHEN** several records demonstrate the same reproducible mechanical failure
- **THEN** the proposal identifies a helper/test target with evidence rather than appending a general warning to the router

#### Scenario: Duplicate untested explanations
- **WHEN** several notes repeat the same untested explanation
- **THEN** consolidation treats them as an unverified hypothesis and proposes a test or explicitly leaves them unresolved

### Requirement: Consolidation separates review from application

The skill SHALL return a compact review in the conversation, creating no separate canonical retrospective or wiki. Changes to source records, skills, templates, rules, contracts or ADRs SHALL use the existing appropriate authorized workflow, with concrete proposed edits before requesting any missing authorization. Corrections to accepted history SHALL be additive and preserve original evidence. An unaccepted proposal SHALL neither alter effective instructions nor satisfy a pending process follow-up. Existing authority remains valid within scope, without duplicate approval requests.

#### Scenario: Review only
- **WHEN** the user requests consolidation without authorizing a proposed instruction change
- **THEN** the skill presents the source-backed proposal and leaves instructions and statuses unchanged

#### Scenario: A correction is authorized
- **WHEN** a concrete correction is authorized through the existing applicable workflow
- **THEN** it is applied to its canonical owner with provenance, and generated adapters are updated only through normal synchronization
