import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

test("contracts define exactly two delivery tracks independently from model tiers", async () => {
  const [contracts, manifest, project] = await Promise.all([
    read(".ai/framework/contracts.yaml"),
    read(".ai/framework/manifest.yaml"),
    read(".ai/templates/project.yaml")
  ]);

  assert.match(manifest, /version: 4\.9\.0/);
  assert.match(project, /version: 4\.9\.0/);
  assert.doesNotMatch(`${manifest}\n${project}`, /version: 4\.5\.0/);
  assert.match(contracts, /delivery_tracks: \[fast, standard\]/);
  assert.match(contracts, /model_tiers: \[strong, balanced, fast\]/);
  assert.match(contracts, /legacy_missing_delivery_track: standard/);
  assert.match(contracts, /fast_to_standard:[\s\S]*?allowed/);
  assert.match(contracts, /standard_to_fast_after_task_start:[\s\S]*?forbidden/);
  assert.match(contracts, /"IN PROGRESS": \["IN REVIEW", "AWAITING USER ACCEPTANCE", PAUSED, CANCELLED\]/);
  assert.match(contracts, /fast_direct_acceptance:[\s\S]*?delivery_track_fast[\s\S]*?current_fast_assurance/);
});

test("fast eligibility is positive, fail-closed, and fully disqualified by risky surfaces", async () => {
  const [contracts, task, planner] = await Promise.all([
    read(".ai/framework/contracts.yaml"),
    read(".ai/templates/TASK.md"),
    read(".ai/framework/agents/epic-planner.yaml")
  ]);

  for (const source of [contracts, task, planner]) {
    assert.match(source, /bounded/i);
    assert.match(source, /reversible/i);
    assert.match(source, /unambiguous/i);
    assert.match(source, /deterministic/i);
  }
  for (const disqualifier of [
    "public contract", "authorization", "security", "privacy", "persistence",
    "data format", "schema", "migration", "concurrency", "shared core",
    "dependency", "production build", "packaging", "deployment", "runtime infrastructure",
    "external integration", "critical user", "test weakening", "unresolved affected surface",
    "unresolved verification"
  ]) {
    assert.match(contracts, new RegExp(disqualifier.replaceAll(" ", "[_ -]"), "i"));
  }
  assert.match(planner, /risk level alone.*(?:does not|never|insufficient)/i);
  assert.match(planner, /missing.*uncertain.*`standard`/is);
});

test("TASK and planning templates persist track and separate assurance evidence", async () => {
  const [task, plan, preparation] = await Promise.all([
    read(".ai/templates/TASK.md"),
    read(".ai/templates/plan.md"),
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md")
  ]);

  assert.match(task, /delivery_track: standard/);
  assert.match(task, /## Delivery Track/);
  assert.match(task, /Fast eligibility evidence:/);
  assert.match(task, /Disqualifier disposition:/);
  assert.match(task, /## Fast Assurance Summary/);
  assert.match(task, /Assurance fingerprint:/);
  assert.match(task, /Track escalation history:/);
  assert.match(plan, /delivery track/i);
  assert.match(preparation, /criterion-by-criterion fast eligibility/i);
});

test("fast route keeps implementer and replaces reviewer and tester with orchestrator assurance", async () => {
  const [workflow, implementer, completion] = await Promise.all([
    read(".ai/framework/skills/forge-run-task/SKILL.md"),
    read(".ai/framework/agents/implementer.yaml"),
    read(".ai/framework/skills/forge-complete-task/SKILL.md")
  ]);

  assert.match(workflow, /## Fast track/);
  assert.match(workflow, /invoke `implementer`/i);
  assert.match(workflow, /do not invoke (?:the )?`?reviewer`? or (?:the )?`?tester`?/i);
  assert.match(workflow, /orchestrator assurance/i);
  assert.match(workflow, /execute or reproduce/i);
  assert.match(workflow, /IN PROGRESS.*AWAITING USER ACCEPTANCE/is);
  assert.match(implementer, /delivery track/i);
  assert.match(implementer, /RED\/GREEN/);
  assert.match(completion, /fast assurance/i);
  assert.match(completion, /standard review.*testing/is);
  assert.match(completion, /explicit Task Acceptance/i);
});

test("fast failures escalate monotonically while standard route remains intact", async () => {
  const [workflow, resume, contracts, reviewer, tester] = await Promise.all([
    read(".ai/framework/skills/forge-run-task/SKILL.md"),
    read(".ai/framework/skills/forge-resume-development/SKILL.md"),
    read(".ai/framework/contracts.yaml"),
    read(".ai/framework/agents/reviewer.yaml"),
    read(".ai/framework/agents/tester.yaml")
  ]);

  for (const source of [workflow, resume]) {
    assert.match(source, /fast.*standard/is);
    assert.match(source, /standard.*fast.*forbidden/is);
    assert.match(source, /legacy.*standard/is);
    assert.match(source, /stale.*fast assurance|fast assurance.*stale/is);
  }
  assert.match(workflow, /## Standard track/);
  assert.match(workflow, /invoke `reviewer`/i);
  assert.match(workflow, /invoke `tester`/i);
  assert.match(contracts, /standard:[\s\S]*?current_structured_review[\s\S]*?current_task_test_evidence/);
  assert.match(reviewer, /independent production-code reviewer/i);
  assert.match(tester, /You are the tester/);
});

test("legacy TASK fixtures default every in-flight state to standard without invented fast evidence", async () => {
  const fixture = JSON.parse(await read("tests/fixtures/delivery-tracks-legacy-tasks.json"));
  const migration = await read(".ai/framework/skills/forge-migrate-framework/SKILL.md");

  assert.deepEqual(
    fixture.cases.map(({ workspace, status, expected_track }) => ({ workspace, status, expected_track })),
    [
      { workspace: "planned", status: "TODO", expected_track: "standard" },
      { workspace: "active", status: "IN PROGRESS", expected_track: "standard" },
      { workspace: "active", status: "IN REVIEW", expected_track: "standard" },
      { workspace: "active", status: "IN TESTING", expected_track: "standard" },
      { workspace: "active", status: "AWAITING USER ACCEPTANCE", expected_track: "standard" }
    ]
  );
  assert.equal(fixture.cases.every(({ delivery_track }) => delivery_track === null), true);
  assert.match(migration, /Missing legacy delivery track means standard/i);
  assert.match(migration, /never synthesize fast eligibility or assurance/i);
});

test("fast assurance fails closed on drift, failure, staleness, and transition misuse", async () => {
  const [contracts, workflow, resume, completion] = await Promise.all([
    read(".ai/framework/contracts.yaml"),
    read(".ai/framework/skills/forge-run-task/SKILL.md"),
    read(".ai/framework/skills/forge-resume-development/SKILL.md"),
    read(".ai/framework/skills/forge-complete-task/SKILL.md")
  ]);

  assert.match(workflow, /unexpectedly failing.*escalate monotonically from fast to standard/is);
  assert.match(resume, /unexpected affected surface.*escalates fast to standard/is);
  assert.match(completion, /Stale, incomplete, failed, or disqualified fast evidence.*escalates to standard/is);
  assert.match(contracts, /fast_direct_acceptance:[\s\S]*?forbidden_for: \[delivery_track_standard, missing_or_stale_fast_assurance\]/);
  assert.match(contracts, /standard_to_fast_after_task_start:[\s\S]*?forbidden/);
});

test("Task delivery tracks do not weaken Epic Validation or fuzzing gates", async () => {
  const [contracts, completeEpic] = await Promise.all([
    read(".ai/framework/contracts.yaml"),
    read(".ai/framework/skills/forge-complete-epic/SKILL.md")
  ]);

  assert.match(contracts, /epic_validation_precedes_epic_fuzzing/);
  assert.match(contracts, /epic_validation:[\s\S]*?mandatory_after: last_task_acceptance/);
  assert.match(completeEpic, /track-specific.*evidence/i);
  assert.match(completeEpic, /Epic Validation/i);
  assert.match(completeEpic, /fuzzing/i);
});

test("documentation and Epic gates expose both routes without weakening aggregate assurance", async () => {
  const paths = ["README.md", "FRAMEWORK.md", "RUNBOOK.md", "scenarios/03-development-pipeline.md"];
  const sources = await Promise.all(paths.map(read));
  for (const source of sources) {
    assert.match(source, /delivery track/i);
    assert.match(source, /fast/i);
    assert.match(source, /standard/i);
  }
  const combined = sources.join("\n");
  assert.match(combined, /model tier/i);
  assert.match(combined, /risk level/i);
  assert.match(combined, /orchestrator assurance/i);
  assert.match(combined, /Epic Validation/i);
  assert.match(combined, /fuzzing/i);
});
