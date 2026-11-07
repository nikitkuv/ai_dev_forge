import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

test("critical surfaces are declared in the architecture with canonical references", async () => {
  const architecture = await read(".ai/templates/ARCHITECTURE.md");

  assert.match(architecture, /## Critical Surfaces/);
  assert.match(architecture, /Canonical source/);
  assert.match(architecture, /persists across epics/i);
  assert.match(architecture, /never (?:reduce|replaces?)[\s\S]{0,120}assurance/i);
});

test("epic planning folds intersecting surfaces into Task Review Focus", async () => {
  const [planner, task] = await Promise.all([
    read(".ai/framework/agents/epic-planner.yaml"),
    read(".ai/templates/TASK.md")
  ]);

  assert.match(planner, /Critical Surfaces/i);
  assert.match(planner, /Review Focus/);
  assert.match(planner, /no declared (?:critical )?surface/i);
  assert.match(task, /## Review Focus[\s\S]{0,400}critical surfaces/i);
});

test("acceptance presentation groups manual verification by surfaces first without narrowing assurance", async () => {
  const [runSkill, completeSkill] = await Promise.all([
    read(".ai/framework/skills/forge-run-task/SKILL.md"),
    read(".ai/framework/skills/forge-complete-task/SKILL.md")
  ]);

  for (const source of [runSkill, completeSkill]) {
    assert.match(source, /critical surfaces/i);
    assert.match(source, /Manual Verification/);
    assert.match(source, /(?:grouped|grouping)[\s\S]{0,200}(?:surface|first)/i);
    assert.match(source, /(?:without changing|never (?:reduce|narrow|waive))[\s\S]{0,160}assurance/i);
  }
});
