---
document_type: investigation
id: INV-NNNN
subject: "<Short investigation subject>"
area: "<Component or product area>"
outcome: unresolved
created_at: "<YYYY-MM-DD>"
updated_at: "<YYYY-MM-DD>"
baseline_revision: "<Git revision or explicit working-tree description>"
relevant_paths: []
research_refs: []
---

# INV-NNNN — <Investigation Subject>

## Question

<What problem or uncertainty was investigated?>

## Scope

- **Included:** <Code, behavior, data, environment, or documentation examined.>
- **Excluded:** <Boundaries and deliberately unexamined areas.>
- **Authorization:** <Research only, or research and direct fix.>

## Investigation

<Methods chosen by the main agent: inspection, history, experiments, instrumentation, tests, benchmarks, profiling, or other relevant work. Keep a useful summary, not a chat transcript.>

## Evidence

| Evidence | Observation | Reproduction or source |
| --- | --- | --- |
| E-01 | <Observed fact> | <Command, path, measurement conditions, or canonical reference> |

## Causes

- **Confirmed:** <Cause supported by evidence, or —.>
- **Suspected:** <Remaining inference or alternative explanation, or —.>

## Conclusion

<What is known now, with facts clearly separated from inference and limitations.>

## Next Action

<Why no action is needed, a practical possible fix, the planned Bug/Epic route, the direct fix performed, or useful next experiments.>

## Direct Fix

Complete this section only for `outcome: fixed_directly`. Git remains authoritative for the exact line diff.

### Added

| Path | What and why |
| --- | --- |
| — | — |

### Modified

| Path | What and why |
| --- | --- |
| — | — |

### Removed

| Path | What and why |
| --- | --- |
| — | — |

- **Material effects:** <Behavior, interface, data, configuration, dependency, and documentation effects, or —.>
- **Verification:** <Exact commands/checks and results.>
- **Remaining risks or incomplete work:** <Details or —.>
- **Final revision, commit, or scoped diff:** <Reproducible reference.>

## Linked Work

- **Bugs:** <BUG-NNN or —>
- **Epics:** <EPIC-NNN or —>
- **Tasks/Replans:** <TASK-NNN, plan path, or —>

## Outcome History

| Date | Outcome | Reason or reference |
| --- | --- | --- |
| <YYYY-MM-DD> | <no_action/promoted/fixed_directly/unresolved> | <Reason or linked work> |
