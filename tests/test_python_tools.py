"""Behavior tests using isolated consumer projects; no external model calls."""
import contextlib
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
import os
from pathlib import Path
import re
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
import forge_lifecycle as lifecycle
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


class TransactionTests(Repository):
    def test_rollback_on_caught_failure_keeps_journal_for_recovery(self):
        self.write("a.txt", "old-a")
        self.write("b.txt", "old-b")
        transaction = core.Transaction(self.root, "test").claim()
        updates = {"a.txt": b"new-a", "b.txt": b"new-b"}
        original = core.atomic_replace
        count = 0

        def fail_second(path, data):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("injected disk failure")
            original(path, data)

        with self.assertRaisesRegex(OSError, "injected"):
            transaction.write(updates, replace=fail_second)
        self.assertEqual(core.text(self.root, "a.txt"), "old-a")
        self.assertEqual(core.text(self.root, "b.txt"), "old-b")
        self.assertTrue((self.root / ".ai/local/test-transaction/journal.json").exists())
        transaction.finish(False)
        self.assertTrue((self.root / ".ai/local/test-transaction/journal.json").exists())
        self.assertEqual(core.Transaction(self.root, "test").restore()["restored"], ["b.txt", "a.txt"])
        self.assertFalse((self.root / ".ai/local/test-transaction").exists())

    def test_recovery_refuses_later_user_edits(self):
        self.write("a.txt", "old-a")
        transaction = core.Transaction(self.root, "test").claim()
        transaction.write({"a.txt": b"new-a"})
        # Simulate a crash leftover: journal exists, file already written, then the user edits it.
        self.write("a.txt", "user edit after crash")
        with self.assertRaisesRegex(core.ForgeError, "later edit"):
            core.Transaction(self.root, "test").restore()
        self.assertEqual(core.text(self.root, "a.txt"), "user edit after crash")
        self.write("a.txt", "new-a")
        core.Transaction(self.root, "test").restore()
        self.assertEqual(core.text(self.root, "a.txt"), "old-a")

    def test_guard_name_is_parameterized_and_claims_are_exclusive(self):
        first = core.Transaction(self.root, "adapter").claim()
        self.assertTrue((self.root / ".ai/local/adapter-transaction").exists())
        with self.assertRaisesRegex(core.ForgeError, "exists"):
            core.Transaction(self.root, "adapter").claim()
        second = core.Transaction(self.root, "lifecycle").claim()
        self.assertTrue((self.root / ".ai/local/lifecycle-transaction").exists())
        first.finish(False)
        second.finish(False)
        self.assertFalse((self.root / ".ai/local/adapter-transaction").exists())
        self.assertFalse((self.root / ".ai/local/lifecycle-transaction").exists())

    def test_write_rejects_unclaimed_transaction_and_concurrent_edits(self):
        with self.assertRaisesRegex(core.ForgeError, "Claim"):
            core.Transaction(self.root, "test").write({"a.txt": b"x"})
        transaction = core.Transaction(self.root, "test").claim()
        self.write("a.txt", "old")
        transaction.write({"a.txt": b"new"})
        self.assertEqual(core.text(self.root, "a.txt"), "new")

    def test_write_detects_concurrent_edit_during_transaction(self):
        self.write("a.txt", "old")
        transaction = core.Transaction(self.root, "test").claim()

        def concurrent_touch():
            self.write("a.txt", "user edit mid-transaction")

        with self.assertRaisesRegex(core.ForgeError, "Concurrent edit"):
            transaction.write({"a.txt": b"new"}, recheck=concurrent_touch)
        self.assertEqual(core.text(self.root, "a.txt"), "user edit mid-transaction")

    def test_unmanaged_recovery_target_is_rejected(self):
        self.write("a.txt", "old-a")
        transaction = core.Transaction(self.root, "test").claim()
        transaction.write({"a.txt": b"new-a"})
        with self.assertRaisesRegex(core.ForgeError, "Unmanaged target"):
            core.Transaction(self.root, "test").restore(allowed={"other.txt"})
        core.Transaction(self.root, "test").restore(allowed={"a.txt"})


class LifecycleTests(Repository):
    def seed_backlog(self):
        self.write("BACKLOG.md", "## Epic Roadmap\n"
                  "| ID | Epic and intended outcome | Requirements | Sources | Research | Priority | Readiness | Dependencies | Status | Blocked by |\n"
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                  "| EPIC-001 | Example | TBD | — | — | P0 | READY | — | ACTIVE | — |\n\n"
                  "## Defect Queue\n"
                  "| ID | Problem | Severity | User priority | Related requirement | Sources | Research | Status | Scheduled TASK |\n"
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                  "| BUG-001 | Broken behavior | medium | P1 | — | — | — | OPEN | — |\n")

    def write_task(self, path, identity, status, track="standard", review_fp=None, testing_fp=None,
                   fast_fp=None, review_outcome="CLEAN", impact="none", smoke="not applicable, no fuzzable boundary"):
        if review_fp is None and testing_fp is None and fast_fp is None:
            review_fp = core.snapshot(self.root, ["src/service.py"])["fingerprint"]
            testing_fp = core.snapshot(self.root, ["src/service.py", "tests/test_service.py"])["fingerprint"]
        changed = ["src/service.py", "tests/test_service.py"]
        content = (f"---\ndocument_type: task\nid: {identity}\nepic_id: EPIC-001\ndefinition_status: approved\n"
                   f"status: {status}\ndelivery_track: {track}\n---\n\n# {identity} — Example\n\n"
                   "## Workflow State\n\n```yaml\n"
                   "current_gate: testing\n"
                   "implementation_revision: 2\n"
                   "review_packet:\n"
                   "  changed_paths: [src/service.py, tests/test_service.py]\n"
                   "  production_review_paths: [src/service.py]\n"
                   "  supporting_evidence_paths: [tests/test_service.py]\n"
                   "  ambiguous_path_classification: []\n"
                   "review:\n"
                   f"  production_fingerprint: {review_fp or 'pending'}\n"
                   f"  outcome: {review_outcome}\n"
                   "testing:\n"
                   f"  implementation_fingerprint: {testing_fp or 'pending'}\n"
                   "  outcome: passed\n"
                   "fast_assurance:\n"
                   f"  implementation_fingerprint: {fast_fp or 'pending'}\n"
                   "  outcome: pending\n"
                   "```\n\n"
                   "## Verification Plan\n\n"
                   "- **Approach:** TDD\n"
                   f"- **Fuzzing impact:** {impact}\n"
                   f"- **Task fuzz smoke:** {smoke}\n\n"
                   "## Implementation Summary\n\n"
                   "- **Base revision:** BASE\n"
                   "- **Revision:** 2\n")
        self.write(path, content)
        return path

    def test_next_id_inv_does_not_fill_gaps(self):
        self.write("investigations/INV-0001.md", "---\nid: INV-0001\noutcome: unresolved\n---\n")
        self.write("investigations/INV-0003.md", "---\nid: INV-0003\noutcome: no_action\n---\n")
        result = lifecycle.next_id(self.root, "inv")
        self.assertEqual(result["next_id"], "INV-0004")
        self.assertEqual(result["current_max"], "INV-0003")

    def test_next_id_empty_locations_return_first_identifier(self):
        self.assertEqual(lifecycle.next_id(self.root, "task")["next_id"], "TASK-001")
        self.assertEqual(lifecycle.next_id(self.root, "bug")["next_id"], "BUG-001")
        self.assertEqual(lifecycle.next_id(self.root, "mut")["next_id"], "MUT-0001")

    def test_next_id_mut_honors_declared_registry_next_id(self):
        self.write("quality/mutation-testing/registry.yaml",
                   "schema_version: 1\nnext_id: MUT-0005\nruns: [MUT-0002]\n")
        self.assertEqual(lifecycle.next_id(self.root, "mut")["next_id"], "MUT-0005")
        self.write("quality/mutation-testing/registry.yaml",
                   "schema_version: 1\nnext_id: MUT-0005\nruns: [{id: MUT-0007}]\n")
        self.assertEqual(lifecycle.next_id(self.root, "mut")["next_id"], "MUT-0008")

    def test_evidence_check_supporting_only_change_keeps_review_fresh(self):
        self.seed_backlog()
        self.write("src/service.py", "def run():\n    return 1\n")
        self.write("tests/test_service.py", "def test_run():\n    assert run() == 1\n")
        task = self.write_task("execution/active/EPIC-001-example/tasks/TASK-001.md", "TASK-001", "IN TESTING")
        self.write("tests/test_service.py", "def test_run():\n    assert run() == 2\n")
        result = lifecycle.evidence_check(self.root, task)
        self.assertEqual(result["review_freshness"]["verdict"], "fresh")
        self.assertEqual(result["testing_currency"]["verdict"], "stale")
        self.assertEqual(result["current"]["whole_implementation"]["fingerprint"],
                         core.snapshot(self.root, ["src/service.py", "tests/test_service.py"])["fingerprint"])

    def test_evidence_check_production_change_makes_review_stale(self):
        self.seed_backlog()
        self.write("src/service.py", "def run():\n    return 1\n")
        self.write("tests/test_service.py", "def test_run():\n    assert run() == 1\n")
        task = self.write_task("execution/active/EPIC-001-example/tasks/TASK-001.md", "TASK-001", "IN TESTING")
        self.write("src/service.py", "def run():\n    return 3\n")
        result = lifecycle.evidence_check(self.root, task)
        self.assertEqual(result["review_freshness"]["verdict"], "stale")
        self.assertIn("reason", result["review_freshness"])

    def test_evidence_check_legacy_missing_fingerprints_stay_insufficient(self):
        self.seed_backlog()
        self.write("src/service.py", "def run():\n    return 1\n")
        self.write("tests/test_service.py", "def test_run():\n    assert run() == 1\n")
        task = self.write_task("execution/active/EPIC-001-example/tasks/TASK-001.md", "TASK-001",
                               "AWAITING USER ACCEPTANCE", review_fp="", testing_fp="")
        result = lifecycle.evidence_check(self.root, task)
        self.assertEqual(result["review_freshness"]["verdict"], "insufficient")
        self.assertEqual(result["testing_currency"]["verdict"], "insufficient")
        self.assertEqual(result["acceptance_eligibility"]["verdict"], "not_eligible")

    def test_evidence_check_standard_acceptance_eligibility(self):
        self.seed_backlog()
        self.write("src/service.py", "def run():\n    return 1\n")
        self.write("tests/test_service.py", "def test_run():\n    assert run() == 1\n")
        task = self.write_task("execution/active/EPIC-001-example/tasks/TASK-001.md", "TASK-001",
                               "AWAITING USER ACCEPTANCE")
        result = lifecycle.evidence_check(self.root, task)
        self.assertEqual(result["acceptance_eligibility"]["verdict"], "mechanically_eligible")
        self.assertIn("explicit user acceptance", result["requires_judgment"])

    def test_evidence_check_epic_gate_aggregation(self):
        self.seed_backlog()
        self.write("src/service.py", "def run():\n    return 1\n")
        self.write("tests/test_service.py", "def test_run():\n    assert run() == 1\n")
        self.write_task("execution/active/EPIC-001-example/tasks/TASK-001.md", "TASK-001", "IN TESTING",
                        impact="<pending>", smoke="<pending>")
        partial = lifecycle.evidence_check_epic(self.root, "EPIC-001")
        self.assertFalse(partial["all_done"])
        self.assertFalse(partial["fuzz_evidence_complete"])
        self.write_task("execution/active/EPIC-001-example/tasks/TASK-001.md", "TASK-001", "DONE")
        self.write_task("execution/active/EPIC-001-example/tasks/TASK-002.md", "TASK-002", "DONE")
        complete = lifecycle.evidence_check_epic(self.root, "EPIC-001")
        self.assertTrue(complete["all_done"])
        self.assertTrue(complete["fuzz_evidence_complete"])
        self.assertEqual(complete["aggregate"]["verdict"], "current")
        with self.assertRaises(core.ForgeError):
            lifecycle.evidence_check_epic(self.root, "EPIC-999")

    def test_review_packet_assembly_and_missing_inputs(self):
        subprocess.run(["git", "init", "--quiet"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=self.root, check=True, capture_output=True)
        self.write("src/service.py", "def run():\n    return 1\n")
        self.write("tests/test_service.py", "def test_run():\n    assert run() == 1\n")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "base"], cwd=self.root, check=True, capture_output=True)
        base = core.git_capture(self.root, ["rev-parse", "HEAD"])["stdout"].strip()
        self.write("src/service.py", "def run():\n    return 2\n")
        task = self.write_task("execution/active/EPIC-001-example/tasks/TASK-001.md", "TASK-001", "IN REVIEW")
        self.write(task, core.text(self.root, task).replace("BASE", base))
        result = lifecycle.review_packet(self.root, task)
        self.assertEqual(result["fingerprints"]["whole_implementation"],
                         core.snapshot(self.root, ["src/service.py", "tests/test_service.py"])["fingerprint"])
        self.assertIn("return 2", result["diffs"]["whole_implementation"]["diff"])
        self.assertEqual(result["diffs"]["production_surface"]["paths"], 1)
        content = core.text(self.root, task).replace("production_review_paths: [src/service.py]",
                                                     "production_review_paths: []")
        self.write(task, content)
        with self.assertRaisesRegex(core.ForgeError, "Missing recorded input"):
            lifecycle.review_packet(self.root, task)

    def test_checks_new_packet_is_accepted_by_executor(self):
        self.write("check.py", "print('ok')")
        output = ".ai/local/checks-focused.json"
        result = runtime.checks_new(self.root, output, "task", ["check.py"], "focused",
                                    [sys.executable, "check.py"], 10, cacheable=True, inputs_complete=True)
        self.assertEqual(result["checks"], 1)
        packet = json.loads((self.root / output).read_text(encoding="utf-8"))
        self.assertTrue(runtime.checks(self.root, packet, True)["passed"])
        runtime.checks_new(self.root, output, "task", ["check.py"], "second", [sys.executable, "check.py"], 10)
        with self.assertRaisesRegex(core.ForgeError, "already present"):
            runtime.checks_new(self.root, output, "task", ["check.py"], "focused", [sys.executable, "check.py"], 10)

    def test_role_assignment_embeds_contract_once_without_echo(self):
        self.consumer()
        self.write(".ai/local/assignment.md", "Review TASK-001 against its acceptance criteria.")
        instructions = core.load_yaml(self.root, ".ai/framework/agents/reviewer.yaml")["instructions"]
        relative = runtime.compose_role_prompt(self.root, "reviewer", ".ai/local/assignment.md")
        composed = core.text(self.root, relative)
        self.assertEqual(composed.count(instructions), 1)
        self.assertIn("# Assignment", composed)
        self.assertIn("Review TASK-001", composed)
        (self.root / relative).unlink()
        self.write(".ai/framework/agents/reviewer.yaml", "schema_version: 1\nid: reviewer\n")
        with self.assertRaisesRegex(core.ForgeError, "instructions"):
            runtime.compose_role_prompt(self.root, "reviewer", ".ai/local/assignment.md")

    def test_cli_role_assignment_removes_transient_prompt(self):
        config = self.consumer()
        config["role_execution"]["mode"] = "claude_with_codex"
        self.write(".ai/project.yaml", core.canonical(config))
        self.write(".ai/local/assignment.md", "Assignment text")
        instructions = core.load_yaml(self.root, ".ai/framework/agents/reviewer.yaml")["instructions"]
        with patch.object(runtime, "role", return_value={"valid_output": True, "exit_code": 0}) as fake:
            code = forge.main(["--root", str(self.root), "role", "--orchestrator", "claude",
                               "--role", "reviewer", "--assignment-file", ".ai/local/assignment.md"])
        self.assertEqual(code, 0)
        prompt = fake.call_args[0][3]
        self.assertEqual(prompt.count(instructions), 1)
        self.assertIn("Assignment text", prompt)
        self.assertEqual(list((self.root / ".ai/local").glob("role-prompt-*.md")), [])

    def test_cli_next_id_json(self):
        self.seed_backlog()
        self.write("investigations/INV-0002.md", "---\nid: INV-0002\noutcome: unresolved\n---\n")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = forge.main(["--root", str(self.root), "next-id", "--kind", "inv"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["next_id"], "INV-0003")


class ConformanceTests(Repository):
    def consumer_errors(self, seed_backlog=True):
        if seed_backlog and not (self.root / "BACKLOG.md").exists():
            self.write("BACKLOG.md", "## Epic Roadmap\n"
                       "| ID | Priority | Readiness | Status | Dependencies | Blocked by |\n"
                       "| --- | --- | --- | --- | --- | --- |\n")
        return core.validate(self.root, True)["errors"]

    def test_clean_project_without_consumer_artifacts_is_silent(self):
        self.consumer(False)
        self.assertEqual(self.consumer_errors(), [])

    def test_router_budget_and_claude_import(self):
        self.consumer(False)
        self.write("AGENTS.md", "\n".join(f"line {i}" for i in range(151)) + "\n")
        self.write("CLAUDE.md", "extra router copy\n")
        errors = " ".join(self.consumer_errors())
        self.assertIn("150-line router budget", errors)
        self.assertIn("exactly @AGENTS.md", errors)

    def test_generated_agent_bom_and_missing_frontmatter(self):
        self.consumer(False)
        (self.root / ".claude/agents").mkdir(parents=True, exist_ok=True)
        (self.root / ".claude/agents/bom.md").write_bytes(b"\xef\xbb\xbf---\nid: x\n---\nbody\n")
        (self.root / ".opencode/agents").mkdir(parents=True, exist_ok=True)
        (self.root / ".opencode/agents/plain.md").write_bytes(b"no frontmatter\n")
        errors = " ".join(self.consumer_errors())
        self.assertIn("UTF-8 BOM", errors)
        self.assertIn("frontmatter at byte zero", errors)

    def test_adr_index_parity_both_directions(self):
        self.consumer(False)
        self.write("decisions/ADR-001-cache.md", "---\nid: ADR-001\nstatus: ACCEPTED\n---\nUse a cache.\n")
        self.write("DECISIONS.md", "| ID | Status | Title |\n| --- | --- | --- |\n| ADR-009 | ACCEPTED | Ghost |\n")
        errors = " ".join(self.consumer_errors())
        self.assertIn("Unindexed ADR", errors)
        self.assertIn("Dangling ADR index entry: ADR-009", errors)

    def test_mutation_registry_structure(self):
        self.consumer(False)
        self.write("quality/mutation-testing/registry.yaml",
                   "schema_version: 1\nnext_id: MUT-0002\nruns: [MUT-0003]\n")
        errors = " ".join(self.consumer_errors())
        self.assertIn("next_id must exceed", errors)
        self.assertIn("Missing mutation run record: MUT-0003", errors)
        self.write("quality/mutation-testing/runs/MUT-0009.yaml", "schema_version: 1\nid: MUT-0009\n")
        errors = " ".join(self.consumer_errors())
        self.assertIn("Unregistered mutation run record: MUT-0009", errors)

    def test_plan_order_and_workflow_state_enforced(self):
        self.consumer(False)
        self.write("BACKLOG.md", "## Epic Roadmap\n| ID | Priority | Readiness | Status | Dependencies | Blocked by |\n| --- | --- | --- | --- | --- | --- |\n| EPIC-001 | P0 | READY | ACTIVE | — | — |\n")
        self.write("execution/active/EPIC-001-example/plan.md",
                   "---\ndocument_type: epic_plan\nepic_id: EPIC-001\ndocument_status: approved\n---\n"
                   "## Ordered Task Sequence\n| Order | Task |\n| --- | --- |\n| 1 | TASK-001 — First |\n")
        self.write("execution/active/EPIC-001-example/tasks/TASK-002.md",
                   "---\ndocument_type: task\nid: TASK-002\nepic_id: EPIC-001\nstatus: IN REVIEW\n---\nbody\n")
        errors = " ".join(self.consumer_errors())
        self.assertIn("Task absent from plan order: TASK-002", errors)
        self.assertIn("record the Workflow State block first", errors)

    def test_investigation_required_fields_and_sections(self):
        self.consumer(False)
        self.write("investigations/INV-0001.md", "---\ndocument_type: investigation\nid: INV-0001\noutcome: unresolved\n---\n# INV\n")
        errors = " ".join(self.consumer_errors())
        self.assertIn("missing frontmatter field subject", errors)
        self.assertIn("missing frontmatter field baseline_revision", errors)
        self.assertIn("Investigation missing section Question", errors)


class MutationTests(Repository):
    def seeded(self, plan_status="approved", backlog_rows_extra="", task_status="TODO", active=False):
        if not (self.root / ".ai").exists():
            self.consumer(False)
        epic_status = "ACTIVE" if active else "PLANNED"
        workspace = "execution/active" if active else "execution/planned"
        self.write("BACKLOG.md", "## Epic Roadmap\n"
                  "| ID | Epic and intended outcome | Requirements | Sources | Research | Priority | Readiness | Dependencies | Status | Blocked by |\n"
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                  f"| EPIC-001 | Example | TBD | — | — | P0 | READY | — | {epic_status} | — |\n"
                  f"{backlog_rows_extra}\n"
                  "## Defect Queue\n"
                  "| ID | Problem | Severity | User priority | Related requirement | Sources | Research | Status | Scheduled TASK |\n"
                  "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
                  "| BUG-001 | Broken | medium | P1 | — | — | — | OPEN | — |\n")
        self.write(f"{workspace}/EPIC-001-example/plan.md",
                   f"---\ndocument_type: epic_plan\nepic_id: EPIC-001\ndocument_status: {plan_status}\n---\n# Plan\n")
        return self.write_task_with_state(f"{workspace}/EPIC-001-example/tasks/TASK-001.md", "TASK-001", task_status)

    def write_task_with_state(self, path, identity, status):
        content = (f"---\ndocument_type: task\nid: {identity}\nepic_id: EPIC-001\ndefinition_status: approved\n"
                   f"status: {status}\ndelivery_track: standard\nstarted_at:\n---\n\n# {identity} — Example\n\n"
                   "## Workflow State\n\n```yaml\ncurrent_gate: task_start\nimplementation_revision: 0\n"
                   "review_packet:\n  changed_paths: []\n  production_review_paths: []\n"
                   "```\n\n## Verification Plan\n\n- **Approach:** TDD\n"
                   "- **Fuzzing impact:** none\n- **Task fuzz smoke:** none\n\n"
                   "## Implementation Summary\n\n- **Base revision:** BASE\n- **Revision:** 0\n\n"
                   "## Iteration History\n\n| Revision | Date | Trigger | Summary | Evidence invalidated |\n"
                   "| --- | --- | --- | --- | --- |\n| 0 | 2026-01-01 | Task definition approved | Initial | — |\n\n"
                   "## User Acceptance\n\n- **Decision:** pending\n- **Accepted by:** <User or role>\n"
                   "- **Accepted at:** pending\n- **Notes:** <Compact acceptance note>\n")
        self.write(path, content)
        return path

    def test_inv_create_scaffolds_and_rejects_duplicate_path(self):
        self.seeded()
        preview = lifecycle.inv_create(self.root, "Slow login", "auth", ["src/login.py"])
        self.assertTrue(preview["changes"][0]["new_file"])
        applied = lifecycle.inv_create(self.root, "Slow login", "auth", ["src/login.py"],
                                       apply_token=preview["preview_token"])
        self.assertEqual(applied["applied"], ["investigations/INV-0001-slow-login.md"])
        content = core.text(self.root, "investigations/INV-0001-slow-login.md")
        self.assertIn("id: INV-0001", content)
        self.assertIn('subject: "Slow login"', content)
        self.assertIn("src/login.py", content)
        self.assertIn("no Git repository; working tree only", content)
        with self.assertRaisesRegex(core.ForgeError, "already exists"):
            lifecycle.inv_create(self.root, "Slow login", "auth")

    def test_backlog_add_bug_preserves_unrelated_bytes_and_escapes_pipes(self):
        self.seeded(backlog_rows_extra="| EPIC-002 | Other | TBD | — | — | P1 | OUTLINE | — | PLANNED | — |")
        before_epic_section = core.text(self.root, "BACKLOG.md").split("## Defect Queue")[0]
        preview = lifecycle.backlog_add_bug(self.root, "Crash on | pipe", "high", "P0", research="INV-0001")
        token = preview["preview_token"]
        lifecycle.backlog_add_bug(self.root, "Crash on | pipe", "high", "P0", research="INV-0001", apply_token=token)
        after = core.text(self.root, "BACKLOG.md")
        self.assertIn("| BUG-002 | Crash on \\| pipe | high | P0 | — | — | INV-0001 | OPEN | — |", after)
        self.assertEqual(after.split("## Defect Queue")[0], before_epic_section)
        row = next(r for r in core.defect_rows(self.root) if r["ID"] == "BUG-002")
        self.assertEqual(row["Problem"], "Crash on | pipe")
        self.assertEqual(row["Status"], "OPEN")

    def test_backlog_update_row_changes_only_named_cells(self):
        self.seeded()
        before = core.text(self.root, "BACKLOG.md")
        preview = lifecycle.backlog_update_row(self.root, "BUG-001", {"Status": "SCHEDULED", "Scheduled TASK": "TASK-001"})
        lifecycle.backlog_update_row(self.root, "BUG-001", {"Status": "SCHEDULED", "Scheduled TASK": "TASK-001"},
                                     apply_token=preview["preview_token"])
        after = core.text(self.root, "BACKLOG.md")
        row = core.defect_rows(self.root)[0]
        self.assertEqual((row["Status"], row["Scheduled TASK"]), ("SCHEDULED", "TASK-001"))
        self.assertEqual(row["Problem"], "Broken")
        original_lines = before.splitlines()
        updated_lines = after.splitlines()
        changed = [i for i, (a, b) in enumerate(zip(original_lines, updated_lines)) if a != b]
        self.assertEqual(len(changed), 1)

    def test_backlog_update_row_moves_row_before_target(self):
        self.seeded(backlog_rows_extra="| EPIC-002 | Other | TBD | — | — | P1 | OUTLINE | — | PLANNED | — |\n| EPIC-003 | Third | TBD | — | — | P2 | OUTLINE | — | PLANNED | — |")
        preview = lifecycle.backlog_update_row(self.root, "EPIC-003", {}, move_before="EPIC-001")
        lifecycle.backlog_update_row(self.root, "EPIC-003", {}, move_before="EPIC-001",
                                     apply_token=preview["preview_token"])
        order = [row["ID"] for row in core.backlog_rows(self.root)]
        self.assertEqual(order, ["EPIC-003", "EPIC-001", "EPIC-002"])

    def test_transition_task_legal_and_mechanical_preconditions(self):
        task = self.seeded(active=True)
        with self.assertRaisesRegex(core.ForgeError, "Invalid target status"):
            lifecycle.transition_task(self.root, task, "FINISHED")
        with self.assertRaisesRegex(core.ForgeError, "Forbidden transition"):
            lifecycle.transition_task(self.root, task, "IN TESTING")
        preview = lifecycle.transition_task(self.root, task, "IN PROGRESS")
        lifecycle.transition_task(self.root, task, "IN PROGRESS", apply_token=preview["preview_token"])
        content = core.text(self.root, task)
        self.assertIn("status: IN PROGRESS", content)
        self.assertIn("current_gate: implementation", content)
        self.assertTrue(core.frontmatter(content)["started_at"])
        other = self.write_task_with_state("execution/active/EPIC-001-example/tasks/TASK-002.md", "TASK-002", "TODO")
        with self.assertRaisesRegex(core.ForgeError, "Single-writer"):
            lifecycle.transition_task(self.root, other, "IN PROGRESS")

    def test_transition_epic_rolls_back_row_byte_identically_on_validation_failure(self):
        extra = "| EPIC-002 | Busy | TBD | — | — | P1 | READY | — | ACTIVE | — |"
        self.seeded(backlog_rows_extra=extra)
        before = core.text(self.root, "BACKLOG.md")
        preview = lifecycle.transition_epic(self.root, "EPIC-001", "ACTIVE")
        with self.assertRaisesRegex(core.ForgeError, "validation failed"):
            lifecycle.transition_epic(self.root, "EPIC-001", "ACTIVE", apply_token=preview["preview_token"])
        self.assertEqual(core.text(self.root, "BACKLOG.md"), before)

    def test_epic_start_happy_path_and_rollback(self):
        self.seeded()
        preview = lifecycle.epic_start(self.root, "EPIC-001")
        result = lifecycle.epic_start(self.root, "EPIC-001", apply_token=preview["preview_token"])
        self.assertTrue((self.root / "execution/active/EPIC-001-example").is_dir())
        self.assertFalse((self.root / "execution/planned/EPIC-001-example").exists())
        self.assertEqual(next(r for r in core.backlog_rows(self.root) if r["ID"] == "EPIC-001")["Status"], "ACTIVE")
        self.assertEqual(result["moved"], ["execution/active/EPIC-001-example"])

        # Failure case: an orphan planned workspace fails post-move validation and rolls everything back.
        shutil.rmtree(self.root / "execution/active/EPIC-001-example")
        self.seeded()
        self.write("execution/planned/EPIC-009-orphan/plan.md",
                   "---\ndocument_type: epic_plan\nepic_id: EPIC-009\ndocument_status: approved\n---\n# Orphan\n")
        before_backlog = core.text(self.root, "BACKLOG.md")
        preview = lifecycle.epic_start(self.root, "EPIC-001")
        with self.assertRaisesRegex(core.ForgeError, "validation failed"):
            lifecycle.epic_start(self.root, "EPIC-001", apply_token=preview["preview_token"])
        self.assertTrue((self.root / "execution/planned/EPIC-001-example").is_dir())
        self.assertFalse((self.root / "execution/active/EPIC-001-example").exists())
        self.assertEqual(core.text(self.root, "BACKLOG.md"), before_backlog)

    def test_epic_start_preconditions(self):
        extra = "| EPIC-002 | Dep | TBD | — | — | P1 | READY | — | PLANNED | — |"
        task = self.seeded(backlog_rows_extra=extra)
        original = core.text(self.root, "BACKLOG.md")
        blocked = original.replace("| EPIC-001 | Example | TBD | — | — | P0 | READY | — | PLANNED | — |",
                                   "| EPIC-001 | Example | TBD | — | — | P0 | READY | — | PLANNED | EPIC-002 |")
        self.write("BACKLOG.md", blocked)
        with self.assertRaisesRegex(core.ForgeError, "blocked"):
            lifecycle.epic_start(self.root, "EPIC-001")
        with_dependency = original.replace("| EPIC-001 | Example | TBD | — | — | P0 | READY | — | PLANNED | — |",
                                           "| EPIC-001 | Example | TBD | — | — | P0 | READY | EPIC-002 | PLANNED | — |")
        self.write("BACKLOG.md", with_dependency)
        with self.assertRaisesRegex(core.ForgeError, "Dependency not satisfied"):
            lifecycle.epic_start(self.root, "EPIC-001")

    def test_epic_complete_moves_to_completed(self):
        self.seeded()
        start = lifecycle.epic_start(self.root, "EPIC-001")
        lifecycle.epic_start(self.root, "EPIC-001", apply_token=start["preview_token"])
        self.write("BACKLOG.md", core.text(self.root, "BACKLOG.md").replace(
            "| EPIC-001 | Example | TBD | — | — | P0 | READY | — | ACTIVE | — |",
            "| EPIC-001 | Example | TBD | — | — | P0 | READY | — | AWAITING EPIC ACCEPTANCE | — |"))
        preview = lifecycle.epic_complete(self.root, "EPIC-001")
        lifecycle.epic_complete(self.root, "EPIC-001", apply_token=preview["preview_token"])
        self.assertTrue((self.root / "execution/completed/EPIC-001-example").is_dir())
        self.assertEqual(next(r for r in core.backlog_rows(self.root) if r["ID"] == "EPIC-001")["Status"], "COMPLETED")

    def test_accept_record_appends_history_and_resolves_scheduled_bug(self):
        task = self.seeded(active=True)
        lifecycle.transition_task(self.root, task, "IN PROGRESS",
                                  apply_token=lifecycle.transition_task(self.root, task, "IN PROGRESS")["preview_token"])
        lifecycle.transition_task(self.root, task, "AWAITING USER ACCEPTANCE",
                                  apply_token=lifecycle.transition_task(self.root, task, "AWAITING USER ACCEPTANCE")["preview_token"])
        with self.assertRaisesRegex(core.ForgeError, "accepting user"):
            lifecycle.accept_record(self.root, task, "", "decision")
        self.write("BACKLOG.md", core.text(self.root, "BACKLOG.md").replace(
            "| BUG-001 | Broken | medium | P1 | — | — | — | OPEN | — |",
            "| BUG-001 | Broken | medium | P1 | — | — | — | SCHEDULED | TASK-001 |\n| BUG-002 | Other | low | P2 | — | — | — | OPEN | — |"))
        preview = lifecycle.accept_record(self.root, task, "user", "chat decision 2026-09-09", notes="looks good",
                                          resolve_bug="BUG-001")
        lifecycle.accept_record(self.root, task, "user", "chat decision 2026-09-09", notes="looks good",
                                resolve_bug="BUG-001", apply_token=preview["preview_token"])
        content = core.text(self.root, task)
        self.assertIn("status: DONE", content)
        self.assertIn("**Decision:** accepted", content)
        self.assertIn("chat decision 2026-09-09; looks good", content)
        self.assertIn("accepted by user (chat decision 2026-09-09)", content)
        bugs = {row["ID"]: row["Status"] for row in core.defect_rows(self.root)}
        self.assertEqual((bugs["BUG-001"], bugs["BUG-002"]), ("RESOLVED", "OPEN"))

    def test_accept_record_requires_awaiting_status(self):
        task = self.seeded()
        with self.assertRaisesRegex(core.ForgeError, "AWAITING USER ACCEPTANCE"):
            lifecycle.accept_record(self.root, task, "user", "decision")

    def test_commit_scoped_policy_and_exclusions(self):
        self.consumer(False)
        subprocess.run(["git", "init", "--quiet"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=self.root, check=True, capture_output=True)
        config = core.load_yaml(self.root, ".ai/templates/project.yaml")
        config["role_execution"]["mode"] = "native_subagents"
        task = self.write_task_with_state("execution/active/EPIC-001-example/tasks/TASK-001.md", "TASK-001",
                                          "AWAITING USER ACCEPTANCE")
        content = core.text(self.root, task).replace("changed_paths: []", "changed_paths: [src/a.py]")
        self.write(task, content)
        self.write("src/a.py", "print('a')\n")
        self.write("unrelated.txt", "user work\n")
        self.write(".ai/project.yaml", core.canonical(config))
        report = lifecycle.commit_scoped(self.root, task, authorized=True)
        self.assertFalse(report["committed"])
        self.assertIn("manual policy", report["reason"])
        config["git"] = {"policy": "auto_commit_after_acceptance"}
        self.write(".ai/project.yaml", core.canonical(config))
        with self.assertRaisesRegex(core.ForgeError, "DONE"):
            lifecycle.commit_scoped(self.root, task, authorized=True)
        content = _set_status(core.text(self.root, task), "DONE")
        self.write(task, content)
        report = lifecycle.commit_scoped(self.root, task, authorized=True)
        self.assertTrue(report["committed"])
        self.assertIn("src/a.py", report["scoped"])
        self.assertIn("unrelated.txt", report["excluded_unrelated"])
        committed_files = core.git_capture(self.root, ["show", "--name-only", "--pretty=format:", "HEAD"])["stdout"]
        self.assertIn("src/a.py", committed_files)
        self.assertNotIn("unrelated.txt", committed_files)
        unstaged = core.git_capture(self.root, ["status", "--porcelain"])["stdout"]
        self.assertIn("unrelated.txt", unstaged)


def _set_status(content, status):
    return re.sub(r"^status: .*$", f"status: {status}", content, count=1, flags=re.MULTILINE)


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
