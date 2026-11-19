# Mutation campaigns

This is the normative process for `forge-mutation-test`. A campaign coordinates independent audit runs and their follow-up; it does not own development lifecycle state. The orchestrator writes records, the fast runner executes, the strong analyzer classifies, and ordinary Forge development workflows implement separately authorized changes.

## 1. Establish scope, objective and authority

Record the user's request, exact production/test paths, exclusions, backend/version/commands, dependency inputs and resource limits before execution. Missing setup produces `SETUP REQUIRED`; installation remains a separately authorized repository change. A campaign request may authorize all listed batches and verification rounds within a finite total budget: do not ask again at each unchanged batch. Analysis and remediation still need their own explicit authority; record existing grants rather than requiring repeated permission.

Choose the objective from the actual request:

- `metrics_only` (default): collect results; do not invoke analysis or create fixes.
- `audit`: collect results and explicitly authorized analysis; deliver classified findings, without requiring implementation.
- `hardening`: audit plus separately authorized development follow-up and mutation verification. A campaign request alone does not approve a new Epic, Replan, Task Start, acceptance or commit.

Choose `audit_first` by default: measure and analyze all batches before consolidating fixes. Choose `batch_then_fix` when the user requests incremental remediation: finish the current batch's analysis and disposition, handle approved fixes and verify them before moving to the next batch. Record any policy change and its reason. In metrics-only mode both policies just collect the ordered batches; there is no implied remediation.

## 2. Plan batches before running

A mutant is a generated code change, not a test case. Two thousand ordinary tests do not imply two thousand mutants or a particular number of batches.

Use one batch when the approved scope fits the per-run time budget and approximately 200 generated mutants. Otherwise partition production scope deterministically by component/file, critical paths first, aiming for at most 200 mutants per batch where the backend can enumerate or estimate them. This is a planning target, not a universal backend limit. With an estimated 2000 mutants, expect roughly ten batches, not 2000 model calls. Record the estimate, evidence and reason for the chosen partition.

If size/cost is unknown, start with a small explicit component as a pilot; keep the rest in the durable queue and refine estimates from its duration. Never silently run the entire unknown repository as a pilot. Use only backend-supported file/operator/ID selectors. If one file exceeds the target and cannot be split by the backend, retain it as a documented oversized batch under a finite time budget; do not invent sharding commands. Selected tests may overlap across batches, but production mutation selections must cover the declared scope with no unexplained gaps or duplicate counting. Test selection must exercise each batch's dependencies, not merely tests in the same folder.

Persist ordered batch IDs, exact selections, exclusions and reasons before execution. New batches append stable IDs; do not renumber old ones. A changed partition preserves previous attempts and records replaced/remaining selections. Scope expansion or a budget increase requires authority beyond the original grant. Record finite campaign execution time, per-run timeout/workers, analysis candidate budget and maximum verification rounds. Exhaustion pauses the campaign with exact remaining work; it never means completion.

## 3. Durable records and checkpoints

Use `quality/mutation-testing/registry.yaml` with optional `next_campaign_id` and `campaigns`, plus `campaigns/MTC-NNNN.yaml` from the campaign template. Allocate MTC identities monotonically, independently of MUT identities. Existing schema-1 registries with only runs and standalone MUT records remain valid; do not invent campaigns for historical runs. On first campaign creation initialize the optional keys from the largest retained identity.

Every actual execution attempt, including retry and verification, gets a fresh `MUT-NNNN`. Its optional `campaign` block names campaign, batch, purpose (`initial`, `retry`, `verification`, `refresh`) and predecessor runs. Deferred or continued analysis updates the same MUT record. Campaign and run links are reciprocal; the orchestrator persists related registry/record changes together and checks them on recovery. No history is created by bootstrap, adapter synchronization or migration.

Before and after every run, analysis slice, disposition, development handoff and verification, persist a checkpoint: state, batch, remaining candidate IDs/selections, last evidence, budget consumed, blockers and the exact next action. `next_action` is a recovery hint, never execution permission. Session history is unnecessary for continuation. Interrupted running attempts are reconciled from artifacts and fingerprints; unknown outcomes stay inconclusive, never assumed successful. Never allocate a second attempt merely to recover a known persisted result.

Campaign states:

| State | Meaning / next action |
| --- | --- |
| `planned` | Scope, ordered batches and authority recorded; execution has not started. |
| `running` | Execute the next authorized initial/retry/refresh batch. |
| `awaiting_analysis` | Resume the persisted unanalyzed candidate IDs within remaining analysis authority/budget. |
| `awaiting_decision` | A disposition, additional authority or explicit exception is required. |
| `waiting_for_fixes` | Approved development work is pending; retain return point and canonical work links. |
| `verifying` | Run authorized fresh mutation checks against changed inputs. |
| `paused` | User pause or exhausted budget; retain reason and resume state. |
| `blocked` | Missing backend/artifacts, failed baseline or unresolvable evidence; retain exact blocker. |
| `completed` | The objective-specific closure checks below passed. |
| `cancelled` | User stopped the campaign; retain unfinished scope and findings. |

Only explicit user direction resumes a user-paused campaign. A cancelled/completed campaign is retained as terminal history and later execution uses a new linked campaign. A budget pause may resume under a recorded extension. Other transitions follow the next eligible action, never a development Task/Epic status copied into the campaign.

## 4. Execute and analyze a batch

Run the ordinary baseline first. Check the exact scoped fingerprint before baseline, before mutation and after mutation. A failure blocks the batch; changed inputs make the attempt inconclusive. The runner never edits tracked tests or production code and does not stop just because it encounters its first survivor. Finish the authorized batch unless time, cancellation or another execution failure stops it. Partial output is retained with completed and unexecuted selections; it never counts as full batch coverage. Resume remaining selections only if the backend proves what is left; otherwise rerun the batch and supersede overlapping results in aggregation.

Persist generated/killed/survived/no-coverage/timeout/invalid-error separately, with backend score semantics. A timeout is not proof of a killed mutant. An unexpected zero-mutant run needs a recorded explanation, not a claim of adequate test strength.

For authorized analysis, select only current surviving/no-coverage/configured candidates. Use `(run_id, candidate_id)` identities; never assume backend IDs remain stable across revisions. Prioritize critical paths, then mutation classes. Record analyzed IDs and exact remaining IDs, plus each analysis slice and consumed budget, in the same run. Subsequent slices exclude already analyzed candidates. Missing retained normalized evidence or a changed scoped fingerprint blocks reuse. Do not restart the backend just to analyze another slice of current evidence.

Classify candidates using the existing analyzer classes. Group related actionable gaps into behavioral scenarios; do not create one Task per mutant. `likely_equivalent` remains a reasoned hypothesis; `unresolved` needs investigation or an explicit deferred/accepted-risk decision. A surviving mutant is not automatically a product defect. Analysis-budget exhaustion retains the exact queue and pauses; do not silently skip candidates to claim a complete audit.

## 5. Decide and hand off fixes

In `audit_first`, continue remaining audit batches after recording findings; consolidate related findings across batches before proposing development work. In `batch_then_fix`, the first batch with actionable findings enters `awaiting_decision` after its analysis, rather than moving silently to the next batch. Critical suspected product defects may justify offering an earlier policy change; do not silently change policy or development priority.

Record a disposition for each finding: `pending`, `no_change`, `deferred`, `fix_requested`, `verified`, or `accepted_risk`, including reason and decision reference. Classification alone is not authorization or a disposition. Follow-up uses current unaccepted Task feedback, compatible Replan, new test-hardening Epic, or bug intake for an observable defect in accepted code. One Epic may cover several batches; no automatic new Epic per batch. Preserve normal planning, Task Start, assurance, acceptance and commit rules.

After identities are approved, link campaign/batch/run/candidate IDs and the expected behavioral scenario in the owning Task/plan's existing context or verification section. Record those work references and the return action in the campaign and run disposition. Never preallocate invented TASK/Epic IDs. `waiting_for_fixes` observes the canonical work records; a completed Task does not prove a mutant killed. Declined or deferred work needs an explicit disposition and remains visible in the final limitations.

## 6. Return from development and verify

`forge-resume-development`, `forge-complete-task` and `forge-complete-epic` surface linked campaign return points, without making mutation a lifecycle gate or automatically running a backend. Finishing an Epic does not finish its mutation campaign. After the relevant fix work is accepted (or a separately authorized in-progress check), route back to `forge-mutation-test` with campaign ID. Existing bounded mutation authority may cover this return; otherwise record the missing authority. Mutation success never supplies Task/Epic acceptance.

First compare current production, test and declared dependency inputs against ALL completed batches. Mark affected batches stale, including batches affected by shared tests, fixtures or configuration. Preserve their history. Reuse unaffected results only with demonstrated unchanged scoped inputs; unknown dependency impact requires refreshing the potentially affected scope. Different base commits alone need not stale a batch if its complete scoped inputs demonstrably match. Never add metrics across incomparable scopes/backends or call historical evidence current.

Create a new MUT verification attempt for the repaired batch with a fresh baseline and fingerprint. Prefer full affected-batch verification. A targeted mutant/scenario rerun may give early feedback, but cannot replace full affected-batch coverage for final closure. Map old findings to new mutations by location/operator/behavior and evidence, not numeric ID alone. A disappeared mutant is `unresolved` until the behavioral change/exclusion is explained; it is not automatically killed. New survivors re-enter analysis and disposition. A surviving actionable finding returns to approved development feedback/Replan as needed. Count every verification round; stop at the recorded limit or budget and report what remains instead of looping indefinitely.

Under `batch_then_fix`, once the batch has current verification and every finding is verified or explicitly dispositioned, return to the FIRST unfinished batch in persisted order (or a stale earlier batch), not to the start of the whole campaign. Under `audit_first`, verify affected batches after the consolidated fixes. Prior fixes do not erase the queue in either policy.

## 7. Close honestly

Before closure, reconcile the full scope/partition, run coverage, current fingerprints, candidate ledger, findings, exceptions and remaining budgets. Select current non-overlapping evidence per batch; retain superseded attempts in history and never count retries twice. Report per-batch revisions if no single snapshot was tested. Summed counts require compatible backend semantics and disjoint mutation selections; do not average percentages. Missing, timed-out, invalid or unexecuted selections remain explicit limitations.

- `metrics_only`: all planned batches have complete current measurement evidence. Outcome `metrics_collected`; surviving candidates are allowed, analysis is explicitly not performed, and there is no claim of test hardening.
- `audit`: all planned measurements and candidate analyses are complete/current, with classified findings delivered. Outcome `analyzed`; unresolved classifications and unimplemented fixes remain visible. Audit completion does not mean findings were fixed.
- `hardening`: all planned measurements/analyses and affected full-batch verification are current, every actionable finding is verified, and no promised fix remains open. Outcome `verified`. Nonactionable findings require reasoned dispositions; 100% mutation score is not mandatory.
- Any objective with omitted scope, incomplete analysis, deferred/unresolved risks, unexplained error results or unverified promised fixes can close only with an explicit user decision naming those exact exceptions; outcome `accepted_exceptions`. Preserve residual scope/findings/work links and the decision. Do not present this outcome as fully verified. In an audit, an explicitly classified unresolved finding can be delivered as uncertainty without claiming resolution; missing analysis still needs an exception.

Otherwise retain the appropriate nonterminal state. User cancellation records `cancelled` and remaining work, not success. Closure records timestamp, outcome, evidence references, exceptions and a compact final summary in the campaign. No separate report Markdown is created for a run. Closed records remain available for later review; a changed repository or a new audit scope starts a new campaign linked by `previous_campaign_id`.

## Example: 2000 mutants with incremental remediation

Create MTC-0001 with about ten explicit batches and `batch_then_fix`, analysis authority and finite budgets. MUT-0001 measures B001; two analysis slices classify its survivors. Link several related gaps to one approved test-hardening Epic/Task set and persist `waiting_for_fixes`, B001, and the return action. After accepted fixes, MUT-0002 verifies B001 against the changed tests. Reconcile other batch fingerprints, then run B002 as MUT-0003. If B001 verification still has actionable survivors, return to its findings within the round limit; do not lose B002-B010. Close only when the selected objective's coverage and evidence conditions hold, or record user-accepted exceptions/cancellation. Under default `audit_first`, B002-B010 run before the consolidated repair work instead.
