import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

test("framework defines tests as independent behavioral evidence", async () => {
  const [contracts, conventions, router] = await Promise.all([
    read(".ai/framework/contracts.yaml"),
    read(".ai/CONVENTIONS.md"),
    read(".ai/templates/adapters/codex/AGENTS.md")
  ]);

  assert.match(contracts, /test_integrity:/);
  assert.match(contracts, /captured_production_output_as_oracle/);
  assert.match(contracts, /duplicated_production_algorithm_as_oracle/);
  assert.match(contracts, /unchanged_behavior_contract_requires_fixing_production_not_adapting_tests/);
  for (const source of [conventions, router]) {
    assert.match(source, /derive test expectations|derive their oracles/i);
    assert.match(source, /fix production code (?:instead of|rather than) adapting (?:the )?test/i);
    assert.match(source, /plausible wrong implementations/i);
  }
});

test("test-writing and planning agents require independent oracles and broad in-scope cases", async () => {
  const [implementer, planner, workflow] = await Promise.all([
    read(".ai/framework/agents/implementer.yaml"),
    read(".ai/framework/agents/epic-planner.yaml"),
    read(".ai/framework/skills/forge-run-task/SKILL.md")
  ]);

  for (const source of [implementer, planner, workflow]) {
    assert.match(source, /independent oracle|derive the expected/i);
    assert.match(source, /boundary/);
    assert.match(source, /invalid-input/);
    assert.match(source, /(?:failure|error)\/recovery|error and recovery/i);
    assert.match(source, /side[ -]effect/i);
    assert.match(source, /mock(?:ing)? the subject under test|never mock the subject under test/i);
  }
  assert.match(implementer, /Never change a test merely to make current production behavior pass/);
  assert.match(workflow, /A production edit does not by itself authorize a test edit/);
});

test("reviewer and tester reject implementation-fitted tests", async () => {
  const [reviewer, tester] = await Promise.all([
    read(".ai/framework/agents/reviewer.yaml"),
    read(".ai/framework/agents/tester.yaml")
  ]);

  assert.match(reviewer, /Audit test integrity as supporting evidence/);
  assert.match(reviewer, /captured production output or a duplicated production algorithm/);
  assert.match(reviewer, /tautological assertions/);
  assert.match(reviewer, /non-production observations unless they demonstrate a concrete defect/i);
  assert.match(tester, /test-integrity evidence/);
  assert.match(tester, /self-derived expectation/);
  assert.match(tester, /substitutes mocks or implementation-detail assertions for production behavior/);
});
