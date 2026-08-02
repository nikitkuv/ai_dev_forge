---
name: "{{ agent.id }}"
description: "{{ agent.description }}"
model: "{{ models.claude[agent.model_tier].model }}"
effort: "{{ models.claude[agent.model_tier].effort }}"
tools: {{ agent.claude_tools | join(", ") }}
---

{{ agent.instructions }}
