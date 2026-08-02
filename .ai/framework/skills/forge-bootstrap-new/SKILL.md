---
name: forge-bootstrap-new
description: Initialize AI Development Forge in a new product repository from a user prompt, linked brief, or iterative product interview. Use when the copied .ai bundle exists but canonical project documents and dual Codex/Claude adapters have not been created.
---

# Bootstrap a New Project

## Establish safety and configuration

1. Read `.ai/BOOTSTRAP.md`, `.ai/CONVENTIONS.md`, `.ai/framework/manifest.yaml`, `.ai/framework/contracts.yaml`, and `.ai/templates/project.yaml`.
2. Confirm this is a consumer product repository. If it is the AI Development Forge source repository itself, stop; never self-bootstrap the framework repository.
3. Inspect existing root files without overwriting unrelated user work.
4. Record the user's communication language as the documentation language. Keep framework control text, IDs, statuses, paths, and commands in English.
5. Prepare `.ai/project.yaml` with both Codex and Claude enabled, the bundled model defaults or explicit user-approved overrides, and the selected Git policy.

## Run the gated bootstrap

Follow the numbered workflows in order:

1. `.ai/01-product-discovery.md` — start from the supplied description or conduct an iterative interview; create a draft target-state `SPEC.md`.
2. `.ai/02-system-design.md` — interview for architecture, present alternatives, create proposed ADRs, and generate the decision index.
3. `.ai/03-release-planning.md` — create the Epic Roadmap and Defect Queue without Tasks or active work.
4. `.ai/04-prepare-workspace.md` — prepare one `READY` Epic only when the user wants to begin execution.
5. `.ai/05-create-platform-adapters.md` — confirm default or overridden model mappings and generate both native platform adapters.
6. `.ai/06-final-validation.md` — validate structure, lifecycle, references, adapter parity, and ownership.

Require explicit user approval at every document, ADR, Epic Start, and other gate defined by the numbered workflow. Do not automatically continue from one numbered step to the next.

## Preserve framework rules

- Create canonical documents at the project root, never inside `.ai/`.
- Write canonical content in the user's language by filling the provided templates; do not translate technical identifiers.
- Treat `.ai/` as the framework bundle, `.ai/project.yaml`, `.ai/framework.lock`, and `.ai/custom/` as project-owned state, and generated adapters as replaceable derived outputs.
- Create no default hooks, MCP configuration, framework CLI, or external lifecycle dependency.
- Never create separate progress, research, review, test, fuzzing, security, or validation Markdown reports.

Finish only after Step 06 passes and each required approval is recorded in canonical metadata.
