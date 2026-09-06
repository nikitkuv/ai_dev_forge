"""Behavior tests using isolated consumer projects; no external model calls."""
import contextlib
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".ai/tools"))
import forge
import forge_adapters as adapters
import forge_core as core
import forge_runtime as runtime


class Repository(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="forge-python-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def consumer(self, opencode=True):
        shutil.copytree(ROOT / ".ai", self.root / ".ai", ignore=shutil.ignore_patterns("local", "__pycache__"))
        config = core.load_yaml(self.root, ".ai/templates/project.yaml")
        config["role_execution"]["mode"] = "native_subagents"
        config["platforms"]["opencode"]["enabled"] = opencode
        for tier in ("strong", "balanced", "fast"):
            config["models"]["opencode"][tier]["model"] = "example/" + tier
        self.write(".ai/project.yaml", core.canonical(config))
        return config


class CoreTests(Repository):
    def test_shared_router_has_explicit_context_budget(self):
        # A byte budget catches long-line prompt growth that a 150-line limit misses.
        router = (ROOT / ".ai/templates/adapters/codex/AGENTS.md").read_bytes()
        self.assertLessEqual(len(router), 9500)

    def test_duplicate_yaml_and_unsafe_tags_fail(self):
        for source in ("id: one\nid: two", "a: !!python/object/apply:os.system ['exit']"):
            with self.assertRaises(core.ForgeError):
                core.yaml_value(source)

    def test_fingerprint_order_unicode_deletion_addition_and_renaming(self):
        self.write("файл.txt", "α\n")
        first = core.snapshot(self.root, ["файл.txt", "missing.txt"])
        self.assertEqual(first, core.snapshot(self.root, ["missing.txt", "файл.txt", "файл.txt"]))
        self.write("missing.txt", "")
        self.assertNotEqual(first["fingerprint"], core.snapshot(self.root, ["файл.txt", "missing.txt"])["fingerprint"])
        (self.root / "файл.txt").rename(self.root / "new.txt")
        self.assertNotEqual(first["fingerprint"], core.snapshot(self.root, ["new.txt", "missing.txt"])["fingerprint"])

    def test_fingerprint_refuses_directory_escape_and_empty_scope(self):
        for paths in ([], ["."], ["../outside"]):
            with self.assertRaises(core.ForgeError):
                core.snapshot(self.root, paths)

    def test_symlink_never_follows_outside_scope(self):
        try:
            (self.root / "linked").symlink_to(ROOT / "README.md")
        except OSError:
            self.skipTest("OS does not permit creating symlinks")
        with self.assertRaises(core.ForgeError):
            core.snapshot(self.root, ["linked"])

    def test_sections_ignore_fences_preserve_nested_and_duplicate_headings(self):
        self.write("task.md", "# Task\n## Scope\nfirst\n```md\n## Fake\n```\n### Detail\nx\n## Other\ny\n## Scope\nsecond\n")
        headings = core.section(self.root, "task.md")["sections"]
        self.assertNotIn("Fake", [h["heading"] for h in headings])
        result = core.section(self.root, "task.md", "Scope")
        self.assertEqual(result["matches"], 2)
        self.assertIn("### Detail", result["content"])
        self.assertNotIn("## Other", result["content"])
        page = core.section(self.root, "task.md", "Scope", limit=10)
        self.assertFalse(page["complete"])
        self.assertEqual(page["next_offset"], 10)
        with self.assertRaises(core.ForgeError):
            core.section(self.root, "task.md", "missing")

    def test_metadata_inventory_does_not_return_task_bodies(self):
        self.write("execution/planned/EPIC-001/tasks/TASK-001.md", "---\nid: TASK-001\nstatus: TODO\n---\n" + "large implementation plan\n" * 500)
        self.write("execution/completed/EPIC-002/tasks/TASK-002.md", "---\nid: TASK-002\nstatus: DONE\n---\n")
        records, errors = core.inventory(self.root)
        self.assertEqual(len(records), 1)
        self.assertFalse(errors)
        self.assertNotIn("large implementation", core.canonical(records))
        self.assertEqual(len(core.inventory(self.root, True)[0]), 2)

    def test_malformed_record_is_visible_not_silently_skipped(self):
        self.write("investigations/INV-0001.md", "no frontmatter")
        self.assertIn("Missing YAML", core.inventory(self.root)[1][0])

    def test_context_pages_detect_inventory_changes(self):
        for n in range(3):
            self.write(f"investigations/INV-{n:04d}.md", f"---\nid: INV-{n:04d}\noutcome: unresolved\n---\n")
        first = core.context(self.root, limit=1)
        second = core.context(self.root, offset=1, limit=1)
        self.assertEqual(first["inventory_fingerprint"], second["inventory_fingerprint"])
        self.assertEqual(first["next_offset"], 1)
        self.write("investigations/INV-0000.md", "---\nid: INV-0000\noutcome: no_action\n---\n")
        self.assertNotEqual(first["inventory_fingerprint"], core.context(self.root)["inventory_fingerprint"])

    def test_git_status_preserves_unicode_and_spaces(self):
        subprocess.run(["git", "init", "--quiet"], cwd=self.root, check=True, capture_output=True)
        self.write("unicode имя with spaces.txt", "data")
        status = core.git_status(self.root)
        self.assertTrue(status["available"])
        self.assertEqual(status["changes"], [{"status": "??", "path": "unicode имя with spaces.txt"}])

    def test_source_validation_and_actual_task_states(self):
        self.consumer(False)
        self.assertTrue(core.validate(self.root)["passed"])
        self.write("BACKLOG.md", "## Epic Roadmap\n| ID | Priority | Readiness | Status | Dependencies | Blocked by |\n| --- | --- | --- | --- | --- | --- |\n| EPIC-001 | P0 | READY | PLANNED | — | — |\n")
        self.write("execution/planned/EPIC-001-example/plan.md", "---\ndocument_type: epic_plan\nepic_id: EPIC-001\ndocument_status: approved\n---\n")
        task_path = "execution/planned/EPIC-001-example/tasks/TASK-001.md"
        task = "---\ndocument_type: task\nid: TASK-001\nepic_id: EPIC-001\ndefinition_status: approved\nstatus: TODO\n---\n"
        self.write(task_path, task)
        self.assertTrue(core.validate(self.root, True)["passed"])
        self.write(task_path, task.replace("TODO", "IN PROGRESS"))
        self.assertFalse(core.validate(self.root, True)["passed"])

    def test_cli_json_failure_and_invalid_pagination(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = forge.main(["--root", str(ROOT), "validate"])
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(output.getvalue())["passed"])
        with self.assertRaises(core.ForgeError):
            forge.main(["--root", str(self.root), "context", "--limit", "0"])


class AdapterTests(Repository):
    def test_all_platforms_roundtrip_quotes_permissions_and_idempotence(self):
        self.consumer()
        source = self.root / ".ai/framework/agents/reviewer.yaml"
        agent = core.load_yaml(self.root, source)
        agent["description"] = 'A "quote" and \\ slash: тест'
        agent["instructions"] += '\nLiteral """ and \\ backslash.'
        source.write_text(core.canonical(agent), encoding="utf-8")
        self.write(".codex/config.toml", "user setting")
        self.write(".opencode/agents/custom.md", "user agent")
        preview = adapters.preview(self.root)[0]
        self.assertFalse(preview["collisions"])
        adapters.apply(self.root, preview["preview_token"])
        import tomllib
        emitted = tomllib.loads(core.text(self.root, ".codex/agents/reviewer.toml"))
        self.assertEqual(emitted["description"], agent["description"])
        self.assertEqual(emitted["developer_instructions"], agent["instructions"])
        self.assertEqual(core.frontmatter(core.text(self.root, ".claude/agents/reviewer.md"))["effort"], "high")
        self.assertEqual(core.frontmatter(core.text(self.root, ".claude/agents/reviewer.md"))["tools"], ", ".join(agent["claude_tools"]))
        for identity in core.load_yaml(self.root, ".ai/framework/manifest.yaml")["subagents"]:
            permissions = core.frontmatter(core.text(self.root, f".opencode/agents/{identity}.md"))["permission"]
            self.assertEqual(permissions["edit"], "allow" if identity == "implementer" else "deny")
            self.assertEqual(permissions["task"], "deny")
        self.assertEqual(core.text(self.root, ".codex/config.toml"), "user setting")
        self.assertEqual(core.text(self.root, ".opencode/agents/custom.md"), "user agent")
        self.assertEqual(adapters.preview(self.root)[0]["changes"], [])
        self.assertEqual(adapters.apply(self.root, adapters.preview(self.root)[0]["preview_token"])["applied"], [])

    def test_collision_and_stale_preview_never_overwrite(self):
        self.consumer(False)
        self.write("AGENTS.md", "manual content")
        preview = adapters.preview(self.root)[0]
        with self.assertRaisesRegex(core.ForgeError, "Unapproved"):
            adapters.apply(self.root, preview["preview_token"])
        self.assertEqual(core.text(self.root, "AGENTS.md"), "manual content")
        self.write("AGENTS.md", "new content")
        with self.assertRaisesRegex(core.ForgeError, "Stale"):
            adapters.apply(self.root, preview["preview_token"], ["AGENTS.md"])

    def test_source_change_invalidates_preview(self):
        self.consumer(False)
        preview = adapters.preview(self.root)[0]
        self.write(".ai/custom/router-shared.md", "New project rule")
        with self.assertRaisesRegex(core.ForgeError, "Stale"):
            adapters.apply(self.root, preview["preview_token"])

    def test_write_failure_rolls_back_and_recovery_clears_journal(self):
        self.consumer(False)
        before = adapters.preview(self.root)[0]
        original = adapters._replace
        count = 0
        def fail_second(path, data):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("injected disk failure")
            original(path, data)
        with patch.object(adapters, "_replace", side_effect=fail_second):
            with self.assertRaisesRegex(OSError, "injected"):
                adapters.apply(self.root, before["preview_token"])
        self.assertFalse((self.root / "AGENTS.md").exists())
        self.assertFalse((self.root / ".ai/framework.lock").exists())
        self.assertTrue((self.root / ".ai/local/adapter-transaction/journal.json").exists())
        adapters.recover(self.root)
        self.assertFalse((self.root / ".ai/local/adapter-transaction").exists())

    def test_invalid_enabled_model_blocks_all_output(self):
        config = self.consumer()
        config["models"]["opencode"]["fast"]["model"] = None
        self.write(".ai/project.yaml", core.canonical(config))
        with self.assertRaises(core.ForgeError):
            adapters.preview(self.root)
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_skill_resources_and_unrelated_lock_fields_survive(self):
        self.consumer(False)
        self.write(".ai/framework/skills/forge-run-task/references/example.md", "detail")
        self.write(".ai/framework.lock", '{"project_field": "preserve"}')
        preview = adapters.preview(self.root)[0]
        adapters.apply(self.root, preview["preview_token"])
        self.assertEqual(core.text(self.root, ".agents/skills/forge-run-task/references/example.md"), "detail")
        self.assertEqual(core.load_yaml(self.root, ".ai/framework.lock")["project_field"], "preserve")


class RuntimeTests(Repository):
    def test_windows_npm_wrapper_uses_entrypoint_and_preserves_prompt(self):
        if not shutil.which("node"):
            self.skipTest("Node compatibility runtime unavailable")
        wrapper = self.write("runtime with spaces/claude.cmd", "@echo off\nexit /b 99\n")
        wrapper.chmod(0o755)
        self.write("runtime with spaces/node_modules/@anthropic-ai/claude-code/cli.js", """
const fs = require('node:fs');
const args = process.argv.slice(2);
if (args[0] === '--version') console.log('2.1.203');
else if (args[0] === 'auth') console.log(JSON.stringify({loggedIn: true}));
else console.log(JSON.stringify({result: fs.readFileSync(0, 'utf8'), args}));
""")
        prompt = 'Quoted " & $(literal)\n日本語\n' + 'x' * 100000
        with patch.dict(os.environ, {"FORGE_CLAUDE_EXECUTABLE": str(wrapper)}):
            result = runtime.role(self.root, "claude", "reviewer", prompt, "opus", "medium")
        self.assertTrue(result["valid_output"])
        self.assertEqual(json.loads(result["stdout"])["result"], prompt)
        self.assertIn("plan", json.loads(result["stdout"])["args"])

    def packet(self, body="print('ok')"):
        self.write("check.py", body)
        return {"schema_version": 1, "stage": "task", "inputs": ["check.py"], "inputs_complete": True,
                "cacheable": True, "checks": [{"id": "test", "argv": [sys.executable, "check.py"], "timeout_seconds": 5}]}

    def test_checks_require_explicit_execute(self):
        with self.assertRaises(core.ForgeError):
            runtime.checks(self.root, self.packet())

    def test_success_cache_and_input_invalidation(self):
        packet = self.packet()
        self.assertTrue(runtime.checks(self.root, packet, True)["passed"])
        self.assertTrue(runtime.checks(self.root, packet, True, True)["reused"])
        self.write("check.py", "raise SystemExit(7)")
        result = runtime.checks(self.root, packet, True, True)
        self.assertFalse(result["passed"])
        self.assertFalse(result["reused"])
        self.assertEqual(result["results"][0]["exit_code"], 7)

    def test_epic_and_incomplete_inputs_never_reuse(self):
        packet = self.packet()
        for field, value in (("stage", "epic"), ("inputs_complete", False)):
            candidate = dict(packet, **{field: value})
            runtime.checks(self.root, candidate, True)
            self.assertFalse(runtime.checks(self.root, candidate, True, True)["reused"])

    def test_tampered_log_forces_execution(self):
        packet = self.packet()
        result = runtime.checks(self.root, packet, True)
        self.write(result["results"][0]["log"], "tampered")
        self.assertFalse(runtime.checks(self.root, packet, True, True)["reused"])

    def test_environment_change_invalidates_cache(self):
        packet = self.packet()
        runtime.checks(self.root, packet, True)
        with patch.dict(os.environ, {"FORGE_TEST_ENV": "changed"}):
            self.assertFalse(runtime.checks(self.root, packet, True, True)["reused"])

    def test_input_mutation_fails_successful_command(self):
        packet = self.packet("from pathlib import Path\nPath('check.py').write_text('changed')")
        result = runtime.checks(self.root, packet, True)
        self.assertFalse(result["passed"])
        self.assertTrue(result["inputs_changed"])

    def test_timeout_output_limit_and_shell_metacharacters(self):
        result = runtime.run([sys.executable, "-c", "import time; time.sleep(10)"], self.root, timeout=.1)
        self.assertEqual(result["exit_code"], 124)
        result = runtime.run([sys.executable, "-c", "print('x'*10000)"], self.root, max_bytes=100)
        self.assertEqual(result["exit_code"], 125)
        literal = "quoted & $(echo unsafe) \" 日本語\nline"
        result = runtime.run([sys.executable, "-c", "import sys; print(sys.argv[1])", literal], self.root)
        self.assertEqual(result["stdout"].strip(), literal)

    def test_zero_negative_nan_timeouts_rejected(self):
        for timeout in (0, -1, float("nan"), float("inf"), True):
            with self.assertRaises(core.ForgeError):
                runtime.run([sys.executable, "--version"], self.root, timeout)

    def test_warning_output_is_visible_on_success(self):
        packet = self.packet("import sys; print('warning: investigate', file=sys.stderr)")
        result = runtime.checks(self.root, packet, True)
        self.assertIn("warning", result["results"][0]["warning_tail"])

    def test_missing_metrics_are_not_zero_cost_claims(self):
        runtime.metrics_record(self.root, {"track": "fast", "stage": "implementation"})
        group = runtime.metrics(self.root)["groups"]["fast:implementation"]
        self.assertEqual(group["events_missing_usage"], 1)
        with self.assertRaises(core.ForgeError):
            runtime.metrics_record(self.root, {"track": "fast", "input_tokens": -1})

    def test_role_rejects_error_json_empty_result_and_unauthenticated(self):
        for final in ('{"is_error":true,"result":"failed"}', '{}', 'not json', '{"result":""}'):
            outputs = ["2.1.203", '{"loggedIn":true}', final]
            def fake_run(*args, **kwargs):
                return {"exit_code": 0, "stdout": outputs.pop(0), "stderr": "", "failure": None}
            with patch.object(runtime, "run", side_effect=fake_run):
                result = runtime.role(self.root, "claude", "reviewer", "packet", "opus", "medium")
            self.assertEqual(result["exit_code"], 1)
        with patch.object(runtime, "run", side_effect=[{"exit_code": 0, "stdout": "2.1.203"}, {"exit_code": 0, "stdout": '{"loggedIn":false}'}]):
            with self.assertRaisesRegex(core.ForgeError, "authentication"):
                runtime.role(self.root, "claude", "reviewer", "packet", "opus", "medium")


class AuthorizationTests(Repository):
    def test_grant_only_covers_unchanged_approved_task_before_expiry(self):
        task = "execution/active/EPIC-001/tasks/TASK-001.md"
        self.write(task, "---\nid: TASK-001\nstatus: TODO\ndefinition_status: approved\n---\nDo it\n")
        policy = {"mode": "bounded_task_starts", "decision_ref": "explicit decision", "approved_by": "user",
                  "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                  "task_starts": [{"task_path": task, "definition_fingerprint": core.snapshot(self.root, [task])["fingerprint"]}]}
        self.write(".ai/project.yaml", core.canonical({"automation": {"authorization": policy}}))
        result = forge.authorization(self.root, task)
        self.assertTrue(result["authorized"])
        self.assertEqual(result["grants"], ["Task Start only"])
        self.write(task, core.text(self.root, task) + "Scope changed\n")
        self.assertFalse(forge.authorization(self.root, task)["authorized"])
        policy["expires_at"] = "2020-01-01T00:00:00Z"
        self.write(".ai/project.yaml", core.canonical({"automation": {"authorization": policy}}))
        with self.assertRaises(core.ForgeError):
            forge.authorization(self.root, task)


if __name__ == "__main__":
    unittest.main()
