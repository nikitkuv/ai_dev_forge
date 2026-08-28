## Context

The current reviewer contract treats implementation code, tests, and all code-owned artifacts as one actionable review surface. The TASK workflow therefore returns to implementation for any actionable issue in that combined surface and repeats the strong review after any code change. In practice, a reviewer can discover test-quality issues over several revisions while the production implementation remains unchanged, consuming a strong-model call for every test-only correction.

Forge already has a separate fast tester stage that owns execution of changed tests, affected-component tests, Task fuzz smoke, and scoped quality checks. The review boundary can therefore distinguish production correctness from verification-support quality without accepting failed tests.

## Goals / Non-Goals

**Goals:**

- Make only defects in the production surface block the strong review.
- Preserve useful reviewer observations about tests and other non-production files without turning them into review-loop triggers.
- Reuse a clean production review while its production fingerprint is unchanged.
- Leave executable verification and test-integrity enforcement to the tester gate after review.

**Non-Goals:**

- Ignore tests or remove them from the Review Packet.
- Allow a TASK to pass testing with broken, missing, weakened, or insufficient tests.
- Treat runtime configuration, schemas, migrations, packaging, or deployment behavior as non-production merely because they are not source-code files.
- Add lifecycle statuses, change reviewer model strength, or weaken Review Packet integrity checks.

## Decisions

### Classify by production effect rather than directory name

The Review Packet will separate `production_review_paths` from `supporting_evidence_paths`. Production paths include executable application or library code and runtime, data-contract, migration, packaging, build, or deployment artifacts whose contents can change the shipped system. Supporting paths include tests, fixtures, snapshots, golden files, test-only configuration, development tooling, examples, and other files that cannot change production behavior.

The orchestrator owns the classification and records its rationale for ambiguous files. A file that affects a production build, runtime contract, migration, or deployment remains production even if it resembles configuration or generated output. Canonical and lifecycle documents remain outside both review targets and continue to be context only.

### Separate production findings from non-blocking observations

The reviewer will inspect production paths in context and may consult supporting evidence. Its output will contain:

- production findings, severity ordered and outcome-affecting;
- non-production observations, each labeled advisory and grouped separately;
- packet-integrity status, acceptance traceability, protocol coverage, and optional diagnostics.

A missing or defective test, fixture, snapshot, assertion, test oracle, or dev-only file cannot by itself create a production finding. If such evidence exposes an actual production defect, the finding must identify the production location and concrete production failure; otherwise it remains a non-blocking observation. `CLEAN` means no actionable production finding remains and is compatible with non-production observations.

### Bind strong review reuse to a production fingerprint

The TASK record and Review Packet will carry both an implementation fingerprint and a production-surface fingerprint. A clean review is current when its production fingerprint matches the current production surface and its packet-integrity requirements remain satisfied.

Changing a production path invalidates review and testing evidence and requires another strong review. Changing only a supporting or non-production path preserves the clean production review, invalidates affected testing evidence, and proceeds to the tester gate without invoking the reviewer again. This is the core token-saving mechanism; changing only the reviewer's wording would still allow the orchestration loop to pay for redundant reviews.

### Keep tester failures blocking without making reviewer responsible for them

The tester remains responsible for running and evaluating changed tests, selected affected-component tests, Task fuzz smoke, scoped checks, coverage selection, and recorded test-integrity evidence. A tester failure returns the TASK to implementation. After remediation, the orchestrator compares production fingerprints: production changes require review and testing; supporting-only changes require testing only.

Reviewer observations are carried into the tester packet so the tester can exercise the relevant checks. They do not require automatic remediation before testing, and they do not alter the clean production-review outcome.

### Preserve packet-integrity blocking

Missing paths, inconsistent fingerprints, an unreproducible diff, or malformed reviewer output still blocks progression because the orchestrator cannot establish what was reviewed. This is an orchestration/input failure, not a production finding, and is not converted into an advisory observation.

## Risks / Trade-offs

- A test defect might be visible to the reviewer before the tester runs. -> Preserve it as an explicit observation and include it in the tester packet; selected testing still must pass.
- Incorrect path classification could hide a production-affecting file from blocking review. -> Classify by effect, require rationale for ambiguous paths, and contract-test representative runtime configuration, migration, packaging, and test-only cases.
- Reusing review after test changes means the reviewer does not assess the revised tests. -> This is intentional: the strong reviewer owns production correctness, while the tester owns test and verification gates.
- Multiple fingerprints add evidence complexity. -> Keep one whole implementation fingerprint for provenance and one production fingerprint solely for review freshness.

## Migration Plan

Update the framework-owned neutral sources, templates, documentation, and tests in one versioned release. Adapter synchronization propagates the updated neutral reviewer contract. Existing active TASK records without a production fingerprint require one classification and fresh strong review before review reuse is allowed; the framework must not infer a reusable clean review from legacy evidence.
