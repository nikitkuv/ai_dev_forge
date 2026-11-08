"""Behavior checks for evidence-backed memory on isolated consumer projects."""
import contextlib
import io
import json
import shutil
from unittest.mock import patch

from test_python_tools import Repository
import forge
import forge_core as core
import forge_index as index
import forge_knowledge as knowledge
import forge_records as records
import forge_runtime as runtime
import forge_adapters as adapters
from pathlib import Path
import evaluate_agent_knowledge as evaluation


class KnowledgeTests(Repository):
    def setUp(self):
        super().setUp()
        self.consumer(False)
        self.path = "investigations/INV-0001-example.md"
        self.write("src/config.txt", "version one")
        self.finding = dict(id="RF-01", claim="known behavior", applicability="config version one",
                            status="verified", evidence_refs=["test: config constraint"], verified_at="2026-11-09",
                            verified_revision="baseline", recheck_when="config changes",
                            dependencies=[dict(kind="file", path="src/config.txt", sha256=core.digest(b"version one"))])
        self.save()

    def save(self, findings=None, **extra):
        meta = dict(document_type="investigation", id="INV-0001", subject="config", area="core",
                    outcome="unresolved", created_at="2026-11-09", updated_at="2026-11-09",
                    baseline_revision="baseline", relevant_paths=[], research_refs=[],
                    reusable_findings=[self.finding] if findings is None else findings, **extra)
        self.write(self.path, "---\n" + core.canonical(meta) + "\n---\n# INV-0001\n")

    def check(self):
        return knowledge.knowledge_check(self.root, self.path)["findings"][0]

    def test_current_changed_deleted_added_and_unknown_dependencies(self):
        before = (self.root / self.path).read_bytes()
        self.assertEqual(self.check()["verdict"], "unchanged")
        self.assertTrue(self.check()["requires_judgment"])
        self.write("src/config.txt", "version two")
        self.assertEqual(self.check()["verdict"], "changed")
        (self.root / "src/config.txt").unlink()
        self.assertEqual(self.check()["verdict"], "changed")
        self.assertEqual(before, (self.root / self.path).read_bytes())
        self.finding["dependencies"][0]["sha256"] = "absent"
        self.save()
        self.assertEqual(self.check()["verdict"], "unchanged")
        self.write("src/config.txt", "added")
        self.finding["dependencies"].append(dict(kind="environment", name="python", expected="3.13"))
        self.save()
        result = self.check()
        self.assertEqual(result["verdict"], "changed")
        self.assertIn("unknown", [v["verdict"] for v in result["dependencies"]])

    def test_untrusted_unknown_and_malformed_are_not_factual_candidates(self):
        for dependency in ({}, {"path": "../escape", "sha256": "absent"},
                           {"path": "src", "sha256": "absent"}, {"kind": "command", "argv": ["danger"]}):
            with self.subTest(dependency=dependency):
                self.finding["dependencies"] = [dependency]
                self.save()
                with patch("subprocess.run", side_effect=AssertionError("must not execute")):
                    self.assertEqual(self.check()["verdict"], "unknown")
                self.assertFalse(self.check()["factual_reuse_candidate"])
        self.finding["dependencies"] = []
        self.save()
        self.assertEqual(self.check()["verdict"], "unknown")
        for invalid in ([None], [dict(self.finding, id=[])], [dict(self.finding, verified_at=True)],
                        [dict(self.finding, verified_revision={"bad": True})], "bad", [self.finding, self.finding]):
            self.save(findings=invalid)
            result = records.identity_check(self.root)
            self.assertTrue(result["passed"], result)
            self.assertTrue(result["advisory"])
            check = knowledge.knowledge_check(self.root, self.path)
            self.assertTrue(check["advisory"] or all(not f["factual_reuse_candidate"] for f in check["findings"]))

    def test_permission_and_symlink_inputs_stay_unknown(self):
        with patch("forge_knowledge.within", side_effect=PermissionError):
            self.assertEqual(knowledge.dependency_check(self.root, self.finding["dependencies"][0])["verdict"], "unknown")
        try:
            (self.root / "link.txt").symlink_to(self.root / "src/config.txt")
        except OSError:
            return  # permission-dependent link creation; read-error check above is unconditional
        self.assertEqual(knowledge.dependency_check(self.root, dict(path="link.txt", sha256="absent"))["verdict"], "unknown")

    def test_hypothesis_obsolete_and_absent_legacy(self):
        for status in ("hypothesis", "obsolete"):
            self.finding["status"] = status
            self.save()
            self.assertFalse(self.check()["factual_reuse_candidate"])
        self.write(self.path, "---\ndocument_type: investigation\nid: INV-0001\n---\n# INV-0001\n")
        self.assertEqual(knowledge.knowledge_check(self.root, self.path)["findings"], [])
        self.assertEqual(records.identity_check(self.root)["advisory"], [])

    def test_identity_references_survive_moves_and_inventory_is_compact(self):
        task = "execution/active/EPIC-001-example/tasks/TASK-001.md"
        meta = dict(document_type="task", id="TASK-001", epic_id="EPIC-001", status="DONE", reusable_findings=[self.finding])
        self.write(task, "---\n" + core.canonical(meta) + "\n---\n# TASK-001\n")
        self.save(knowledge_refs=[dict(ref="TASK-001#RF-01", rationale="reused", checked_revision="head")])
        self.assertEqual(records.identity_check(self.root)["advisory"], [])
        (self.root / "execution/completed").mkdir()
        shutil.move(str(self.root / "execution/active/EPIC-001-example"), self.root / "execution/completed/EPIC-001-example")
        self.assertEqual(records.identity_check(self.root)["advisory"], [])
        inventory, errors = core.inventory(self.root, include_completed=True)
        self.assertFalse(errors)
        self.assertNotIn("known behavior", core.canonical(inventory))
        self.assertIn("RF-01", core.canonical(inventory))
        self.save(knowledge_refs=[dict(ref="TASK-001#RF-99", rationale="reused", checked_revision="head")])
        result = records.identity_check(self.root)
        self.assertTrue(result["passed"])
        self.assertTrue(any(a["code"] == "knowledge_reference" for a in result["advisory"]))

    def test_additive_correction_preserves_history_and_surfaces_on_reuse(self):
        original = (self.root / self.path).read_bytes()
        correction = dict(self.finding, correction_of="INV-0001#RF-01", claim="corrected behavior")
        meta = dict(document_type="investigation", id="INV-0002", reusable_findings=[correction])
        self.write("investigations/INV-0002-correction.md", "---\n" + core.canonical(meta) + "\n---\n# INV-0002\n")
        result = self.check()
        self.assertEqual(result["verdict"], "unknown")
        self.assertEqual(result["correction_paths"], ["investigations/INV-0002-correction.md"])
        self.assertEqual(original, (self.root / self.path).read_bytes())

    def test_cli_read_only_check(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(forge.main(["--root", str(self.root), "knowledge-check", self.path, "--finding", "RF-01"]), 0)
        self.assertEqual(json.loads(out.getvalue())["findings"][0]["verdict"], "unchanged")
        self.assertFalse((self.root / ".ai/local/index.db").exists())


class KnowledgeSearchTests(Repository):
    def source(self, number, body, area="core"):
        return self.write(f"investigations/INV-{number:04d}.md", f"---\ndocument_type: investigation\nid: INV-{number:04d}\narea: {area}\ncreated_at: 2026-11-09\n---\n{body}\n")

    def test_all_any_literal_filters_and_rebuild(self):
        self.source(1, "migration rollback")
        self.source(2, "migration", "other")
        self.source(3, "rollback")
        self.assertEqual(index.query(self.root, "migration rollback")["returned"], 1)
        self.assertEqual(index.query(self.root, "migration rollback", match="any")["returned"], 3)
        self.assertEqual(index.query(self.root, "migration rollback", area="core", match="any")["returned"], 2)
        self.assertEqual(index.query(self.root, "migration OR unknown")["returned"], 0)
        self.assertEqual(index.query(self.root, '"migration" "rollback"')["returned"], 1)
        with self.assertRaises(core.ForgeError):
            index.query(self.root, '""')
        with self.assertRaises(core.ForgeError):
            index.query(self.root, "migration", match="unsupported")
        self.source(1, "new behavior")
        current = index.query(self.root, "new")
        self.assertEqual(current["returned"], 1)
        (self.root / ".ai/local/index.db").unlink()
        self.assertEqual(index.query(self.root, "new")["results"], current["results"])

    def test_filters_and_ranking_before_limit(self):
        for i in range(1, 505):
            self.source(i, "needle " + "filler " * 100, "other")
        self.source(505, "needle", "wanted")
        self.source(506, "needle", "wanted")
        result = index.query(self.root, "needle", area="wanted", limit=1)
        self.assertEqual(result["results"][0]["id"], "INV-0505")
        result = index.query(self.root, "needle", limit=1)
        # Oracle: a document entirely about needle outranks diluted repeated mentions.
        self.assertEqual(result["results"][0]["id"], "INV-0505")

    def test_telemetry_no_content_and_separate_metrics(self):
        self.consumer(False)
        self.source(1, "private-query")
        index.query_observed(self.root, "private-query", workflow="forge-investigate")
        index.query_observed(self.root, "notfound")
        with self.assertRaises(core.ForgeError):
            index.query_observed(self.root, "private-query", match="bad")
        with patch.object(index, "query", side_effect=core.ForgeError("sensitive error")):
            with self.assertRaisesRegex(core.ForgeError, "sensitive error"):
                index.query_observed(self.root, "private-query")
        events = list((self.root / ".ai/local/metrics/search").glob("*.json"))
        self.assertEqual(len(events), 4)
        self.assertEqual(list((self.root / ".ai/local/metrics").glob("*.json")), [])
        encoded = "".join(p.read_text() for p in events)
        for secret in ("private-query", "sensitive error", "INV-0001", "notfound"):
            self.assertNotIn(secret, encoded)
        runtime.metrics_record(self.root, {"track": "standard", "stage": "testing", "role_calls": 1})
        result = runtime.metrics(self.root)
        self.assertEqual(result["groups"]["standard:testing"]["events"], 1)
        self.assertEqual(result["search"]["unknown"]["failures"], 2)
        self.assertEqual(result["search"]["unknown"]["zero_results"], 1)
        self.assertEqual(result["search"]["forge-investigate"]["successes"], 1)

    def test_telemetry_failure_preserves_original_search_and_error(self):
        self.source(1, "needle")
        with patch.object(runtime, "search_metrics_record", side_effect=PermissionError("private")), contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(index.query_observed(self.root, "needle")["returned"], 1)
            with self.assertRaisesRegex(core.ForgeError, "Matching mode"):
                index.query_observed(self.root, "needle", match="invalid")
        self.assertIn("telemetry unavailable", err.getvalue())
        self.assertNotIn("private", err.getvalue())


class KnowledgeIntegrationTests(Repository):
    def test_adapters_and_workflow_contracts(self):
        self.consumer(True)
        self.write(".agents/skills/user-owned/SKILL.md", "keep me")
        outputs, _ = adapters.render(self.root / ".ai", self.root)
        skill = ".agents/skills/forge-consolidate-knowledge/SKILL.md"
        self.assertIn(skill, outputs)
        self.assertEqual(outputs[skill], outputs[".claude/skills/forge-consolidate-knowledge/SKILL.md"])
        self.assertNotIn(".opencode/skills/forge-consolidate-knowledge/SKILL.md", outputs)
        self.assertLessEqual(len(outputs["AGENTS.md"]), 9500)
        for workflow in ("forge-investigate", "forge-prepare-epic", "forge-intake-feature", "forge-intake-external-work",
                         "forge-intake-bug", "forge-run-task", "forge-resume-development"):
            source = outputs[f".agents/skills/{workflow}/SKILL.md"].decode()
            self.assertIn("knowledge-check", source)
            self.assertIn("TASK/PLAN", source)
            self.assertIn("five additional", source)
            self.assertIn("no routine lesson or new gate", source)
        consolidation = outputs[skill].decode()
        for rule in ("20 by default", "Invoke no generated subagents", "Review alone edits no records", "concrete proposed edits"):
            self.assertIn(rule, consolidation)
        preview = adapters.preview(self.root)[0]
        adapters.apply(self.root, preview["preview_token"])
        self.assertEqual(core.text(self.root, ".agents/skills/user-owned/SKILL.md"), "keep me")

    def test_correction_uses_records_write_without_rewriting_completed_history(self):
        self.consumer(False)
        self.write("BACKLOG.md", "## Epic Roadmap\n| ID | Priority | Readiness | Status | Dependencies | Blocked by |\n| --- | --- | --- | --- | --- | --- |\n")
        # A closed research record is retained byte-for-byte; a new authorized INV owns the correction.
        template = core.text(self.root, ".ai/templates/INVESTIGATION.md")
        old = template.replace("INV-NNNN", "INV-0001").replace("outcome: unresolved", "outcome: no_action")
        self.write("investigations/INV-0001-original.md", old)
        before = (self.root / "investigations/INV-0001-original.md").read_bytes()
        new = template.replace("INV-NNNN", "INV-0002") + "\nCorrection to INV-0001: original evidence is historical; new reproduction is required.\n"
        packet = dict(schema_version=1, files=[dict(path="investigations/INV-0002-correction.md", content=new)])
        preview = records.records_write(self.root, packet)
        records.records_write(self.root, packet, preview["preview_token"])
        self.assertEqual(before, (self.root / "investigations/INV-0001-original.md").read_bytes())
        self.assertEqual(core.frontmatter(core.text(self.root, "investigations/INV-0002-correction.md"))["outcome"], "unresolved")

    def test_evaluation_oracles_and_unknown_measurements(self):
        result = evaluation.mechanical()
        self.assertEqual(len(result["cases"]), 8)
        self.assertTrue(all(c["mechanical"] == "passed" and c["agent_outcome"] == "unmeasured" for c in result["cases"]))
        fixture = json.loads(evaluation.FIXTURE.read_text())
        _, trial = evaluation.prepare(self.root / "trial", fixture["cases"][0], "B")
        self.assertIsNone(evaluation.validate_trial(trial)["input_tokens"])
        with self.assertRaises(ValueError):
            evaluation.prepare(self.root / "trial", fixture["cases"][0], "B")
        with self.assertRaises(ValueError):
            evaluation.validate_trial(dict(trial, input_tokens=0))
        with self.assertRaises(ValueError):
            evaluation.validate_trial(dict(trial, agent_outcome="measured", quality_pass=True))
        measured = dict(trial, agent_outcome="measured", fresh_session=True, model="test-model", settings={"effort": "high"},
                        trial=1, evidence_ref="trial-evidence", quality_pass=True, harmful_reuse=False,
                        retrieved_sources=[], used_sources=[])
        self.assertIsNone(evaluation.validate_trial(measured)["input_tokens"])
