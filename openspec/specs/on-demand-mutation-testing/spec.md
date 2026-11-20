# On-Demand Mutation Testing Specification

## Purpose

Provide reproducible, explicitly requested mutation-testing audits of existing test suites without coupling those audits to Forge development lifecycle state or mandatory quality gates.

## Requirements

### Requirement: Discuss and approve the concrete execution plan
Before starting the baseline the orchestrator SHALL discuss the exact proposed files, tests, inputs, exclusions, backend selectors and commands, ordered batches and resource limits with the user. Approval SHALL identify both the user decision and the specific plan. Existing approval SHALL carry across unchanged batches. A revised plan SHALL return to the user before execution.

#### Scenario: The agent selects files
- **WHEN** a user asks for an audit and delegates file selection
- **THEN** the orchestrator presents the selection and rationale and waits for approval before baseline or mutation execution
- **AND** a changed file selection or increased limit fails the original approval check

#### Scenario: A repaired finding returns from development
- **WHEN** an approved repair returns from Task completion
- **THEN** ordinary hardening closure requires mapped evidence from a successful current full-batch verification or refresh linked to the source run and batch
- **AND** the checkpoint preserves the next unfinished batch

### Requirement: Campaigns preserve ordered bounded execution and continuation
New mutation audits SHALL persist an independent `MTC-NNNN` campaign with exact ordered batches, objective, policy, authorization, finite cumulative execution/analysis budgets, verification-round limit and recovery checkpoint. Small scopes SHALL use one batch; larger scopes SHALL use backend-supported component/file selections with a planning target of 200 mutants per batch, documented exceptions and explicit coverage of the declared scope. Unknown cost SHALL use a small scoped pilot. Legacy standalone MUT records SHALL remain valid without conversion.

#### Scenario: Two thousand estimated mutants
- **WHEN** the selected scope is estimated at 2000 mutants and backend selection supports partitioning
- **THEN** the orchestrator records approximately ten bounded batches before execution and continues authorized batches within budget without repeating permission requests
- **AND** the number of ordinary tests is not used as a mutant count

#### Scenario: Unknown backend partition capability
- **WHEN** the backend cannot shard an oversized file or report an exact remainder
- **THEN** the orchestrator records the limitation and uses an explicit bounded full selection rather than inventing commands or claiming complete partial coverage

### Requirement: Campaign policy determines when findings enter development
The default policy SHALL be `audit_first`, collecting and analyzing all authorized batches before consolidating remediation. Explicit `batch_then_fix` SHALL preserve a return point after the current batch's analysis, route approved fixes through existing development workflows, and verify that batch before proceeding. Metrics-only SHALL never imply analysis or remediation. Finding classifications SHALL remain separate from dispositions and approval.

#### Scenario: Survivors in the first batch
- **WHEN** the first batch contains survivors under `audit_first`
- **THEN** the orchestrator completes the bounded batch, records authorized analysis and continues the remaining audit queue without automatically creating development work

#### Scenario: Incremental test hardening
- **WHEN** `batch_then_fix` finds actionable gaps and the user approves repair work
- **THEN** the orchestrator stores campaign/batch/run/candidate references and a return action in campaign and approved work records, waits for fixes, and does not require a separate Epic for each batch

### Requirement: Analysis and execution resume from durable identities
The system SHALL retain exact analyzed and remaining candidate IDs scoped to a MUT run, analysis slices and consumed budgets. Continuation SHALL use remaining candidates without rerunning a current backend result or reanalyzing completed slices. Interrupted or partial execution SHALL retain known completed and remaining selections and SHALL NOT count incomplete coverage as a completed batch. Session history SHALL NOT be required to reconstruct the next action.

#### Scenario: Analysis resumes in another session
- **WHEN** one analysis slice is complete and its normalized artifact and scoped inputs remain current
- **THEN** the next slice updates the same MUT record using only remaining IDs and remaining cumulative budget

#### Scenario: Execution budget exhausted
- **WHEN** a campaign reaches its execution, analysis or verification limit with work remaining
- **THEN** it pauses with the exact remainder and resumes only within an authorized extension, never silently completing or repeating indefinitely

### Requirement: Development completion returns to fresh mutation verification
Linked Task/Epic completion and development resume SHALL surface the campaign return point without running a backend or adding a lifecycle gate. Accepted fixes SHALL NOT count as killed mutants. Each verification/refresh SHALL allocate a new MUT record, recheck all potentially affected batch fingerprints including shared inputs, and reconcile old/new findings by behavioral evidence rather than backend numeric ID. Full affected-batch evidence SHALL be required for ordinary hardening closure.

#### Scenario: First batch fixed and verified
- **WHEN** approved B001 repairs have current full-batch verification under `batch_then_fix`
- **THEN** the campaign continues the first unfinished or stale batch from its persisted queue, including B002 when it is next, without losing other batches

#### Scenario: Shared fixture changes
- **WHEN** a repair changes a shared test fixture used by previously measured batches
- **THEN** every affected batch is marked stale and refreshed before its evidence contributes to ordinary closure

#### Scenario: Mutant disappears after a fix
- **WHEN** a prior mutant ID is absent from the new backend output
- **THEN** the finding remains unresolved until a behavior/location/operator mapping or an explicit disposition explains it; absence alone is not a kill

### Requirement: Campaign closure reflects the requested objective and residual work
Campaigns SHALL close as `metrics_collected`, `analyzed`, or `verified` only with complete current evidence appropriate to `metrics_only`, `audit`, or `hardening` respectively. Retries SHALL NOT be double-counted; incomparable results SHALL NOT be presented as one current score. Omitted work or unverified promised fixes SHALL require an explicit `accepted_exceptions` decision identifying the residual risk. Cancellation SHALL preserve remaining work as cancellation rather than success. Closed history SHALL remain available and subsequent campaigns SHALL link to it rather than rewriting it.

#### Scenario: Metrics-only campaign has survivors
- **WHEN** all planned measurements are complete/current but analysis was not requested
- **THEN** the campaign may close as `metrics_collected` while explicitly reporting unanalyzed survivors and making no hardening claim

#### Scenario: Repair Epic accepted with verification pending
- **WHEN** a repair Epic is accepted but required campaign verification is missing or stale
- **THEN** development acceptance remains independent and the campaign stays unfinished unless the user explicitly accepts the named exceptions

#### Scenario: Complete hardening with equivalent mutants
- **WHEN** every actionable finding is verified, remaining nonactionable findings have reasoned dispositions and full required evidence is current
- **THEN** the campaign may close as `verified` without demanding a 100 percent mutation score

### Requirement: Mutation testing is an independent on-demand operation
The system SHALL start mutation testing only after an explicit user request that identifies or approves the production-code scope, and SHALL permit the operation regardless of whether any Epic or TASK exists or which lifecycle status it has. Starting, completing, blocking, cancelling, or analyzing a mutation run MUST NOT change Backlog, Epic, TASK, review, testing, validation, fuzzing, acceptance, or commit state; satisfy a development quality gate; or invalidate development evidence.

#### Scenario: Run without active development work
- **WHEN** the user requests mutation testing for an approved repository scope and no Epic or TASK is active
- **THEN** the system runs the independent mutation workflow without creating or activating development work

#### Scenario: Run during active development
- **WHEN** the user requests mutation testing while a TASK or Epic is in any nonterminal state
- **THEN** the system runs the mutation workflow without changing that TASK or Epic or its evidence

### Requirement: Mutation execution uses an exact reproducible scope
Before invoking a mutation backend, the system SHALL record an exact source scope, test scope, backend command and version, execution budget, and reproducible fingerprint covering the tested source and tests. The system SHALL run the unmutated baseline first and SHALL NOT treat mutation results as valid when the baseline fails or the scoped fingerprint changes during execution.

#### Scenario: Passing baseline on stable scope
- **WHEN** the baseline passes and the scoped fingerprint remains unchanged through execution
- **THEN** the system may complete the mutation campaign and associate its metrics with that exact fingerprint

#### Scenario: Baseline failure
- **WHEN** the selected ordinary tests fail before mutation execution
- **THEN** the system records a blocked or inconclusive run and does not invoke semantic mutation analysis

#### Scenario: Scope changes during a run
- **WHEN** production code or tests covered by the recorded scope change before the run completes
- **THEN** the system records the result as inconclusive and does not present it as current evidence

### Requirement: Fast runner performs bounded mechanical execution
The system SHALL provide a fast-tier mutation runner that invokes only a configured or explicitly approved mutation backend and ordinary test command. The runner SHALL limit writes to temporary files, caches, logs, coverage data, backend outputs, and normalized runtime artifacts, and SHALL NOT install tools, edit tracked production code or tests, apply a mutant to the working tree, create development work, change canonical lifecycle state, or invoke another agent.

#### Scenario: Configured backend is available
- **WHEN** the approved backend, scope, commands, and budget are available
- **THEN** the runner executes the baseline and mutation campaign and returns normalized metrics plus artifact references to the orchestrator

#### Scenario: Backend setup is missing
- **WHEN** no compatible backend or reproducible command is configured or approved
- **THEN** the runner returns `SETUP REQUIRED` without installing a dependency or editing repository configuration

### Requirement: Strong analysis is separately authorized and conditional
The system SHALL support metrics-only mutation runs without invoking a strong model. It SHALL invoke the strong-tier mutation analyzer only when the user explicitly requests immediate or deferred analysis, the run artifacts are current for the recorded fingerprint, and the normalized result contains surviving, uncovered, or otherwise explicitly configured analysis candidates. The analyzer SHALL NOT be invoked when there are no candidates, the baseline failed, setup is missing, or the run result is unusable.

#### Scenario: Metrics-only request
- **WHEN** the user requests mutation testing without authorizing semantic analysis
- **THEN** the system completes and records the runner result without invoking the mutation analyzer

#### Scenario: Analysis requested but all mutants are killed
- **WHEN** analysis is authorized but the runner reports no surviving, uncovered, or configured candidates
- **THEN** the system records analysis as skipped because no candidates exist and does not invoke the strong model

#### Scenario: Deferred analysis
- **WHEN** the user requests analysis of a prior run whose fingerprint and required artifacts are still current
- **THEN** the system invokes the analyzer on those artifacts without repeating the mutation campaign

#### Scenario: Bounded partial analysis
- **WHEN** the number of candidates exceeds the user-approved analysis budget
- **THEN** the analyzer prioritizes and analyzes only the bounded subset and records the analysis as partial with the remaining candidate count

### Requirement: Analyzer returns evidence-backed classifications without remediation
For every analyzed candidate, the analyzer SHALL return a classification, confidence, affected production location, relevant existing tests, behavioral gap or equivalence rationale, and a suggested test scenario when applicable. The analyzer SHALL limit writes to runtime analysis artifacts and SHALL NOT edit production code or tests, install tools, create development work, change lifecycle state, or invoke another agent.

#### Scenario: Actionable survivor
- **WHEN** a surviving mutation changes required behavior that existing tests do not observe
- **THEN** the analyzer classifies it as an actionable test gap with evidence and a suggested ordinary test scenario

#### Scenario: Likely equivalent mutation
- **WHEN** a surviving mutation does not produce an observable behavioral difference in the approved scope
- **THEN** the analyzer records a likely-equivalent classification and its rationale rather than reporting a confirmed test defect

### Requirement: Every attempt has durable lifecycle-independent history
The system SHALL allocate a unique `MUT-NNNN` identifier and persist a compact project-owned record for every requested mutation attempt, including unsuccessful, cancelled, partial, and metrics-only attempts. The record SHALL contain timestamps, scope, fingerprint, commands and tool versions, budgets, baseline result, normalized metrics, artifact references or retention state, analysis authorization and status, compact findings, and any later user-approved disposition. A registry SHALL index the records without making them development lifecycle artifacts.

#### Scenario: Successful metrics-only run
- **WHEN** the runner completes and semantic analysis was not requested
- **THEN** the system writes a `MUT-NNNN` record with metrics and `analysis.status: not_requested` and updates the independent registry

#### Scenario: Setup-required attempt
- **WHEN** the requested run cannot start because no approved backend is available
- **THEN** the system still writes a `MUT-NNNN` record containing `SETUP REQUIRED` and the exact missing capability

#### Scenario: Later analysis updates the same record
- **WHEN** deferred analysis completes for a current recorded run
- **THEN** the system updates that run's analysis section rather than allocating a second mutation-run identity

### Requirement: Follow-up development work requires a separate user decision
Mutation findings SHALL remain diagnostic records unless the user separately approves their disposition. The system SHALL NOT automatically create a Bug, TASK, Epic, Replan, priority change, or remediation action from a mutation result. When the user later chooses development work, the system SHALL route it through the existing applicable intake or Replan workflow and MAY add informational references back to the mutation record.

#### Scenario: User retains no follow-up work
- **WHEN** the user reviews mutation findings and declines remediation
- **THEN** the system preserves the mutation record and makes no development-state change

#### Scenario: User requests test hardening
- **WHEN** the user separately approves work to improve tests based on mutation findings
- **THEN** the system uses the existing development workflow and records only optional references from the mutation record to the approved work
