"""Record consistency regression tests on isolated consumer repositories."""
import unittest
import contextlib
import io
import json
from unittest.mock import patch

from test_python_tools import Repository
import forge_core as core
import forge_records as records
import forge_runtime as runtime
import forge


class RecordTests(Repository):
    def setUp(self):
        super().setUp()
        self.consumer(False)
        self.write("BACKLOG.md", "## Epic Roadmap\n| ID | Priority | Readiness | Status | Dependencies | Blocked by |\n"
                   "| --- | --- | --- | --- | --- | --- |\n| EPIC-001 | P0 | READY | PLANNED | — | — |\n")
        self.plan = "execution/planned/EPIC-001-example/plan.md"
        self.task = "execution/planned/EPIC-001-example/tasks/TASK-001.md"

    def packet(self):
        return {"schema_version": 1, "allocations": {"first": "task", "second": "task"}, "files": [
            {"path": self.plan, "content": "---\ndocument_type: epic_plan\nepic_id: EPIC-001\ndocument_status: approved\n---\n"
             "## Ordered Task Sequence\n| Order | Task |\n| --- | --- |\n"
             "| 1 | `{{id:first}}` |\n| 2 | [{{id:second}}](tasks/{{id:second}}.md) |\n"},
            *[{"path": f"execution/planned/EPIC-001-example/tasks/{{{{id:{alias}}}}}.md",
               "content": "---\ndocument_type: task\nid: {{id:" + alias + "}}\nepic_id: EPIC-001\n"
               "status: TODO\ndefinition_status: approved\nblocked_by: " + deps + "\n---\n"}
              for alias, deps in (("first", "[]"), ("second", "[{{id:first}}]"))]]}

    def create(self):
        packet = self.packet()
        preview = records.records_write(self.root, packet)
        self.assertFalse((self.root / self.plan).exists())
        records.records_write(self.root, packet, preview["preview_token"])

    def test_batch_allocates_once_and_new_session_is_consistent(self):
        self.create()
        self.assertTrue(core.validate(self.root, True)["passed"])
        self.assertIn("TASK-002", records.identity_check(self.root)["declarations"])
        from forge_lifecycle import next_id
        self.assertEqual(next_id(self.root, "task")["next_id"], "TASK-003")
        self.assertEqual(core.frontmatter(core.text(self.root, self.task))["id"], "TASK-001")

    def test_stale_preview_after_another_session_writes(self):
        packet = self.packet()
        preview = records.records_write(self.root, packet)
        self.write("execution/paused/EPIC-002/tasks/TASK-001.md", "---\nid: TASK-001\n---\n")
        with self.assertRaisesRegex(core.ForgeError, "Stale"):
            records.records_write(self.root, packet, preview["preview_token"])
        self.assertFalse((self.root / self.plan).exists())

    def test_failed_validation_rolls_back_every_file(self):
        packet = self.packet()
        packet["files"][2]["content"] = packet["files"][2]["content"].replace("[{{id:first}}]", "[TASK-999]")
        preview = records.records_write(self.root, packet)
        with self.assertRaisesRegex(core.ForgeError, "missing_reference"):
            records.records_write(self.root, packet, preview["preview_token"])
        self.assertFalse((self.root / self.plan).exists())
        self.assertFalse((self.root / self.task).exists())

    def test_existing_content_requires_hash_and_cannot_change_status(self):
        self.create()
        content = core.text(self.root, self.task)
        packet = {"schema_version": 1, "files": [{"path": self.task, "content": content}]}
        with self.assertRaisesRegex(core.ForgeError, "expected_sha256"):
            records.records_write(self.root, packet)
        packet["files"][0]["expected_sha256"] = core.digest((self.root / self.task).read_bytes())
        packet["files"][0]["content"] = content.replace("status: TODO", "status: DONE")
        with self.assertRaisesRegex(core.ForgeError, "existing status"):
            records.records_write(self.root, packet)

    def test_filename_mismatch_and_numeric_alias_are_not_auto_repaired(self):
        self.create()
        self.write(self.task, core.text(self.root, self.task).replace("id: TASK-001", "id: TASK-0002"))
        codes = {f["code"] for f in records.identity_check(self.root)["findings"]}
        self.assertIn("filename_id_mismatch", codes)
        self.assertIn("numeric_id_collision", codes)
        with self.assertRaisesRegex(core.ForgeError, "conflicts"):
            records.links_repair(self.root)

    def test_unique_stale_link_repaired_without_changing_id(self):
        self.create()
        self.write("SPEC.md", "[Work](execution/active/EPIC-001-example/tasks/TASK-001.md#goal)\n")
        preview = records.links_repair(self.root)
        self.assertIn("preview_token", preview)
        records.links_repair(self.root, preview["preview_token"])
        self.assertEqual(core.text(self.root, "SPEC.md"), "[Work](" + self.task + "#goal)\n")
        self.assertTrue(records.identity_check(self.root)["passed"])

    def test_unrelated_paths_and_archive_cannot_be_written(self):
        for name in ("../outside.md", ".ai/framework/contracts.yaml", "BACKLOG-ARCHIVE.md", "execution/completed/TASK-001.md"):
            with self.subTest(name=name), self.assertRaises(core.ForgeError):
                records.records_write(self.root, {"schema_version": 1, "files": [{"path": name, "content": "x"}]})

    def test_order_accepts_code_and_links_but_rejects_duplicates(self):
        self.create()
        self.write(self.plan, core.text(self.root, self.plan) + "| 3 | TASK-001 |\n")
        self.assertTrue(any("Duplicate Task in plan order" in e for e in core.validate(self.root, True)["errors"]))

    def test_metrics_rates_have_explicit_denominators(self):
        for event in ({"first_pass": True, "waiting_seconds": 2, "review_iterations": 1, "post_acceptance_fix": False},
                      {"first_pass": False, "escalation_reason": "scope"}, {}):
            runtime.metrics_record(self.root, dict(track="standard", stage="testing", **event))
        group = runtime.metrics(self.root)["groups"]["standard:testing"]
        self.assertEqual(group["first_pass"], {"true": 1, "observations": 2, "missing": 1, "rate": .5})
        self.assertEqual(group["waiting_seconds"]["missing"], 2)
        self.assertEqual(group["escalation_reasons"], {"scope": 1})
        self.assertEqual(group["events_missing_usage"], 3)
        with self.assertRaises(core.ForgeError):
            runtime.metrics_record(self.root, {"track": "fast", "first_pass": "yes"})

    def test_workspace_move_updates_links_in_same_transaction(self):
        from forge_lifecycle import epic_start
        self.create()
        self.write("SPEC.md", "[Task](" + self.task + ")\n[Plan](" + self.plan + ")\n")
        preview = epic_start(self.root, "EPIC-001")
        epic_start(self.root, "EPIC-001", preview["preview_token"])
        self.assertIn("execution/active/", core.text(self.root, "SPEC.md"))
        self.assertNotIn("execution/planned/", core.text(self.root, "SPEC.md"))
        self.assertTrue(core.validate(self.root, True)["passed"])

    def test_move_failure_restores_links_and_workspace(self):
        import forge_lifecycle as lifecycle
        self.create()
        original = "[Task](" + self.task + ")\n"
        self.write("SPEC.md", original)
        preview = lifecycle.epic_start(self.root, "EPIC-001")
        with patch.object(lifecycle, "_validate_project", return_value=["injected"]):
            with self.assertRaisesRegex(core.ForgeError, "validation failed"):
                lifecycle.epic_start(self.root, "EPIC-001", preview["preview_token"])
        self.assertEqual(core.text(self.root, "SPEC.md"), original)
        self.assertTrue((self.root / self.task).exists())

    def test_links_ignore_fenced_examples_and_detect_wrong_label(self):
        self.create()
        self.write("SPEC.md", "```md\n[Example](execution/active/EPIC-999/plan.md)\n```\n")
        self.assertTrue(records.identity_check(self.root)["passed"])
        self.write("SPEC.md", "[TASK-999](" + self.task + ")\n")
        self.assertIn("link_id_mismatch", {f["code"] for f in records.identity_check(self.root)["findings"]})

    def test_plan_link_repair_uses_workspace_identity(self):
        self.create()
        self.write("SPEC.md", "[Plan](execution/active/EPIC-001-example/plan.md)\n")
        preview = records.links_repair(self.root)
        records.links_repair(self.root, preview["preview_token"])
        self.assertIn(self.plan, core.text(self.root, "SPEC.md"))

    def test_tool_metrics_use_observations_not_guessed_tokens(self):
        result = {"provider": "claude", "role": "reviewer", "model": "test", "duration_seconds": 1.5,
                  "stdout": '{"usage":{"input_tokens":10,"output_tokens":3,"cache_read_input_tokens":4}}'}
        runtime.record_observation(self.root, {"id": "TASK-001"}, "role", result)
        group = runtime.metrics(self.root)["groups"]["standard:reviewer"]
        self.assertEqual(group["known_input_tokens"], 10)
        self.assertEqual(group["role_calls"]["known_total"], 1)
        self.assertEqual(group["cached_input_tokens"]["known_total"], 4)
        self.assertIsNone(group["first_pass"]["rate"])

    def test_repair_changes_destination_not_identical_label(self):
        self.create()
        target = self.task.replace("planned", "active")
        self.write("SPEC.md", f"[{target}]({target})\n")
        preview = records.links_repair(self.root)
        records.links_repair(self.root, preview["preview_token"])
        self.assertEqual(core.text(self.root, "SPEC.md"), f"[{target}]({self.task})\n")

    def test_completed_broken_link_is_historical_advisory(self):
        self.create()
        self.write("execution/completed/EPIC-002/notes.md", "---\ndocument_type: note\n---\n"
                   "[Old](execution/active/EPIC-999/plan.md)\n")
        result = records.identity_check(self.root)
        self.assertTrue(result["passed"])
        self.assertEqual(result["advisory"][0]["code"], "historical_record_link")

    def test_cli_diagnostics_are_compact_unless_hashes_are_requested(self):
        self.create()
        for options in ([], ["--path", self.task]):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(forge.main(["--root", str(self.root), "identity-check", *options]), 0)
            result = json.loads(output.getvalue())
            if options:
                self.assertEqual(set(result["file_hashes"]), {self.task})
            else:
                self.assertNotIn("file_hashes", result)
                self.assertNotIn("declarations", result)


if __name__ == "__main__":
    unittest.main()
