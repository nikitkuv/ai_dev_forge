import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

test("Epic and Task templates plan fuzzing without a separate artifact", async () => {
  const [plan, task] = await Promise.all([
    read(".ai/templates/plan.md"),
    read(".ai/templates/TASK.md")
  ]);

  assert.match(plan, /## Epic Fuzzing Plan/);
  for (const field of [
    "Applicability",
    "Risk surfaces",
    "Targets and invariants",
    "Harness readiness and Task ownership",
    "Task-level fuzz smoke",
    "Epic campaign",
    "Failure criteria",
    "Artifact handling",
    "Not-applicable rationale",
    "Alternative risk coverage"
  ]) {
    assert.match(plan, new RegExp(`\\*\\*${field}:\\*\\*`));
  }
  assert.match(task, /\*\*Fuzzing impact:\*\*/);
  assert.match(task, /\*\*Task fuzz smoke:\*\*/);
});

test("epic planner requires evidence for every fuzzing applicability assessment", async () => {
  const [planner, workflow, skill] = await Promise.all([
    read(".ai/framework/agents/epic-planner.yaml"),
    read(".ai/04-prepare-workspace.md"),
    read(".ai/framework/skills/forge-prepare-epic/SKILL.md")
  ]);

  for (const source of [planner, workflow, skill]) {
    assert.match(source, /Epic Fuzzing Plan/);
    assert.match(source, /applicable/);
    assert.match(source, /not applicable/);
    assert.match(source, /unresolved/);
    assert.match(source, /harness readiness/i);
    assert.match(source, /alternative risk coverage/i);
  }
  assert.match(planner, /Do not create a separate test-plan or fuzzing artifact/);
  assert.match(planner, /exact missing evidence or blocker/);
});

test("contracts preserve lifecycle and outcomes while making fuzzer invocation conditional", async () => {
  const contracts = await read(".ai/framework/contracts.yaml");

  assert.match(contracts, /VALIDATING: \[FUZZING, ACTIVE, PAUSED, CANCELLED\]/);
  assert.match(contracts, /FUZZING: \["AWAITING EPIC ACCEPTANCE", ACTIVE, PAUSED, CANCELLED\]/);
  assert.match(contracts, /fuzzing_outcomes: \[PASSED, "HARNESS REQUIRED", FINDINGS, "NOT APPLICABLE"\]/);
  assert.match(contracts, /mandatory_subject: fuzzing_gate/);
  assert.match(contracts, /epic_plan_approval:[\s\S]*?requires: \[[^\]]*valid_epic_fuzzing_plan_proposal/);
  assert.match(contracts, /epic_validation:[\s\S]*?requires: \[[^\]]*approved_epic_fuzzing_plan/);
  assert.match(contracts, /planning_applicability: \[applicable, "not applicable", unresolved\]/);
  assert.match(contracts, /required_when: \[planned_applicable, planned_unresolved, final_evidence_contradicts_planned_not_applicable\]/);
  for (const condition of [
    "approved_plan_not_applicable",
    "all_final_task_fuzzing_impacts_none",
    "actual_affected_surface_matches_approved_plan",
    "alternative_risk_coverage_passed",
    "current_aggregate_fingerprint_matches_epic_validation"
  ]) {
    assert.match(contracts, new RegExp(condition));
  }
  for (const outcome of ["PASSED", "NOT APPLICABLE", "HARNESS REQUIRED", "FINDINGS"]) {
    assert.match(contracts, new RegExp(outcome));
  }
});

test("Epic completion skips only current not-applicable plans and invokes fuzzer otherwise", async () => {
  const [complete, fuzzer, resume, conformance, validation] = await Promise.all([
    read(".ai/framework/skills/forge-complete-epic/SKILL.md"),
    read(".ai/framework/agents/fuzzer.yaml"),
    read(".ai/framework/skills/forge-resume-development/SKILL.md"),
    read(".ai/framework/skills/forge-check-framework/SKILL.md"),
    read(".ai/06-final-validation.md")
  ]);

  assert.match(complete, /skip the fuzzer only if every final Task fuzzing impact is `none`/i);
  assert.match(complete, /applicability is `applicable` or `unresolved`.*contradicts planned `not applicable`[\s\S]*invoke `fuzzer`/i);
  assert.match(fuzzer, /approved Epic Fuzzing Plan/);
  assert.match(fuzzer, /planned_applicable_unresolved_or_contradictory/);
  for (const source of [resume, conformance, validation]) {
    assert.match(source, /not applicable/i);
    assert.match(source, /fuzzer/i);
    assert.match(source, /fingerprint/i);
  }
});

test("Task testing executes applicable fuzz smoke and validates none rationale", async () => {
  const [tester, workflow] = await Promise.all([
    read(".ai/framework/agents/tester.yaml"),
    read(".ai/framework/skills/forge-run-task/SKILL.md")
  ]);

  for (const source of [tester, workflow]) {
    assert.match(source, /Task fuzz smoke/);
    assert.match(source, /impact.*`none`|impact is `none`/i);
    assert.match(source, /actual changed and affected surfaces|actual fuzzing impact/i);
  }
  assert.match(tester, /command, budget and result or not-applicable rationale/);
});

test("maintained guidance no longer claims unconditional fuzzer invocation", async () => {
  const paths = [
    "FRAMEWORK.md",
    "README.md",
    "RUNBOOK.md",
    "scenarios/03-development-pipeline.md",
    ".ai/templates/adapters/codex/AGENTS.md",
    ".ai/templates/adapters/claude/CLAUDE.md"
  ];
  const sources = await Promise.all(paths.map(read));
  const combined = sources.join("\n");

  assert.doesNotMatch(combined, /Затем автоматически запускается read-only fuzzer/);
  assert.doesNotMatch(combined, /После passing Epic Validation автоматически вызывается read-only fuzzer/);
  assert.doesNotMatch(combined, /Epic fuzzing after current Epic Validation passes\./);
  assert.match(combined, /not applicable/i);
  assert.match(combined, /unresolved/i);
  assert.match(combined, /without invoking the fuzzer|без вызова fuzzer|не вызывает fuzzer/i);
  assert.equal(sources[5].trim(), "@AGENTS.md");
});
