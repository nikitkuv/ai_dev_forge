import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

test("epic preparation is a four-stage interview with per-stage confirmation gates", async () => {
  const [skill, contracts] = await Promise.all([
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md"),
    read(".ai/framework/contracts.yaml")
  ]);

  const stages = [
    /\*\*Objective and expected outcome\*\*/,
    /\*\*Interface design\*\*/,
    /\*\*Risks and critical paths\*\*/,
    /\*\*Decomposition skeleton\*\*/
  ];
  let cursor = -1;
  for (const stage of stages) {
    const match = skill.slice(cursor + 1).search(stage);
    assert.ok(match >= 0, `missing interview stage ${stage}`);
    cursor = cursor + 1 + match;
  }

  assert.match(skill, /staged interview with confirmation gates/i);
  assert.match(skill, /presented for explicit user confirmation before the next stage begins/i);
  assert.match(skill, /rejected by the user is revised and re-confirmed before later stages proceed/i);
  assert.match(skill, /later stages remain untouched/i);
  assert.match(skill, /Never produce a later stage's artifact before the preceding stage is confirmed/i);
  assert.match(contracts, /epic_planning_interview:/);
  assert.match(contracts, /stages: \[objective_and_expected_outcome, interface_design, risks_and_critical_paths, decomposition_skeleton\]/);
  assert.match(contracts, /per_stage_confirmation: required_before_next_stage/);
});

test("interface stage enumerates intended changes and flags ADR candidates", async () => {
  const [skill, plan] = await Promise.all([
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md"),
    read(".ai/templates/plan.md")
  ]);

  for (const source of [skill, plan]) {
    assert.match(source, /Interface Delta/);
    assert.match(source, /contract/i);
    assert.match(source, /schema/i);
  }
  assert.match(skill, /data formats, and component boundaries/i);
  assert.match(skill, /intended shape/i);
  assert.match(skill, /ADR candidates with their decision drivers/i);
  assert.match(skill, /contract shapes only/i);
  assert.match(plan, /### Interface Delta/);
});

test("skeleton confirmation precedes all detail filling", async () => {
  const [skill, planner, contracts] = await Promise.all([
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md"),
    read(".ai/framework/agents/epic-planner.yaml"),
    read(".ai/framework/contracts.yaml")
  ]);

  assert.match(skill, /The skeleton carries no test cases, change maps, fuzz detail/i);
  assert.match(skill, /Detail filling begins only after the user confirms the skeleton/i);
  assert.match(skill, /confirmed skeleton plus the confirmed `Interface Delta` as its fixed input/i);
  assert.match(skill, /never produced before skeleton confirmation/i);
  assert.match(skill, /all detail filling proceeds from the revised skeleton/i);
  assert.match(planner, /confirmed skeleton/i);
  assert.match(planner, /Interface Delta/);
  assert.match(planner, /before (?:the )?skeleton (?:is )?confirm/i);
  assert.match(contracts, /detail_before_confirmation: forbidden/);
});

test("Plan Approval returns unconfirmed interface changes to the interview", async () => {
  const [skill, contracts] = await Promise.all([
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md"),
    read(".ai/framework/contracts.yaml")
  ]);

  assert.match(skill, /interface or scope change absent from the confirmed interview returns the plan to the interview stages/i);
  assert.match(skill, /design already agreed plus its details/i);
  assert.match(contracts, /plan_approval_consistency:/);
  assert.match(contracts, /unconfirmed_interface_or_scope_change: return_to_interview_stages/);
  assert.match(contracts, /consistent_plan: confirmed_design_plus_details/);
  assert.match(contracts, /epic_plan_approval:[\s\S]*?requires: \[[^\]]*interview_consistency_verified/);
});

test("stage collapse is proportional with recorded rationale and legacy plans stay valid", async () => {
  const [skill, contracts] = await Promise.all([
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md"),
    read(".ai/framework/contracts.yaml")
  ]);

  assert.match(skill, /collapsed or merged only for bounded epics/i);
  assert.match(skill, /name the merged stages and the recorded rationale/i);
  assert.match(skill, /No stage collapses silently/i);
  assert.match(skill, /missing rationale keeps all four stages/i);
  assert.match(skill, /continue their lifecycle without any re-interview/i);
  assert.match(contracts, /stage_collapse:[\s\S]*?silent_collapse: forbidden/);
  assert.match(contracts, /legacy_approved_plans: continue_without_reinterview/);
});
