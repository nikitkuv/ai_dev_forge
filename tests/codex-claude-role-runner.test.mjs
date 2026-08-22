import assert from "node:assert/strict";
import test from "node:test";
import { mkdtempSync, readdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { claudeCommand, buildClaudeArgs, main, preflight, versionAtLeast } from "../.ai/templates/adapters/codex/claude-role-runner.mjs";

function fixture() {
  const root = mkdtempSync(join(tmpdir(), "forge-claude-cli-"));
  const script = join(root, "fake-claude.mjs");
  writeFileSync(script, `
    import { readFileSync } from "node:fs";
    const args = process.argv.slice(2);
    if (args[0] === "--version") { console.log(process.env.FAKE_VERSION || "2.1.203 (Claude Code)"); process.exit(0); }
    if (args[0] === "auth" && args[1] === "status") {
      if (process.env.FAKE_AUTH === "missing") { console.error("not logged in"); process.exit(1); }
      if (process.env.FAKE_AUTH === "malformed") { console.log("not-json"); process.exit(0); }
      console.log(JSON.stringify({ loggedIn: true })); process.exit(0);
    }
    const prompt = readFileSync(0, "utf8");
    if (process.env.FAKE_EXPECT_PROMPT && prompt !== process.env.FAKE_EXPECT_PROMPT) process.exit(9);
    if (process.env.FAKE_HANG === "1") setInterval(() => {}, 1000);
    else {
      if (process.env.FAKE_OUTPUT === "malformed") console.log("not-json");
      else console.log(JSON.stringify({ result: "CLEAN", promptLength: prompt.length, args }));
      process.exit(Number(process.env.FAKE_EXIT || 0));
    }
  `);
  return { root, script, env: { ...process.env, FORGE_CLAUDE_EXECUTABLE: process.execPath, FORGE_CLAUDE_SCRIPT: script } };
}

test("resolves POSIX and Windows Claude executables", () => {
  assert.equal(claudeCommand({}, "linux").command, "claude");
  assert.equal(claudeCommand({}, "win32").command, "claude.cmd");
  assert.equal(claudeCommand({ FORGE_CLAUDE_EXECUTABLE: "/opt/claude" }, "linux").command, "/opt/claude");
});

test("preflight verifies supported version and authentication", () => {
  const { env, root } = fixture();
  assert.equal(preflight(env, root).available, true);
  assert.equal(preflight({ ...env, FAKE_VERSION: "2.1.202" }, root).available, false);
  assert.match(preflight({ ...env, FAKE_AUTH: "missing" }, root).reason, /not logged in/);
  assert.match(preflight({ ...env, FAKE_AUTH: "malformed" }, root).reason, /invalid authentication JSON/);
  assert.equal(versionAtLeast("2.2.0"), true);
});

test("launcher arguments enforce a fresh non-persistent plan-mode surface", () => {
  const args = buildClaudeArgs("opus", "high");
  assert.deepEqual(args.slice(0, 3), ["-p", "--output-format", "json"]);
  assert.ok(args.includes("plan"));
  assert.ok(args.includes("--no-session-persistence"));
  assert.ok(args.includes("Read,Grep,Glob,Bash"));
  const denied = args[args.indexOf("--disallowedTools") + 1];
  for (const tool of ["Edit", "Write", "NotebookEdit", "Agent", "Task", "WebFetch", "WebSearch", "Chrome", "mcp__*"]) assert.match(denied, new RegExp(tool.replace("*", "\\*")));
  assert.doesNotMatch(args.join(" "), /bypassPermissions|acceptEdits|--resume|--continue|--fallback-model|--plugin-dir/);
});

test("planner and reviewer preserve multiline and large prompts", () => {
  const { env, root } = fixture();
  const planner = "planner \"quoted\"\n" + "x".repeat(100_000);
  const review = "Review Packet\nrevision: 4\nfingerprint: abc";
  writeFileSync(join(root, "planner.md"), planner);
  writeFileSync(join(root, "review.md"), review);
  assert.equal(main(["--role", "epic-planner", "--prompt-file", "planner.md", "--model", "opus", "--effort", "high"], { ...env, FAKE_EXPECT_PROMPT: planner }, root), 0);
  assert.equal(main(["--role", "reviewer", "--prompt-file", "review.md", "--model", "opus", "--effort", "high"], { ...env, FAKE_EXPECT_PROMPT: review }, root), 0);
});

test("preflight unavailability and started failures never fall back", () => {
  const { env, root } = fixture();
  writeFileSync(join(root, "prompt.md"), "packet");
  assert.equal(main(["--role", "reviewer", "--prompt-file", "prompt.md", "--model", "opus", "--effort", "high"], { ...env, FAKE_AUTH: "missing" }, root), 2);
  assert.equal(main(["--role", "reviewer", "--prompt-file", "prompt.md", "--model", "opus", "--effort", "high"], { ...env, FAKE_EXIT: "7" }, root), 7);
  assert.equal(main(["--role", "reviewer", "--prompt-file", "prompt.md", "--model", "opus", "--effort", "high"], { ...env, FAKE_OUTPUT: "malformed" }, root), 1);
  assert.equal(main(["--role", "reviewer", "--prompt-file", "prompt.md", "--model", "opus", "--effort", "high"], { ...env, FAKE_HANG: "1", FORGE_ROLE_TIMEOUT_MS: "50" }, root), 124);
});

test("runner creates no prompt or session artifact of its own", () => {
  const { env, root } = fixture();
  writeFileSync(join(root, "prompt.md"), "packet");
  const before = new Set(readdirSync(root));
  main(["--role", "reviewer", "--prompt-file", "prompt.md", "--model", "opus", "--effort", "high"], env, root);
  const after = new Set(readdirSync(root));
  assert.deepEqual(after, before);
});
