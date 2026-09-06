---
name: {{ agent.id | tojson }}
description: {{ agent.description | tojson }}
model: {{ models.claude[agent.model_tier].model | tojson }}
effort: {{ ('high' if role_execution.mode == 'native_subagents' else models.claude[agent.model_tier].effort) | tojson }}
tools: {{ agent.claude_tools | join(", ") | tojson }}
---

{{ agent.instructions }}
