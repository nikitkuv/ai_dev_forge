## Purpose

Provides a lightweight way for the main agent to investigate a codebase problem outside the standard workflow, preserve the result, and either promote or directly fix it.

## ADDED Requirements

### Requirement: Forge provides standalone main-agent investigation
Forge SHALL provide an explicitly invoked `forge-investigate` workflow that can run without selecting, creating, starting, or advancing a Bug, Epic, or TASK. The main agent SHALL conduct the investigation directly and SHALL NOT invoke framework subagents. The agent MAY choose the investigation methods appropriate to the question while respecting the user's scope, repository instructions, and existing safety permissions.

#### Scenario: Investigate a slow algorithm
- **WHEN** the user asks the agent to investigate why an algorithm is slow outside Backlog work
- **THEN** the main agent inspects the code, runs appropriate bounded experiments, and determines or narrows the cause without starting the standard development workflow

#### Scenario: Investigation needs broader authority
- **WHEN** useful research requires production access, destructive action, external side effects, secrets, or a materially broader scope than the user authorized
- **THEN** the agent explains the need and obtains the applicable permission before proceeding

### Requirement: Every material investigation has one canonical record
Forge SHALL allocate a monotonic `INV-NNNN` identifier and store one document at `investigations/INV-NNNN-<short-name>.md`. The document SHALL record the question, scope and exclusions, relevant code and canonical context, baseline revision or working-tree state, investigation performed, material evidence, confirmed or suspected causes, conclusion, limitations, and next action. The record SHALL distinguish observed evidence from inference and SHALL be sufficient for another agent to understand the result without relying on chat history.

#### Scenario: Cause is found
- **WHEN** the agent confirms why the algorithm is slow
- **THEN** the investigation record contains the cause, supporting measurements or observations, affected code, limitations, and a suggested correction

#### Scenario: Cause remains unresolved
- **WHEN** the available evidence is insufficient to select one cause
- **THEN** the record preserves eliminated and remaining hypotheses, evidence collected, blockers, and useful next experiments

### Requirement: Every investigation records one simple outcome
The investigation record SHALL identify its current `outcome` as `no_action`, `promoted`, `fixed_directly`, or `unresolved`. `no_action` SHALL explain why no change was made and MAY include a possible future fix. `promoted` SHALL link the approved Bug, Epic, Replan, or TASK. `fixed_directly` SHALL include the direct-change record and verification evidence. `unresolved` SHALL preserve the remaining questions and next experiments. An outcome MAY be updated later while retaining the prior disposition in history.

#### Scenario: Nothing is changed
- **WHEN** the investigation is useful but the user decides not to act
- **THEN** the INV records `outcome: no_action`, the reason, and any useful future recommendation

#### Scenario: Result is handed to normal work
- **WHEN** the user approves creating a Bug, Epic, Replan, or TASK from the investigation
- **THEN** the INV records `outcome: promoted` and reciprocal links to that canonical work

#### Scenario: Main agent fixes the issue
- **WHEN** the main agent completes the correction within the investigation
- **THEN** the INV records `outcome: fixed_directly` and the required change and verification evidence

### Requirement: The main agent can fix the investigated problem directly
Forge SHALL allow the main agent to implement a fix in the same investigation when the user explicitly asks to investigate and fix, or authorizes the fix after reviewing the cause. The agent SHALL remain within the authorized problem scope, resolve product or architecture ambiguity with the user, preserve unrelated changes, apply verification proportionate to the affected surface, and record the final result in the investigation document. This route SHALL NOT require creation of an Epic or TASK or invocation of reviewer, tester, implementer, or planner subagents.

#### Scenario: Investigation and fix are requested together
- **WHEN** the user asks the main agent to find and fix the cause
- **THEN** the agent may move directly from investigation to implementation and verification without a separate Task Start

#### Scenario: The fix needs a product decision
- **WHEN** several fixes imply materially different required behavior or architecture
- **THEN** the agent presents the decision and does not silently choose or change canonical intent

### Requirement: Direct fixes have a durable change record
For a directly fixed investigation, the canonical record SHALL identify every added, modified, and removed path; summarize what changed in each path and why; record relevant behavior, interface, data, configuration, dependency, and documentation effects; list verification commands and results; state remaining limitations or risks; and bind the summary to the final revision, commit, or reproducible scoped diff when available. Forge SHALL NOT require the document to duplicate the complete source diff because Git remains authoritative for exact code changes.

#### Scenario: Agent completes a direct fix
- **WHEN** the investigated problem is fixed and scoped checks pass
- **THEN** the record contains the path-level change summary, verification evidence, and final revision or diff reference

#### Scenario: Implementation is only partial
- **WHEN** the agent improves the problem but does not complete all intended corrections
- **THEN** the record describes completed and remaining work explicitly and does not claim `outcome: fixed_directly`

### Requirement: Investigation results can be reused during planning
Bug intake, feature intake, Replan, and Epic planning SHALL accept explicit `INV-NNNN` references and SHALL look for clearly relevant investigation documents when their recorded area overlaps the proposed work. A planner SHALL reuse applicable evidence, causes, risks, and suggested verification instead of repeating the complete investigation, but SHALL check whether the recorded relevant files or assumptions changed materially. The resulting Bug, Epic plan, or TASK SHALL cite every investigation it relies on.

#### Scenario: New Epic uses prior research
- **WHEN** an investigation about the same component is referenced or clearly relevant and its context is still applicable
- **THEN** the Epic planner uses its conclusions and proposed fix as planning input and records the `INV-NNNN` reference

#### Scenario: Relevant code changed after research
- **WHEN** material investigated code or assumptions changed after the investigation
- **THEN** the planner rechecks the affected conclusions before using them and does not blindly repeat or trust the entire record

### Requirement: Investigations do not silently control lifecycle or Git
Creating, updating, concluding, promoting, or directly fixing an investigation SHALL NOT by itself change Epic or TASK status, satisfy development gates, imply user acceptance, or authorize a commit. If investigation edits make existing TASK or Epic evidence stale, Forge SHALL report that through the existing resume and validation rules. A commit of direct investigation changes SHALL follow the project's configured Git policy and applicable explicit authorization.

#### Scenario: Investigation occurs beside existing work
- **WHEN** an ad hoc investigation changes code relevant to existing planned or active work
- **THEN** Forge preserves the investigation result and reports any affected lifecycle evidence or scope that must be reconciled

#### Scenario: Fix is verified but not committed
- **WHEN** direct investigation changes pass their checks but no commit authorization exists
- **THEN** Forge records the verified working-tree result and leaves it uncommitted
