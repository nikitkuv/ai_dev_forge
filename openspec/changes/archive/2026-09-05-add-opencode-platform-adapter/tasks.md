## 1. Platform Contract and Configuration

- [x] 1.1 Increment the framework minor version and extend the manifest, generated-output ownership, protected OpenCode paths, adapter list, and existing `native_subagents` route description for a third `opencode` platform without adding a route mode.
- [x] 1.2 Extend `.ai/templates/project.yaml`, bootstrap, and migration guidance with `platforms.opencode.enabled` plus explicit provider-qualified `strong`, `balanced`, and `fast` model resolution; preserve disabled-platform and no-install/no-auth behavior.
- [x] 1.3 Update bootstrap, migration, the shared root router template, and neutral agent/platform references so an OpenCode-led workflow proposes the existing `native_subagents` value by default when no approved route exists, records it only after approval, preserves existing choices, and keeps cross-runtime orchestrator mismatch and no-fallback rules explicit.

## 2. Native OpenCode Adapter Generation

- [x] 2.1 Add the native `.ai/templates/adapters/opencode/agent.md` renderer template with UTF-8-without-BOM frontmatter, `mode: subagent`, provider-qualified tier model, deterministic permissions, and the unchanged neutral role body.
- [x] 2.2 Define and apply deterministic OpenCode permission mapping for all eleven neutral agents, allowing edits only for the implementer, command or research access only where required, and denying nested tasks and external-directory access for every generated subagent.
- [x] 2.3 Extend adapter creation and synchronization to stage, validate, and replace `.opencode/agents/<manifest-id>.md` atomically with Codex and Claude outputs while reusing `AGENTS.md` and `.agents/skills/` and preserving every unlisted `.opencode/` path.
- [x] 2.4 Extend `.ai/framework.lock` provenance, collision detection, obsolete-file handling, rollback, and migration rules to include only manifest-managed OpenCode agent entries.

## 3. Validation and Regression Coverage

- [x] 3.1 Extend final-validation and framework-check guidance for OpenCode agent membership, router and skill discovery, model resolution, permissions, UTF-8/BOM format, native routing, cross-runtime mismatch, parity, and protected project-owned files.
- [x] 3.2 Add contract tests that parse representative OpenCode agent frontmatter and cover all manifest IDs, tier models, permission boundaries, shared router/skills, atomic replacement language, unresolved and disabled model cases, collisions, no fallback, and preservation of project-owned OpenCode content.
- [x] 3.3 Run focused new contract tests, the repository-evidenced `node --test tests/*.test.mjs` suite, and strict OpenSpec validation when the CLI is available; reconcile maintained source counts, framework version assertions, and generated-output expectations.

## 4. User-Facing Documentation

- [x] 4.1 Update `README.md`, `FRAMEWORK.md`, `RUNBOOK.md`, `MIGRATION.md`, bootstrap prompts, and relevant scenarios to explain OpenCode setup, explicit provider/model selection, generated paths, `native_subagents`, shared skills, preserved configuration, and unsupported automatic installation/authentication.
- [x] 4.2 Update diagrams or platform tables that currently assume exactly two adapters and verify that no maintained guidance tells users to duplicate OpenCode skills or edit generated OpenCode agents directly.
