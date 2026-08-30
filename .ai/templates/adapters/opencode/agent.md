---
description: "{{ agent.description }}"
mode: subagent
model: "{{ models.opencode[agent.model_tier].model }}"
permission:
  read: allow
  glob: allow
  grep: allow
  list: allow
  edit: "{{ 'allow' if agent.write_policy.mode == 'assigned_scope' else 'deny' }}"
  bash: "{{ 'allow' if 'Bash' in agent.claude_tools else 'deny' }}"
  webfetch: "{{ 'allow' if 'WebFetch' in agent.claude_tools else 'deny' }}"
  websearch: "{{ 'allow' if 'WebSearch' in agent.claude_tools else 'deny' }}"
  external_directory: deny
  task: deny
  skill: deny
  todowrite: deny
---

{{ agent.instructions }}
