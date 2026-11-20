"""Campaign recovery/closure checks against temporary project records."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".ai/tools"))
from forge_core import ForgeError, conformance_errors
from forge_mutation import campaign_errors, mutation_plan


class CampaignTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="forge-campaign-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.registry = {"schema_version": 1, "next_id": "MUT-0002", "runs": ["MUT-0001"],
                         "next_campaign_id": "MTC-0002", "campaigns": ["MTC-0001"]}
        self.campaign = {
            "schema_version": 1, "id": "MTC-0001", "status": "awaiting_analysis",
            "objective": "audit", "policy": "audit_first",
            "budget": {"execution_seconds": 300, "consumed_execution_seconds": 50,
                       "analysis_candidates": 10, "consumed_analysis_candidates": 1,
                       "per_run_timeout_seconds": 60, "workers": 2, "maximum_verification_rounds": 2},
            "batches": [{"id": "B001", "status": "measured", "stale": False,
                         "run_ids": ["MUT-0001"], "current_run_ids": ["MUT-0001"],
                         "remaining_selection": []},
                        {"id": "B002", "status": "pending", "stale": False,
                         "run_ids": [], "current_run_ids": [], "remaining_selection": ["src/b.py"]}],
            "checkpoint": {"batch_id": "B001", "next_action": "analyze remaining candidates"}}
        self.run = {"id": "MUT-0001", "campaign": {"id": "MTC-0001", "batch_id": "B001", "purpose": "initial"},
                    "analysis": {"analyzed_candidates": 1, "remaining_candidates": 2,
                                 "analyzed_candidate_ids": ["m1"], "remaining_candidate_ids": ["m2", "m3"]}}

    def write(self, name, data):
        path = self.root / "quality/mutation-testing" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data), encoding="utf-8")

    def check(self):
        self.write("campaigns/MTC-0001.yaml", self.campaign)
        self.write("runs/MUT-0001.yaml", self.run)
        self.write("registry.yaml", self.registry)
        return campaign_errors(self.root, self.registry)

    def test_partial_analysis_survives_reload_with_second_batch_pending(self):
        self.assertEqual(self.check(), [])
        loaded = yaml.safe_load((self.root / "quality/mutation-testing/campaigns/MTC-0001.yaml").read_text())
        self.assertEqual(loaded["checkpoint"]["batch_id"], "B001")
        self.assertEqual(loaded["batches"][1]["id"], "B002")
        self.run["analysis"]["remaining_candidate_ids"].append("m1")
        self.assertIn("inconsistent candidate continuation ledger", " ".join(self.check()))

    def test_accepting_work_does_not_complete_pending_batches(self):
        self.campaign["status"] = "completed"
        self.campaign["closure"] = {"outcome": "analyzed", "completed_at": "2026-11-15",
                                    "evidence_refs": ["MUT-0001"]}
        self.assertIn("current closed batches", " ".join(self.check()))

    def test_explicit_residual_exceptions_are_distinct_from_full_completion(self):
        self.campaign["status"] = "completed"
        self.campaign["closure"] = {"outcome": "accepted_exceptions", "completed_at": "2026-11-15",
                                    "evidence_refs": ["MUT-0001"], "exceptions": ["B002 omitted"]}
        self.assertIn("explicit decision", " ".join(self.check()))
        self.campaign["closure"]["decision_ref"] = "user-decision-1"
        self.assertEqual(self.check(), [])

    def test_new_verification_run_links_to_same_batch_without_losing_next(self):
        self.campaign.update(status="verifying", policy="batch_then_fix", objective="hardening")
        self.registry.update(next_id="MUT-0003", runs=["MUT-0001", "MUT-0002"])
        verify = copy.deepcopy(self.run)
        verify.update(id="MUT-0002", analysis={})
        verify["campaign"].update(purpose="verification", predecessor_run_ids=["MUT-0001"])
        self.write("runs/MUT-0002.yaml", verify)
        self.campaign["batches"][0]["run_ids"].append("MUT-0002")
        self.campaign["batches"][0]["current_run_ids"] = ["MUT-0002"]
        self.assertEqual(self.check(), [])
        verify["campaign"]["batch_id"] = "B002"
        self.write("runs/MUT-0002.yaml", verify)
        self.assertIn("nonreciprocal", " ".join(self.check()))

    def test_stale_batch_prevents_ordinary_closure(self):
        self.campaign["batches"] = self.campaign["batches"][:1]
        self.campaign["batches"][0].update(status="closed", stale=True)
        self.campaign.update(status="completed", objective="metrics_only")
        self.campaign["closure"] = {"outcome": "metrics_collected", "completed_at": "2026-11-15",
                                    "evidence_refs": ["MUT-0001"]}
        self.assertIn("current closed batches", " ".join(self.check()))
        self.campaign["batches"][0]["stale"] = False
        self.assertEqual(self.check(), [])

    def test_budget_overrun_requires_pause(self):
        self.campaign["budget"]["consumed_execution_seconds"] = 301
        self.assertIn("exhausted budget", " ".join(self.check()))
        self.campaign["status"] = "paused"
        self.assertEqual(self.check(), [])

    def test_duplicate_and_dangling_campaigns_fail_without_changing_files(self):
        self.registry["campaigns"].extend(["MTC-0001", "MTC-0003"])
        errors = " ".join(self.check())
        self.assertIn("unique MTC", errors)
        self.assertIn("Missing mutation campaign", errors)
        self.assertIn("must exceed", errors)
        before = {p: p.read_bytes() for p in self.root.rglob("*.yaml")}
        campaign_errors(self.root, self.registry)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*.yaml")})

    def test_project_conformance_calls_campaign_validation(self):
        self.campaign["checkpoint"]["batch_id"] = "B099"
        self.check()
        self.assertIn("checkpoint references unknown batch", " ".join(conformance_errors(self.root, {})))

    def test_legacy_run_registry_needs_no_campaign(self):
        self.write("runs/MUT-0001.yaml", {"id": "MUT-0001", "analysis": {"remaining_candidates": 7}})
        self.assertEqual(campaign_errors(self.root, {"runs": ["MUT-0001"]}), [])

    def prepare_plan(self):
        tests = ["tests/test_ab.py"]
        self.campaign.update(schema_version=2, objective="hardening", findings=[],
                             tool=dict(backend="fixture", version="1", baseline_command="test",
                                       mutation_command="mutate"),
                             scope=dict(production_paths=["a.py", "b.py"], test_paths=tests,
                                        exclusions=[], dependency_inputs=["shared.py"]))
        for batch, path in zip(self.campaign["batches"], ["a.py", "b.py"]):
            batch["selection"] = dict(production_paths=[path], test_paths=tests, backend_selector=path)
        self.campaign["authorization"] = {"execution_ref": "user-plan-1",
                                          "plan_hash": mutation_plan(self.campaign)["plan_hash"]}

    def test_approval_covers_files_commands_order_and_limits_across_resume(self):
        self.prepare_plan()
        self.campaign["budget"]["consumed_execution_seconds"] += 5
        self.assertEqual(self.check(), [])
        for key, value in (("tool", {"version": "2"}), ("budget", {"workers": 3}),
                           ("scope", {"dependency_inputs": ["other.py"]}),
                           ("authorization", {"execution_ref": ""})):
            changed = copy.deepcopy(self.campaign)
            changed[key].update(value)
            with self.subTest(key=key), self.assertRaises(ForgeError):
                mutation_plan(changed, require_approval=True)
        self.campaign["batches"].reverse()
        self.assertIn("matching the current plan", " ".join(self.check()))

    def test_fix_returns_to_verification_then_next_batch(self):
        self.prepare_plan()
        first, second = self.campaign["batches"]
        finding = dict(run_id=self.run["id"], candidate_id="m1", batch_id=first["id"],
                       classification="actionable_test_gap", disposition="fix_requested",
                       work_refs=["TASK-001"])
        self.campaign.update(status="waiting_for_fixes", findings=[finding])
        self.assertEqual(self.check(), [])
        verify = copy.deepcopy(self.run)
        verify.update(id="MUT-0002", analysis={"status": "skipped_no_candidates"},
                      run={"outcome": "COMPLETED"}, baseline={"outcome": "passed"})
        verify["campaign"].update(purpose="verification", predecessor_run_ids=[self.run["id"]],
                                  full_batch_selection=first["selection"])
        self.registry.update(next_id="MUT-0004", runs=[self.run["id"], verify["id"], "MUT-0003"])
        self.write("runs/MUT-0002.yaml", verify)
        first.update(status="closed", current_run_ids=[verify["id"]])
        first["run_ids"].append(verify["id"])
        self.campaign["checkpoint"]["batch_id"] = second["id"]
        self.campaign["status"] = "running"
        self.assertEqual(self.check(), [])
        second.update(status="closed", run_ids=["MUT-0003"], current_run_ids=["MUT-0003"], remaining_selection=[])
        self.write("runs/MUT-0003.yaml", dict(verify, id="MUT-0003", campaign=dict(self.run["campaign"], batch_id="B002")))
        self.campaign.update(status="completed", closure=dict(completed_at="2026-11-20", outcome="verified",
                                                             evidence_refs=["MUT-0002", "MUT-0003"]))
        self.assertIn("mapped verification", " ".join(self.check()))
        finding.update(disposition="verified", verification_mapping="Boundary assertion killed the mapped mutant",
                       verification_run_ids=[verify["id"]])
        self.assertEqual(self.check(), [])
        verify["campaign"]["full_batch_selection"] = {"backend_selector": "one mutant"}
        self.write("runs/MUT-0002.yaml", verify)
        self.assertIn("full-batch verification", " ".join(self.check()))

    def test_malformed_campaign_and_nested_fields_report_errors(self):
        self.campaign["budget"] = "not a mapping"
        self.assertIn("budget must be a mapping", " ".join(self.check()))
        self.write("campaigns/MTC-0001.yaml", ["not a record"])
        self.assertIn("Expected mapping", " ".join(campaign_errors(self.root, self.registry)))


if __name__ == "__main__":
    unittest.main()
