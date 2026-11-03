import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

test("TASK definitions carry a Contract Sketch beside Affected Surface and Risk", async () => {
  const [task, contracts, prepare, planner] = await Promise.all([
    read(".ai/templates/TASK.md"),
    read(".ai/framework/contracts.yaml"),
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md"),
    read(".ai/framework/agents/epic-planner.yaml")
  ]);

  assert.match(task, /## Contract Sketch/);
  const affected = task.indexOf("## Affected Surface and Risk");
  const sketch = task.indexOf("## Contract Sketch");
  const changeMap = task.indexOf("## Planned Change Map");
  assert.ok(affected >= 0 && affected < sketch && sketch < changeMap, "Contract Sketch must sit beside Affected Surface and Risk");
  assert.match(task, /required when the affected contracts include public interfaces/i);
  assert.match(task, /explicit none/i);
  assert.match(task, /before Plan Approval/);
  assert.match(task, /signatures or endpoints, schema fields, and error behavior/i);
  assert.match(task, /constrains contract shape only and never internal implementation/i);
  assert.match(task, /Replan gate before implementation adopts the new shape/i);

  assert.match(contracts, /contract_sketch:/);
  assert.match(contracts, /contract_sketch:[\s\S]*?prepared_at: task_definition_before_plan_approval/);
  assert.match(contracts, /contract_sketch:[\s\S]*?shape_change: requires_replan_before_adoption/);
  assert.match(contracts, /contract_sketch:[\s\S]*?shape_excludes: internal_implementation/);

  assert.match(prepare, /contract sketch or its explicit none/i);
  assert.match(planner, /Contract Sketch/);
});

test("sketches ride the Review Packet and review reports per-contract conformance", async () => {
  const [reviewer, workflow] = await Promise.all([
    read(".ai/framework/agents/reviewer.yaml"),
    read(".ai/framework/skills/forge-run-task/SKILL.md")
  ]);

  assert.match(workflow, /approved Contract Sketch rows for each changed public contract/);
  assert.match(reviewer, /approved Contract Sketch row for every changed public contract/i);
  assert.match(reviewer, /sketch-conformance result for every changed contract/i);
  assert.match(reviewer, /acceptance traceability step/i);
  assert.match(reviewer, /A delivered contract shape that differs from the approved sketch without a recorded Replan is a production finding/i);
  assert.match(reviewer, /constrains contract shape only/i);
});

test("Task Start binds approved sketches as boundary constraints and routes shape changes through Replan", async () => {
  const [workflow, implementer] = await Promise.all([
    read(".ai/framework/skills/forge-run-task/SKILL.md"),
    read(".ai/framework/agents/implementer.yaml")
  ]);

  assert.match(workflow, /Bind the approved Contract Sketch[\s\S]*?boundary constraint/);
  assert.match(workflow, /approved Contract Sketch as a boundary constraint on contract shape/);
  assert.match(workflow, /shape change away from the approved sketch is routed through the Replan gate/i);
  assert.match(implementer, /Treat the approved Contract Sketch as a boundary constraint/i);
  assert.match(implementer, /Replan gate before code adopts the new shape/i);
  assert.match(implementer, /never adopt a new shape silently/i);
});

test("legacy TASK fixtures without sketches keep the existing affected-contracts flow", async () => {
  const fixture = JSON.parse(await read("tests/fixtures/contract-sketch-legacy-tasks.json"));
  const [contracts, task, workflow] = await Promise.all([
    read(".ai/framework/contracts.yaml"),
    read(".ai/templates/TASK.md"),
    read(".ai/framework/skills/forge-run-task/SKILL.md")
  ]);

  assert.deepEqual(
    fixture.cases.map(({ workspace, status, expected_flow, blocked_by_sketch_requirement }) =>
      ({ workspace, status, expected_flow, blocked_by_sketch_requirement })),
    fixture.cases.map(({ workspace, status }) =>
      ({ workspace, status, expected_flow: "existing_affected_contracts_flow", blocked_by_sketch_requirement: false }))
  );
  assert.equal(fixture.cases.every(({ contract_sketch }) => contract_sketch === null), true);
  assert.match(contracts, /contract_sketch:[\s\S]*?legacy_tasks: follow_existing_affected_contracts_flow/);
  assert.match(contracts, /missing_sketch_never_blocks: \[task_start, review, testing, acceptance\]/);
  assert.match(task, /never blocked by the sketch requirement/i);
  assert.match(workflow, /never blocked by the sketch requirement/i);
});
