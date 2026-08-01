---
name: "{{ agent.id }}"
description: "{{ agent.description }}"
model: "{{ models.claude[agent.model_tier].model }}"
tools: {{ agent.claude_tools | join(", ") }}
---

{{ agent.instructions }}
