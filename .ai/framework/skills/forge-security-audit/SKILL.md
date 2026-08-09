---
name: forge-security-audit
description: Orchestrate an explicitly requested security review of a Forge project and route accepted findings into existing canonical work. Use only when the user asks for a security audit or vulnerability analysis.
---

# Run a Security Audit

## Require explicit scope

1. Confirm the user's explicit request and exact repository scope.
2. Default to local, read-only analysis with:
   - no source or canonical edits;
   - no tool installation;
   - no network access or vulnerability database download;
   - no production, external-target, or active exploitation scan.
3. Invoke the strong `security-auditor` with the approved local scope and relevant SPEC, architecture, ADR, dependency, and trust-boundary context.

Network access, scanner installation, external targets, production access, credential use, active scanning, or exploit verification each require separate user authorization that names exact targets, tools, limits, and safety constraints. Do not infer expanded permission from the general audit request.

## Review and route findings

1. Present each finding with severity, confidence, affected asset, realistic impact, evidence, and remediation direction.
2. Separate confirmed findings, defense-in-depth improvements, and uncertain hypotheses.
3. Ask the user which findings to retain and how to schedule them.
4. Persist accepted findings through existing artifacts:
   - use the current unaccepted TASK when the issue was introduced there;
   - add a confirmed issue in accepted code to the Backlog Defect Queue;
   - create a `PLANNED/OUTLINE` security Epic for broader work;
- use Replan for approved changes to a planned or active Epic.

Do not create a security report Markdown file. Do not edit code, create Bugs, Epics, or TASK files, change priority, or start remediation without the applicable user approval and lifecycle gate.

Return the audit scope, compact findings, user decisions, canonical updates, and next gate to the user.
