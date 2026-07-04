<!-- TEMPLATE: .claude/agents/<name>.md — generic skeleton for a CUSTOM subagent. -->
<!-- Created in: Bootstrap Step 05. -->
<!-- For the 5 STANDARD subagents, copy the ready-made files in THIS directory: -->
<!--   context.md, code-context.md, implementation.md, validation.md, documentation.md -->
<!-- Use THIS skeleton only when a project needs an extra, non-standard agent. -->

---
name: <agent-name>
description: <One line: when the main agent should invoke this subagent.>
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

<What the agent returns. Always a concise summary, not raw dumps.>

## Must NOT

<Boundaries>

<!--
Cross-cutting subagent rules (apply to every agent, standard or custom):
- do NOT modify code unless explicitly assigned
- do NOT cross responsibilities
- communicate only via summaries
Standard set: context, code-context, implementation (main), validation, documentation.
-->
