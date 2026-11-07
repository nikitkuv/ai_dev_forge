import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

test("process follow-up enums and routing live in the contracts", async () => {
  const contracts = await read(".ai/framework/contracts.yaml");

  assert.match(contracts, /process_followup_root_causes: \[task_ambiguity, missing_repo_context, missing_acceptance_criterion, weak_test_oracle, rule_drift, other\]/);
  assert.match(contracts, /process_followup_fix_targets: \[skill, template_field, contract, neutral_instruction, regression_test, no_process_change\]/);
  assert.match(contracts, /process_followup_dispositions: \[pending, applied, declined\]/);
  assert.match(contracts, /process_followup:/);
  assert.match(contracts, /unapplied_followup: conformance_advisory_only/);
  assert.match(contracts, /fix_application: separate_authorized_change/);
  assert.match(contracts, /legacy_records: valid_without_backfill/);
});

test("templates carry the process follow-up block defaulting to empty", async () => {
  const [task, plan] = await Promise.all([
    read(".ai/templates/TASK.md"),
    read(".ai/templates/plan.md")
  ]);

  for (const source of [task, plan]) {
    assert.match(source, /#+ Process Follow-up/);
    assert.match(source, /\*\*Root cause:\*\*/);
    assert.match(source, /\*\*Fix target:\*\*/);
    assert.match(source, /\*\*Disposition:\*\*/);
    assert.match(source, /\*\*Rationale:\*\*/);
    assert.match(source, /advisory/i);
    assert.match(source, /never blocks a gate/i);
  }
  assert.match(task, /## User Validation[\s\S]*## Process Follow-up[\s\S]*## Iteration History/);
  assert.match(plan, /## Epic User Validation History[\s\S]*### Process Follow-up/);
});

test("acceptance skills require a follow-up only for rejected or corrected deliveries", async () => {
  const [taskSkill, epicSkill, checkSkill] = await Promise.all([
    read(".ai/framework/skills/forge-complete-task/SKILL.md"),
    read(".ai/framework/skills/forge-complete-epic/SKILL.md"),
    read(".ai/framework/skills/forge-check-framework/SKILL.md")
  ]);

  assert.match(taskSkill, /rejected or corrected/i);
  assert.match(taskSkill, /Process Follow-up/);
  assert.match(taskSkill, /before [`']?DONE/);
  assert.match(taskSkill, /no_process_change/);
  assert.match(taskSkill, /separate authorized change/i);
  assert.match(epicSkill, /Epic User Validation History/);
  assert.match(epicSkill, /Process Follow-up/);
  assert.match(epicSkill, /before [`']?COMPLETED/);
  assert.match(checkSkill, /unapplied follow-up/i);
  assert.match(checkSkill, /advisory/i);
  assert.match(checkSkill, /never blocks? (?:a |any )?gate/i);
});
