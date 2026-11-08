## ADDED Requirements

### Requirement: Search supports explicit all-term and any-term matching

The query interface SHALL accept an explicit matching mode `all` or `any`, defaulting to the existing all-term behavior. Any-term mode SHALL return records matching at least one supplied term, while preserving kind/area/date filters, bounded ranked pointers, deterministic ordering and source freshness reconciliation. Query text SHALL remain literal search input rather than executable search syntax. Empty input or an unsupported mode SHALL return a clear error.

#### Scenario: Backward-compatible default
- **WHEN** an existing caller supplies several terms without a matching mode
- **THEN** the query retains all-term matching

#### Scenario: Broader discovery with filters
- **WHEN** a caller chooses any-term matching with a record-kind filter
- **THEN** matching records from only those kinds are ranked even if they contain just one supplied term

#### Scenario: Literal query operators
- **WHEN** query text includes quotes or words resembling search operators
- **THEN** they are handled as escaped literal terms and cannot change the selected matching mode

### Requirement: Query telemetry is minimal and non-authoritative

Each CLI query attempt SHALL best-effort record a local event with time, supplied workflow label or unknown, matching mode, duration, result count when known and success/error outcome. It SHALL NOT store raw query text, document content, prompts, credentials or returned snippets. Aggregation SHALL distinguish invocations, zero-result responses and failures; it SHALL NOT infer useful reuse or task success from a query. Telemetry write failure SHALL be reported without changing the search result or hiding the original error. Telemetry SHALL affect neither ranking nor lifecycle gates and SHALL be disposable without affecting project state.

#### Scenario: Query finds candidates
- **WHEN** a workflow query successfully returns records
- **THEN** an event reports the invocation and result count without claiming the agent read or used any candidate

#### Scenario: Query or telemetry failure
- **WHEN** search fails or the local metrics destination is unwritable
- **THEN** the original search outcome remains visible, missing measurements stay unknown, and the telemetry issue does not create a lifecycle blocker
