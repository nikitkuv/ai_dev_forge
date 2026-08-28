import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), "utf8");

test("review packets classify production and supporting surfaces by shipped effect", async () => {
  const [contracts, workflow, task] = await Promise.all([
    read(".ai/framework/contracts.yaml"),
    read(".ai/framework/skills/forge-run-task/SKILL.md"),
    read(".ai/templates/TASK.md")
  ]);

  assert.match(contracts, /production_surface:/);
  assert.match(contracts, /supporting_evidence:/);
  for (const source of [workflow, task]) {
    assert.match(source, /production_review_paths|production review paths/i);
    assert.match(source, /supporting_evidence_paths|supporting evidence paths/i);
  }
  for (const source of [contracts, workflow, task]) {
    assert.match(source, /production(?:-| )surface fingerprint|production_fingerprint/i);
    assert.match(source, /ambiguous.*rationale|rationale.*ambiguous/is);
  }
  for (const productionArtifact of ["runtime configuration", "schemas", "migrations", "packaging", "production build", "deployment"]) {
    assert.match(workflow, new RegExp(productionArtifact, "i"));
  }
  for (const supportingArtifact of ["tests", "fixtures", "snapshots", "golden files", "development tooling", "examples"]) {
    assert.match(workflow, new RegExp(supportingArtifact, "i"));
  }
});

test("only production findings block strong review", async () => {
  const [reviewer, workflow, task] = await Promise.all([
    read(".ai/framework/agents/reviewer.yaml"),
    read(".ai/framework/skills/forge-run-task/SKILL.md"),
    read(".ai/templates/TASK.md")
  ]);

  assert.match(reviewer, /production findings ordered by BLOCKER, HIGH, MEDIUM and LOW/i);
  assert.match(reviewer, /Every defect confined to tests.*must be labeled ADVISORY/is);
  assert.match(reviewer, /CLEAN is compatible with non-production observations/i);
  assert.match(workflow, /route only production findings to `implementer`/i);
  assert.match(workflow, /defect confined to tests.*non-production observation/is);
  assert.match(task, /Production findings:/);
  assert.match(task, /Non-production observations:/);
});

test("supporting-only remediation reuses clean review and reruns testing", async () => {
  const [contracts, workflow, tester, resume] = await Promise.all([
    read(".ai/framework/contracts.yaml"),
    read(".ai/framework/skills/forge-run-task/SKILL.md"),
    read(".ai/framework/agents/tester.yaml"),
    read(".ai/framework/skills/forge-resume-development/SKILL.md")
  ]);

  assert.match(contracts, /supporting_only_change:[\s\S]*?preserves: clean_production_review[\s\S]*?strong_reviewer_reinvocation: forbidden/);
  assert.match(workflow, /supporting-only continuation.*do not invoke the strong reviewer/is);
  assert.match(workflow, /rerun selected testing directly/i);
  assert.match(tester, /implementation revision may be newer than that review after supporting-only remediation/i);
  assert.match(tester, /Consume every reviewer non-production observation/i);
  assert.match(resume, /legacy evidence lacks a production fingerprint/i);
  assert.match(resume, /without another strong-review invocation/i);
});

test("production changes and packet integrity still block progression", async () => {
  const [contracts, reviewer, workflow] = await Promise.all([
    read(".ai/framework/contracts.yaml"),
    read(".ai/framework/agents/reviewer.yaml"),
    read(".ai/framework/skills/forge-run-task/SKILL.md")
  ]);

  assert.match(contracts, /production_change:[\s\S]*?task_review_evidence[\s\S]*?next_gate: strong_review/);
  assert.match(contracts, /legacy_evidence_without_production_fingerprint: fresh_review_required/);
  assert.match(contracts, /packet_or_output_integrity_failures: blocking/);
  assert.match(reviewer, /unreproducible diff, route failure, or malformed output blocks review/i);
  assert.match(workflow, /packet-integrity failure, or malformed output blocks review/i);
});
