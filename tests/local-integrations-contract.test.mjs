import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

test("clean Forge keeps integrations absent and optional", async () => {
  const [contracts, bootstrap, manifest, docs] = await Promise.all([
    read(".ai/framework/integrations/contracts.yaml"),
    read(".ai/BOOTSTRAP.md"),
    read(".ai/framework/manifest.yaml"),
    read("docs/local-integrations.md")
  ]);
  assert.match(contracts, /optional: true/);
  assert.match(contracts, /absent_behavior: clean_forge_baseline/);
  assert.match(contracts, /live_connector_required_for_upgrade: false/);
  assert.match(bootstrap, /clean project has no local integrations/i);
  assert.match(manifest, /- \.ai\/integrations\//);
  assert.match(docs, /clean project has no `\.ai\/integrations\/`/i);
});

test("generic profiles require explicit consumers and preserve custom profiles", async () => {
  const [contracts, template, conventions, router] = await Promise.all([
    read(".ai/framework/integrations/contracts.yaml"),
    read(".ai/templates/integration.yaml"),
    read(".ai/CONVENTIONS.md"),
    read(".ai/templates/adapters/codex/AGENTS.md")
  ]);
  for (const profile of ["work_source", "knowledge_source", "data_source", "analysis_service"]) {
    assert.match(contracts, new RegExp(`${profile}:`));
  }
  assert.match(contracts, /requires_project_owned_consumer: true/);
  assert.match(contracts, /unknown_profile_behavior: preserve_without_core_invocation/);
  assert.match(template, /consumers:/);
  assert.match(conventions, /Registration never grants implicit tool authority/i);
  assert.match(router, /Registration alone grants no tool authority/i);
});

test("work_source is read-only and provider neutral", async () => {
  const [contracts, skill, docs] = await Promise.all([
    read(".ai/framework/integrations/contracts.yaml"),
    read(".ai/framework/skills/forge-intake-external-work/SKILL.md"),
    read("docs/local-integrations.md")
  ]);
  assert.match(contracts, /required_operations: \[list_candidates, get_item\]/);
  assert.match(contracts, /allowed_access: \[read_only\]/);
  assert.doesNotMatch(contracts, /kaiten/i);
  assert.match(skill, /wrong profile.*blocker only for this intake/i);
  assert.match(skill, /Never invoke an undeclared operation or a mutation/i);
  assert.match(skill, /untrusted data/i);
  assert.match(docs, /Kaiten work-source example/);
});

test("external items have bidirectional many-to-many Forge references", async () => {
  const [backlog, taskTemplate, plan, skill, stateTemplate] = await Promise.all([
    read(".ai/templates/BACKLOG.md"),
    read(".ai/templates/TASK.md"),
    read(".ai/templates/plan.md"),
    read(".ai/framework/skills/forge-intake-external-work/SKILL.md"),
    read(".ai/templates/work-items.yaml")
  ]);
  assert.match(backlog, /\| Sources \|/);
  assert.match(taskTemplate, /external_sources: \[\]/);
  assert.match(plan, /## External Source Coverage/);
  assert.match(skill, /one-to-many and many-to-one coverage/i);
  assert.match(stateTemplate, /canonical_refs: \[\]/);
});

test("intake preserves Forge gates and handles split, combine, duplicate, and stale sources", async () => {
  const skill = await read(".ai/framework/skills/forge-intake-external-work/SKILL.md");
  for (const required of [
    /possible defect, investigation, product change, duplicate, rejected item, or unresolved candidate/i,
    /several independently deliverable Epics/i,
    /coherent Epic combined with related items/i,
    /never becomes a standalone TASK/i,
    /material change invalidates the proposal/i,
    /External priority, status, assignee, label, or wording is evidence only/i
  ]) assert.match(skill, required);
});

test("upgrade is offline, isolated, staged, and reversible", async () => {
  const [contracts, migrate, migrationSkill, sync, check] = await Promise.all([
    read(".ai/framework/integrations/contracts.yaml"),
    read(".ai/MIGRATE.md"),
    read(".ai/framework/skills/forge-migrate-framework/SKILL.md"),
    read(".ai/framework/skills/forge-sync-adapters/SKILL.md"),
    read(".ai/framework/skills/forge-check-framework/SKILL.md")
  ]);
  for (const state of ["absent", "current_supported", "older_migratable", "malformed", "unsupported_future", "custom_profile", "ownership_collision"]) {
    assert.match(contracts, new RegExp(state));
  }
  assert.match(contracts, /framework_upgrade_and_schema_migration_are_separate: true/);
  assert.match(contracts, /preserve_unknown_content_byte_for_byte: true/);
  assert.match(contracts, /local_content_is_framework_lock_input: false/);
  assert.match(migrate, /without invoking MCP, API, CLI, or other connectors/i);
  assert.match(migrationSkill, /separate project-owned change/i);
  assert.match(sync, /Do not use project-owned `\.ai\/integrations\/` definitions\/state as render input/i);
  assert.match(check, /block only consuming skills/i);
});

test("Codex and Claude routers and portable integration contract remain in parity", async () => {
  const [codex, claude, manifest, generation] = await Promise.all([
    read(".ai/templates/adapters/codex/AGENTS.md"),
    read(".ai/templates/adapters/claude/CLAUDE.md"),
    read(".ai/framework/manifest.yaml"),
    read(".ai/05-create-platform-adapters.md")
  ]);
  assert.equal(codex, claude);
  assert.match(manifest, /- forge-intake-external-work/);
  assert.match(generation, /sixteen portable `SKILL\.md` files/);
  assert.match(generation, /no `\.ai\/integrations\/` file or project-local provider\/tool name/i);
  assert.ok(codex.split(/\r?\n/).length <= 150);
});
