---
name: forge-bootstrap-existing
description: Adopt AI Development Forge in an existing codebase by collecting repository evidence before the product interview, reconciling code/document/user conflicts, and then creating approved canonical documents plus enabled platform adapters.
---

# Bootstrap an Existing Project

## Collect evidence before interviewing

1. Read `.ai/BOOTSTRAP.md`, conventions, contracts, templates, and the project configuration template.
2. Confirm this is a consumer repository, not the AI Development Forge source repository itself.
3. Ask the `context-collector` for a local read-only inventory of code, tests, documentation, configuration, deployment material, issue artifacts, Git state, any existing product or architecture records, optional project-owned investigations, and integration definitions without invoking their connectors.
4. Summarize apparent behavior, protected compatibility constraints, missing tests, defects, technical debt, dependency risks, architecture violations, and contradictions.
5. Label each statement as code evidence, test evidence, documentation claim, user-confirmed intent, or inference.
6. Ask the user to choose enabled platforms and exactly one `role_execution.mode` for both `epic-planner` and `reviewer`: `claude_with_codex`, `codex_with_claude`, or `native_subagents`. For an OpenCode-led setup with no approved route, propose the existing `native_subagents` value by default but persist it only after approval and add no mode. Preserve an already approved route. Enabled OpenCode requires explicit non-empty `provider/model-id` mappings for all three tiers from user input or evidenced local `opencode models` output; do not invent a provider or install, authenticate, configure, preflight, or invoke external runtimes.

Current behavior is evidence, not product truth. Present conflicts and ask the user which target behavior is authoritative. Do not silently copy accidental implementation behavior into canonical documents.

## Run the gated bootstrap

Follow all six numbered workflows:

1. Use `.ai/01-product-discovery.md` to interview from the evidence and create a draft target-state `SPEC.md`.
2. Use `.ai/02-system-design.md` to compare current and target architecture, approve significant ADRs, and create `ARCHITECTURE.md` plus generated `DECISIONS.md`.
3. Use `.ai/03-release-planning.md` to present discovered feature, defect, debt, and risk candidates; add only user-approved items to `BACKLOG.md`.
4. Use `.ai/04-prepare-workspace.md` when the user selects a `PLANNED + READY` Epic for detailed planning. Plan Approval creates a queued `execution/planned/` workspace even when dependencies, blockers, or another active Epic defer the separate Epic Start.
5. Use `.ai/05-create-platform-adapters.md` to confirm every enabled model mapping and generate Codex, Claude, and enabled OpenCode adapters.
6. Use `.ai/06-final-validation.md` to validate the adopted repository without changing product code.

Require explicit user approval at every numbered step and every document, ADR, Plan Approval, Replan, Epic Start, and collision gate. Never advance automatically.

## Preserve existing work

- Preview all canonical replacements and adapter collisions before writing.
- Do not add discovered candidates to SPEC, architecture, or Backlog without a user decision.
- Do not create a planned workspace or activate an Epic unless the corresponding explicit gate was granted.
- Do not create synthetic investigation records, default hooks, MCP configuration, CLI dependencies, a local integration registry, or an external lifecycle layer. Preserve existing `investigations/` and `.ai/integrations/` as project-owned and treat their absence as the clean baseline.
- Keep canonical documents in the user's language and framework control files in English.
- Create no separate report Markdown files.

Finish only after Step 06 passes and unresolved evidence conflicts are either resolved or explicitly recorded.
