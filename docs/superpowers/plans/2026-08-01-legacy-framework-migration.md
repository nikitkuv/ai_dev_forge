# Legacy Framework Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (\`- [ ]\`) syntax for tracking.

**Goal:** Add a single-source \`.ai-next/\` migration workflow that preserves canonical project state, structurally updates root routers, safely replaces legacy Forge adapters, and consolidates user guidance in root \`MIGRATION.md\`.

**Architecture:** Keep \`.ai/\` as the only committed framework payload and add \`.ai/MIGRATE.md\` as the executable migration entrypoint. A consumer stages the same payload as \`.ai-next/\`; Forge builds and validates candidate framework/router/adapter outputs, applies them with backup and rollback, and writes the first lock only after success. Python standard-library contract tests enforce protected paths, local adapter ownership, overlay rendering, documentation consolidation, and absence of a duplicate migration payload.

**Tech Stack:** Markdown and YAML framework contracts, Python standard-library \`unittest\`, Git sparse checkout, PowerShell and POSIX shell examples.

## Global Constraints

- The framework repository keeps exactly one release source: \`.ai/\`.
- Fresh initialization starts from \`.ai/BOOTSTRAP.md\`; upgrade stages the same payload at \`.ai-next/\` and starts from \`.ai-next/MIGRATE.md\`.
- \`SPEC.md\`, \`ARCHITECTURE.md\`, \`BACKLOG.md\`, \`DECISIONS.md\`, \`decisions/\`, \`execution/\`, project-specific documents, product code, and tests are read-only during migration.
- Canonical schema differences are findings, never migration writes.
- Forge installs no global agents or skills.
- Adapter synchronization manages manifest-declared Forge IDs and preserves unlisted project-owned files.
- \`AGENTS.md\` and \`CLAUDE.md\` are rendered from current templates plus durable \`.ai/custom/\` overlays.
- Root \`MIGRATION.md\` is the only user-facing framework migration guide.
- Do not edit derived \`build/\`, \`dist/\`, or \`.worktrees/\` content manually.

---

### Task 1: Executable migration contract and user guide

**Files:**
- Create: \`tests/__init__.py\`
- Create: \`tests/test_migration_contract.py\`
- Create: \`.ai/MIGRATE.md\`
- Create: \`MIGRATION.md\`

**Interfaces:**
- Consumes: current \`.ai/framework/manifest.yaml\`, old active \`.ai/\`, staged \`.ai-next/\`, Git repository state.
- Produces: the \`.ai-next/MIGRATE.md\` agent entrypoint and the root human workflow for local copy or GitHub \`main\` sparse checkout.

- [ ] **Step 1: Write failing entrypoint and protected-path tests**

Create \`MigrationContractTests\` with a UTF-8 \`read(path)\` helper and these assertions:

\`\`\`python
def test_single_payload_and_entrypoints(self):
    self.assertTrue((ROOT / ".ai/MIGRATE.md").is_file())
    self.assertTrue((ROOT / "MIGRATION.md").is_file())
    self.assertFalse((ROOT / ".ai-next").exists())
    self.assertFalse((ROOT / ".ai-migration").exists())

def test_migrate_contract_freezes_project_state(self):
    text = self.read(".ai/MIGRATE.md")
    for value in (
        "SPEC.md", "ARCHITECTURE.md", "BACKLOG.md", "DECISIONS.md",
        "decisions/", "execution/", "project source code", "tests",
        "canonical schema",
    ):
        self.assertIn(value, text)
    self.assertIn("read-only", text)
    self.assertIn("rollback", text)

def test_user_guide_stages_main_as_ai_next(self):
    text = self.read("MIGRATION.md")
    self.assertIn("https://github.com/nikitkuv/ai_dev_forge.git", text)
    self.assertIn("--branch main", text)
    self.assertIn("sparse-checkout set .ai", text)
    self.assertIn(".ai-next", text)
    self.assertIn("Read .ai-next/MIGRATE.md", text)
\`\`\`

- [ ] **Step 2: Run tests and verify RED**

Run: \`python -m unittest tests.test_migration_contract -v\`

Expected: FAIL because \`.ai/MIGRATE.md\` and \`MIGRATION.md\` do not exist.

- [ ] **Step 3: Write \`.ai/MIGRATE.md\`**

Write ordered imperative stages: distinct old/staged bundles; read-only inventory and protected hashes; legacy/custom/unknown classification; router overlay extraction; complete preview and approval; backup; staged candidates; apply; validate; lock-after-success; full rollback.

- [ ] **Step 4: Write root \`MIGRATION.md\`**

Document prerequisites, local copy, PowerShell and POSIX Git sparse-checkout commands, exact prompt, preview, success, and rollback. Staging must fail if \`.ai-next/\` already exists.

- [ ] **Step 5: Run tests and verify GREEN**

Run: \`python -m unittest tests.test_migration_contract -v\`

Expected: Task 1 tests PASS.

- [ ] **Step 6: Commit**

\`\`\`text
git add tests/__init__.py tests/test_migration_contract.py .ai/MIGRATE.md MIGRATION.md
git commit -m "feat: add staged framework migration entrypoint"
\`\`\`

### Task 2: Mixed-ownership routers and ID-managed local adapters

**Files:**
- Modify: \`tests/test_migration_contract.py\`
- Modify: \`.ai/framework/manifest.yaml\`
- Modify: \`.ai/templates/adapters/codex/AGENTS.md\`
- Modify: \`.ai/templates/adapters/claude/CLAUDE.md\`
- Modify: \`.ai/05-create-platform-adapters.md\`
- Modify: \`.ai/framework/skills/forge-sync-adapters/SKILL.md\`

**Interfaces:**
- Consumes: manifest \`skills\` and \`subagents\` IDs, \`.ai/project.yaml\`, neutral sources, existing adapters, router overlays.
- Produces: structured shared/platform overlay inputs and ID-scoped adapter synchronization that permits unlisted project outputs.

- [ ] **Step 1: Add failing ownership tests**

Assert both router templates contain \`{{ custom.router_shared }}\` and their platform placeholder. Assert the combined manifest/generation/sync contract names all four local adapter roots, includes \`preserve\` and \`unlisted\`, and does not include \`exactly seven\` or \`exactly fourteen\`.

- [ ] **Step 2: Run focused tests and verify RED**

Run: \`python -m unittest tests.test_migration_contract.MigrationContractTests.test_router_templates_consume_durable_overlays tests.test_migration_contract.MigrationContractTests.test_adapter_contract_is_id_scoped_and_local -v\`

Expected: FAIL on missing structured placeholders and exact-count language.

- [ ] **Step 3: Refine manifest ownership**

State that managed membership is derived only from manifest \`subagents\` and \`skills\`; unlisted entries are project-owned and preserved; same-ID collisions require approval; platform config/settings/commands/hooks are not Forge outputs.

- [ ] **Step 4: Add structured overlay slots**

Render \`{{ custom.router_shared }}\` plus \`{{ custom.codex_router }}\` or \`{{ custom.claude_router }}\` at the end of each framework router.

- [ ] **Step 5: Rewrite generation and sync contracts**

Require local-only paths, staged rendering, per-ID replacement of recognized Forge outputs, preservation of unlisted entries/configuration, collision approval, parity of the manifest-declared Forge set, and rollback. Remove exact total directory counts.

- [ ] **Step 6: Run tests and verify GREEN**

Run: \`python -m unittest tests.test_migration_contract -v\`

Expected: all tests PASS.

- [ ] **Step 7: Commit**

\`\`\`text
git add tests/test_migration_contract.py .ai/framework/manifest.yaml .ai/templates/adapters/codex/AGENTS.md .ai/templates/adapters/claude/CLAUDE.md .ai/05-create-platform-adapters.md .ai/framework/skills/forge-sync-adapters/SKILL.md
git commit -m "feat: preserve project adapter extensions"
\`\`\`

### Task 3: Legacy migration behavior and conformance

**Files:**
- Modify: \`tests/test_migration_contract.py\`
- Modify: \`.ai/framework/skills/forge-migrate-framework/SKILL.md\`
- Modify: \`.ai/framework/skills/forge-check-framework/SKILL.md\`
- Modify: \`.ai/06-final-validation.md\`
- Modify: \`.ai/BOOTSTRAP.md\`

**Interfaces:**
- Consumes: \`.ai-next/MIGRATE.md\`, current/staged manifests, optional legacy lock, protected hashes, adapter ownership policy.
- Produces: legacy-safe execution and conformance rules that validate required Forge IDs while allowing project-owned extras.

- [ ] **Step 1: Add failing legacy tests**

Assert migration uses \`.ai-next/\`, explicitly supports missing lock, never modifies canonical state, and no longer applies approved canonical changes. Assert check/final validation require the \`manifest-declared\` set, allow \`additional project-owned\` adapters, and contain no exact-path total assertions.

- [ ] **Step 2: Run focused tests and verify RED**

Run: \`python -m unittest tests.test_migration_contract.MigrationContractTests.test_legacy_migration_uses_ai_next_and_never_edits_canonical_schema tests.test_migration_contract.MigrationContractTests.test_conformance_allows_project_owned_adapter_extensions -v\`

Expected: FAIL on current copied-bundle assumptions and exact totals.

- [ ] **Step 3: Rewrite \`forge-migrate-framework\`**

Consume \`.ai-next/\`, support missing lock, preserve old \`.ai/\` until approval, freeze canonical/execution paths, extract overlays, replace recognized legacy Forge IDs, preserve unlisted adapters, build candidates, validate hashes, and roll back every affected path.

- [ ] **Step 4: Update conformance and final validation**

Validate the manifest-declared Forge set and hashes while accepting additional project-owned agents and skills. Validate overlay rendering and unclaimed adjacent platform configuration.

- [ ] **Step 5: Separate bootstrap routing**

Keep \`.ai/BOOTSTRAP.md\` exclusively for new/first-adoption initialization and route already-initialized Forge repositories to \`.ai-next/MIGRATE.md\`.

- [ ] **Step 6: Run tests and verify GREEN**

Run: \`python -m unittest tests.test_migration_contract -v\`

Expected: all tests PASS.

- [ ] **Step 7: Commit**

\`\`\`text
git add tests/test_migration_contract.py .ai/framework/skills/forge-migrate-framework/SKILL.md .ai/framework/skills/forge-check-framework/SKILL.md .ai/06-final-validation.md .ai/BOOTSTRAP.md
git commit -m "feat: enforce rollback-safe legacy migration"
\`\`\`

### Task 4: Consolidate migration documentation

**Files:**
- Modify: \`tests/test_migration_contract.py\`
- Modify: \`README.md\`
- Modify: \`RUNBOOK.md\`
- Modify: \`FRAMEWORK.md\`
- Modify: \`FRAMEWORK_DESIGN.md\`
- Modify: \`.ai/CONVENTIONS.md\`

**Interfaces:**
- Consumes: root \`MIGRATION.md\` as the sole user-facing migration guide.
- Produces: general documentation without duplicate Forge-migration procedure while retaining internal executable contracts.

- [ ] **Step 1: Add failing consolidation test**

For \`README.md\`, \`RUNBOOK.md\`, \`FRAMEWORK.md\`, and \`FRAMEWORK_DESIGN.md\`, assert absence of \`forge-migrate-framework\`, \`framework migration\`, \`## 15. Миграция\`, and \`## Синхронизация и миграция\`.

- [ ] **Step 2: Run test and verify RED**

Run: \`python -m unittest tests.test_migration_contract.MigrationContractTests.test_general_docs_do_not_duplicate_framework_migration_guidance -v\`

Expected: FAIL on current duplicated prose.

- [ ] **Step 3: Remove duplicate user-facing prose**

Remove the README sentence combining installation and migration, RUNBOOK migration section, FRAMEWORK migration bullets/section, and FRAMEWORK_DESIGN migration requirement/section. Renumber following RUNBOOK sections. Preserve product/data migration examples in scenarios and architecture templates.

- [ ] **Step 4: Keep internal routing concise**

Retain the migration skill in manifests, generated router maintenance lists, and executable internal contracts. Remove explanatory migration prose from conventions and state collision behavior generically through synchronization.

- [ ] **Step 5: Run tests and hygiene checks**

Run: \`python -m unittest tests.test_migration_contract -v\`

Run: \`git -c safe.directory=D:/Jupyter_notebooks/ai_dev_forge diff --check\`

Expected: all tests PASS and no whitespace errors.

- [ ] **Step 6: Commit**

\`\`\`text
git add tests/test_migration_contract.py README.md RUNBOOK.md FRAMEWORK.md FRAMEWORK_DESIGN.md .ai/CONVENTIONS.md
git commit -m "docs: consolidate framework migration guidance"
\`\`\`

### Task 5: Final verification

**Files:**
- Verify: all files changed by Tasks 1-4

**Interfaces:**
- Consumes: completed implementation and contract suite.
- Produces: completion evidence without modifying derived artifacts or \`main\`.

- [ ] **Step 1: Run full contract suite**

Run: \`python -m unittest tests.test_migration_contract -v\`

Expected: all tests PASS.

- [ ] **Step 2: Search migration references**

Search source files excluding \`.git/\`, \`.worktrees/\`, \`build/\`, \`dist/\`, and \`docs/superpowers/\`. Expected user-facing Forge migration guidance only in \`.ai/MIGRATE.md\` and \`MIGRATION.md\`; internal references remain only where executable routing or enforcement requires them.

- [ ] **Step 3: Inspect Git state**

Run: \`git -c safe.directory=D:/Jupyter_notebooks/ai_dev_forge status --short\`

Run: \`git -c safe.directory=D:/Jupyter_notebooks/ai_dev_forge log -5 --oneline\`

Expected: focused implementation commits and a clean worktree.

- [ ] **Step 4: Review GitHub staging commands**

Confirm explicit \`main\`, exact repository URL, unique temporary directory, failure on existing \`.ai-next/\`, copy of only \`.ai/\`, and cleanup limited to the validated temporary path.

- [ ] **Step 5: Report completion**

Report entrypoints, protected ownership behavior, router/adapter merge behavior, GitHub staging, tests, and limitations. Do not push or modify \`main\` without separate authorization.

