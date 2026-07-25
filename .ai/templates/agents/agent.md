<!-- TEMPLATE: .claude/agents/<name>.md — generic skeleton for a CUSTOM subagent. -->
<!-- Created in: Bootstrap Step 05. -->
<!-- Standard agents: implementation.md, validation.md, review.md, fuzzing.md -->
<!-- Use THIS skeleton only when a project needs an extra, non-standard agent. -->

---
name: <agent-name>
description: <One line: when the orchestrator should invoke this subagent.>
tools: <Optional: e.g. Read, Grep, Glob. Omit to inherit all tools.>
model: <Optional: inherit if omitted.>
---

# <Agent Name>

## Role

<Single responsibility. One sentence.>

## When invoked

<Trigger condition in the workflow.>

## Procedure

1. <step>

## Output

<What the agent returns to the orchestrator. Always a concise summary.>

## Must NOT

<Boundaries>

<!--
Cross-cutting subagent rules (apply to every agent):
- do NOT modify code unless explicitly assigned
- do NOT cross responsibilities
- communicate only via summaries to the orchestrator
Standard set: implementation (main), validation, review, fuzzing.
-->
