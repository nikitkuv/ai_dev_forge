---
name: "{{ agent.id }}"
description: "{{ agent.description }}"
model: "{{ models.claude[agent.model_tier].model }}"
effort: "{{ 'high' if role_execution.mode == 'native_subagents' else models.claude[agent.model_tier].effort }}"
tools: {{ agent.claude_tools | join(", ") }}
---

{{ agent.instructions }}
