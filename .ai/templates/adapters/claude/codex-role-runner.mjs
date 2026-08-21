#!/usr/bin/env node
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { basename, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const REQUIRED_NODE = [18, 18, 0];
const REQUIRED_PLUGIN = [1, 0, 6];
const REQUIRED_MODEL = "gpt-5.6-sol";
const REQUIRED_EFFORT = "high";
const REQUIRED_ROLES = new Set(["epic-planner", "reviewer"]);

function json(value) {
  process.stdout.write(`${JSON.stringify(value)}\n`);
}

function versionAtLeast(actual, minimum) {
  const parts = String(actual).replace(/^v/, "").split(".").map((part) => Number.parseInt(part, 10) || 0);
  for (let index = 0; index < minimum.length; index += 1) {
    if ((parts[index] ?? 0) > minimum[index]) return true;
    if ((parts[index] ?? 0) < minimum[index]) return false;
  }
  return true;
}

function pluginCacheRoot(env = process.env) {
  return join(env.CLAUDE_CODE_PLUGIN_CACHE_DIR || join(homedir(), ".claude", "plugins"), "cache");
}

function readPluginManifest(root) {
  const manifestPath = join(root, ".claude-plugin", "plugin.json");
  if (!existsSync(manifestPath)) return null;
  try { return JSON.parse(readFileSync(manifestPath, "utf8")); } catch { return null; }
}

export function findPluginRoots(env = process.env) {
  if (env.FORGE_CODEX_PLUGIN_ROOT) return [resolve(env.FORGE_CODEX_PLUGIN_ROOT)];
  const cache = pluginCacheRoot(env);
  if (!existsSync(cache)) return [];
  const matches = [];
  for (const marketplace of readdirSync(cache, { withFileTypes: true })) {
    if (!marketplace.isDirectory()) continue;
    const pluginRoot = join(cache, marketplace.name, "codex");
    if (!existsSync(pluginRoot)) continue;
    for (const version of readdirSync(pluginRoot, { withFileTypes: true })) {
      if (!version.isDirectory()) continue;
      const candidate = join(pluginRoot, version.name);
      const manifest = readPluginManifest(candidate);
      if (manifest?.name === "codex" && existsSync(join(candidate, "scripts", "codex-companion.mjs"))) matches.push(candidate);
    }
  }
  return matches.sort();
}

function run(command, args, options = {}) {
  return spawnSync(command, args, { encoding: "utf8", ...options });
}

export function preflight(env = process.env, cwd = process.cwd(), nodeVersion = process.version) {
  if (!versionAtLeast(nodeVersion, REQUIRED_NODE)) return { available: false, reason: `Node.js ${REQUIRED_NODE.join(".")}+ is required.` };
  const roots = findPluginRoots(env);
  if (roots.length !== 1) return { available: false, reason: roots.length ? "Multiple usable codex-plugin-cc installations were found." : "codex-plugin-cc is not installed or enabled." };
  const root = roots[0];
  const manifest = readPluginManifest(root);
  if (!versionAtLeast(manifest?.version, REQUIRED_PLUGIN)) return { available: false, reason: `codex-plugin-cc ${REQUIRED_PLUGIN.join(".")}+ is required.`, pluginRoot: root };
  const companion = join(root, "scripts", "codex-companion.mjs");
  const setup = run(process.execPath, [companion, "setup", "--json", "--cwd", cwd], { cwd, env });
  if (setup.status !== 0) return { available: false, reason: setup.stderr.trim() || "codex-plugin-cc setup failed.", pluginRoot: root };
  try {
    const report = JSON.parse(setup.stdout);
    if (!report.ready) return { available: false, reason: "Codex CLI is unavailable or not authenticated.", pluginRoot: root, setup: report };
    return { available: true, pluginRoot: root, setup: report };
  } catch {
    return { available: false, reason: "codex-plugin-cc returned invalid setup JSON.", pluginRoot: root };
  }
}

function parseArgs(argv) {
  const options = {};
  for (let index = 0; index < argv.length; index += 1) {
    const key = argv[index];
    if (!key.startsWith("--")) throw new Error(`Unexpected argument: ${key}`);
    const name = key.slice(2);
    if (name === "preflight") { options.preflight = true; continue; }
    const value = argv[index + 1];
    if (value == null) throw new Error(`Missing value for ${key}`);
    options[name] = value;
    index += 1;
  }
  return options;
}

export function main(argv = process.argv.slice(2), env = process.env, cwd = process.cwd()) {
  const options = parseArgs(argv);
  const check = preflight(env, cwd);
  if (options.preflight) { json({ provider: check.available ? "codex-plugin-cc" : "claude-subagent", ...check }); return check.available ? 0 : 2; }
  if (!REQUIRED_ROLES.has(options.role)) throw new Error("--role must be epic-planner or reviewer.");
  if (!options["prompt-file"]) throw new Error("--prompt-file is required.");
  if (!check.available) { json({ provider: "claude-subagent", fallback_agent: options.role, ...check }); return 2; }
  const promptFile = resolve(cwd, options["prompt-file"]);
  if (!existsSync(promptFile)) throw new Error(`Prompt file does not exist: ${promptFile}`);
  const result = run(process.execPath, [join(check.pluginRoot, "scripts", "codex-companion.mjs"), "task", "--fresh", "--model", REQUIRED_MODEL, "--effort", REQUIRED_EFFORT, "--prompt-file", promptFile, "--cwd", cwd], { cwd, env });
  json({ provider: "codex-plugin-cc", role: options.role, model: REQUIRED_MODEL, reasoning_effort: REQUIRED_EFFORT, fresh: true, read_only: true, started: true, exit_code: result.status ?? 1, stdout: result.stdout, stderr: result.stderr, pluginRoot: check.pluginRoot });
  return result.status ?? 1;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { process.exitCode = main(); } catch (error) { process.stderr.write(`${error.message}\n`); process.exitCode = 1; }
}
