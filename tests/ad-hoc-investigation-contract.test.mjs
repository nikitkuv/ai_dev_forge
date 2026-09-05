import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

function validFixture(record) {
  if (!/^INV-\d{4,}$/.test(record.id)) return false;
  if (!["no_action", "promoted", "fixed_directly", "unresolved"].includes(record.outcome)) return false;
  if (record.outcome === "no_action") return Boolean(record.reason && record.future_recommendation);
  if (record.outcome === "promoted") return Boolean(record.linked_work?.length && record.reciprocal_research_refs?.length);
  if (record.outcome === "unresolved") return Boolean(record.remaining_hypotheses?.length && record.next_experiments?.length);
  return Boolean(
    record.fix_authorized &&
    record.changes &&
    Array.isArray(record.changes.added) &&
    Array.isArray(record.changes.modified) &&
    Array.isArray(record.changes.removed) &&
    record.verification?.length &&
    record.final_reference
  );
}

test("manifest and contracts expose a lifecycle-independent orchestrator workflow", async () => {
  const [manifest, contracts, project] = await Promise.all([
    read(".ai/framework/manifest.yaml"),
    read(".ai/framework/contracts.yaml"),
    read(".ai/templates/project.yaml")
  ]);
  assert.match(manifest, /version: 4\.8\.0/);
  assert.match(project, /version: 4\.8\.0/);
  assert.match(manifest, /- investigations\//);
  assert.match(manifest, /- forge-investigate/);
  assert.match(contracts, /investigation_outcomes: \[no_action, promoted, fixed_directly, unresolved\]/);
  assert.match(contracts, /ad_hoc_investigations:[\s\S]*?execution_owner: orchestrator[\s\S]*?subagent_invocation: forbidden/);
  assert.match(contracts, /lifecycle_coupling: forbidden/);
  assert.match(contracts, /automatic_bug_epic_task_or_replan: forbidden/);
  assert.match(contracts, /commit_authorization_inference: forbidden/);
});

test("INV template is one flat canonical record with four outcomes and a direct-fix ledger", async () => {
  const template = await read(".ai/templates/INVESTIGATION.md");
  for (const field of ["document_type: investigation", "id: INV-NNNN", "outcome: unresolved", "baseline_revision:", "relevant_paths:", "research_refs:"]) {
    assert.match(template, new RegExp(field));
  }
  for (const heading of ["Question", "Scope", "Investigation", "Evidence", "Causes", "Conclusion", "Next Action", "Direct Fix", "Linked Work", "Outcome History"]) {
    assert.match(template, new RegExp(`## ${heading}`));
  }
  for (const heading of ["Added", "Modified", "Removed"]) assert.match(template, new RegExp(`### ${heading}`));
  assert.match(template, /no_action\/promoted\/fixed_directly\/unresolved/);
  assert.doesNotMatch(template, /IN REVIEW|IN TESTING|AWAITING USER ACCEPTANCE/);
});

test("forge-investigate stays with the main agent and supports every disposition", async () => {
  const skill = await read(".ai/framework/skills/forge-investigate/SKILL.md");
  assert.match(skill, /main orchestrator performs the work itself/i);
  assert.match(skill, /Do not invoke `context-collector`[\s\S]*any other generated subagent/i);
  assert.match(skill, /research_only[\s\S]*research_and_fix/);
  for (const outcome of ["no_action", "promoted", "fixed_directly", "unresolved"]) assert.match(skill, new RegExp(outcome));
  assert.match(skill, /does not require Task Start/i);
  assert.match(skill, /every added, modified, and removed path/i);
  assert.match(skill, /Never commit merely because the investigation is complete or fixed/i);
});

test("direct-fix and outcome fixtures enforce the minimal record contract", async () => {
  const fixtures = JSON.parse(await read("tests/fixtures/ad-hoc-investigations.json"));
  for (const fixture of fixtures) assert.equal(validFixture(fixture.record), fixture.valid, fixture.name);
});

test("planning carries reciprocal research references and reuses applicable investigation context", async () => {
  const [backlog, plan, task, prepare, planner, feature, bug] = await Promise.all([
    read(".ai/templates/BACKLOG.md"),
    read(".ai/templates/plan.md"),
    read(".ai/templates/TASK.md"),
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md"),
    read(".ai/framework/agents/epic-planner.yaml"),
    read(".ai/framework/skills/forge-intake-feature/SKILL.md"),
    read(".ai/framework/skills/forge-intake-bug/SKILL.md")
  ]);
  assert.match(backlog, /\| Research \|/);
  assert.match(plan, /research_refs: \[\]/);
  assert.match(plan, /## Research Context/);
  assert.match(task, /research_refs: \[\]/);
  for (const source of [prepare, planner]) {
    assert.match(source, /INV-NNNN/);
    assert.match(source, /baseline/i);
    assert.match(source, /recheck only|recheck/i);
    assert.match(source, /Research Context/);
  }
  for (const source of [feature, bug]) assert.match(source, /outcome: promoted[\s\S]*reciprocal/i);
});

test("resume and conformance recognize investigation evidence without making it lifecycle authority", async () => {
  const [collector, resume, check, validation] = await Promise.all([
    read(".ai/framework/agents/context-collector.yaml"),
    read(".ai/framework/skills/forge-resume-development/SKILL.md"),
    read(".ai/framework/skills/forge-check-framework/SKILL.md"),
    read(".ai/06-final-validation.md")
  ]);
  for (const source of [collector, resume]) assert.match(source, /investigat|INV-/i);
  assert.match(resume, /canonical research evidence, never as lifecycle authority/i);
  assert.match(check, /## Validate ad hoc investigations/);
  assert.match(check, /no_action.*promoted.*fixed_directly.*unresolved/);
  assert.match(validation, /Every `INV-NNNN` path matches its ID/);
});

test("bootstrap, migration and adapter generation preserve history and distribute only the skill", async () => {
  const [bootstrap, migration, migrateSkill, sync, generation, router] = await Promise.all([
    read(".ai/BOOTSTRAP.md"),
    read(".ai/MIGRATE.md"),
    read(".ai/framework/skills/forge-migrate-framework/SKILL.md"),
    read(".ai/framework/skills/forge-sync-adapters/SKILL.md"),
    read(".ai/05-create-platform-adapters.md"),
    read(".ai/templates/adapters/codex/AGENTS.md")
  ]);
  assert.match(bootstrap, /no synthetic INV records/i);
  for (const source of [migration, migrateSkill]) assert.match(source, /investigations\//);
  assert.match(sync, /Generate no `investigations\/`/);
  assert.match(generation, /seventeen portable `SKILL\.md` files/);
  assert.match(router, /Diagnostics: `forge-investigate`/);
  assert.match(router, /invokes no generated subagent/);
});

test("maintained documentation describes the same simple workflow", async () => {
  const docs = (await Promise.all(["README.md", "FRAMEWORK.md", "RUNBOOK.md", "MIGRATION.md", "scenarios/05-ad-hoc-investigation.md"].map(read))).join("\n");
  for (const term of ["forge-investigate", "INV-NNNN", "no_action", "promoted", "fixed_directly", "unresolved", "research_refs"]) assert.match(docs, new RegExp(term));
  assert.match(docs, /без вызова субагентов|не вызывает generated subagents/i);
  assert.match(docs, /added.*modified.*removed|добавленные, изменённые и удалённые/is);
});
