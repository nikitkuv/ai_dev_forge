import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";


const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");

function read(path) {
  return readFileSync(resolve(ROOT, path), "utf8");
}

test("repository has one payload and both migration entrypoints", () => {
  assert.equal(existsSync(resolve(ROOT, ".ai/MIGRATE.md")), true);
  assert.equal(existsSync(resolve(ROOT, "MIGRATION.md")), true);
  assert.equal(existsSync(resolve(ROOT, ".ai-next")), false);
  assert.equal(existsSync(resolve(ROOT, ".ai-migration")), false);
});

test("migration contract freezes project state", () => {
  const text = read(".ai/MIGRATE.md");
  for (const value of [
    "SPEC.md",
    "ARCHITECTURE.md",
    "BACKLOG.md",
    "DECISIONS.md",
    "decisions/",
    "execution/",
    "project source code",
    "tests",
    "canonical schema",
  ]) {
    assert.match(text, new RegExp(value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
  assert.match(text, /read-only/);
  assert.match(text, /rollback/);
});

test("user guide stages GitHub main as .ai-next", () => {
  const text = read("MIGRATION.md");
  assert.match(text, /https:\/\/github\.com\/nikitkuv\/ai_dev_forge\.git/);
  assert.match(text, /--branch main/);
  assert.match(text, /sparse-checkout set \.ai/);
  assert.match(text, /\.ai-next/);
  assert.match(text, /Read \.ai-next\/MIGRATE\.md/);
});
