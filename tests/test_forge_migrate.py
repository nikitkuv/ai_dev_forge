"""Framework migration command behavior using synthetic consumer projects."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".ai/tools"))
import forge_adapters as adapters
import forge_core as core
import forge_migration as migration


def tree_state(root, skip_local=False):
    state = {}
    for path in sorted(Path(root).rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        if skip_local and relative.startswith(".ai/local/"):
            continue
        state[relative] = core.digest(path.read_bytes())
    return state


class Repository(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="forge-migrate-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def consumer(self, mode="native_subagents"):
        """A realistic 4.11 consumer: template-shaped project.yaml plus a shared overlay."""
        shutil.copytree(ROOT / ".ai", self.root / ".ai", ignore=shutil.ignore_patterns("local", "__pycache__"))
        config = core.text(ROOT, ".ai/templates/project.yaml")
        if mode is None:
            config = config.replace("role_execution:\n  mode: null", "role_execution:\n  mode: null")
        else:
            config = config.replace("role_execution:\n  mode: null", f"role_execution:\n  mode: {mode}")
        config = config.replace("opencode:\n    enabled: true", "opencode:\n    enabled: false")
        self.write(".ai/project.yaml", config)
        self.write(".ai/custom/router-shared.md", "# Project rules\n\nKeep examples in Russian.\n")
        self.write("SPEC.md", "# Specification\n\nProtected consumer content.\n")
        self.write("BACKLOG.md", "## Epic Roadmap\n| ID | Priority | Readiness | Status | Dependencies | Blocked by |\n"
                                 "| --- | --- | --- | --- | --- | --- |\n| EPIC-001 | P0 | READY | PLANNED | — | — |\n")
        return config

    def next_version(self):
        manifest = core.load_yaml(self.root, ".ai/framework/manifest.yaml")
        major, minor, patch = (int(part) for part in str(manifest["framework"]["version"]).split("."))
        return f"{major}.{minor + 1}.0"

    def stage(self, version=None, contract=None, modify=True):
        """Copy the active bundle into .ai-next and shape it into a newer staged release.

        Project-owned state that happens to live inside .ai/ (project.yaml,
        custom/, local/, framework.lock) is never part of a staged release bundle.
        """
        shutil.copytree(self.root / ".ai", self.root / ".ai-next", ignore=shutil.ignore_patterns("__pycache__"))
        for project_owned in ("project.yaml", "custom", "local", "framework.lock", "integrations"):
            target = self.root / ".ai-next" / project_owned
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
        if version is None:
            version = self.next_version()
        manifest = core.load_yaml(self.root, ".ai-next/framework/manifest.yaml")
        manifest["framework"]["version"] = version
        (self.root / ".ai-next/framework/manifest.yaml").write_text(core.canonical(manifest), encoding="utf-8")
        if modify:
            conventions = self.root / ".ai-next/CONVENTIONS.md"
            conventions.write_text(conventions.read_text(encoding="utf-8") + "\nStaged release addition.\n", encoding="utf-8")
            router = self.root / ".ai-next/templates/adapters/codex/AGENTS.md"
            router.write_text(router.read_text(encoding="utf-8").replace(
                "# AI Development Forge — Project Router", "# AI Development Forge — Project Router (staged)"), encoding="utf-8")
        if contract is not None:
            (self.root / ".ai-next/framework/migrations.yaml").write_text(core.canonical(contract), encoding="utf-8")

    def unstage(self):
        shutil.rmtree(self.root / ".ai-next")

    def finding_ids(self, result):
        return [finding["id"] for finding in result["findings"]["blocking"]]


class ContractTests(Repository):
    def test_repository_contract_parses_and_roundtrips(self):
        data = core.load_yaml(ROOT, ".ai/framework/migrations.yaml")
        self.assertEqual(data["schema_version"], 1)
        for name, entry in data["versions"].items():
            migration.version_tuple(name)
            self.assertIsInstance(entry, dict)
            for key in entry:
                self.assertIn(key, {"notes", "config_additions", "config_decisions", "breaking", "backfill_commands"})
        self.assertEqual(core.yaml_value(core.text(ROOT, ".ai/framework/migrations.yaml")), data)

    def test_agent_first_entry_points_keep_cli_details_out_of_user_workflow(self):
        skill = core.text(ROOT, ".ai/framework/skills/forge-migrate-framework/SKILL.md")
        router = core.text(ROOT, ".ai/MIGRATE.md")
        specification = core.text(ROOT, "openspec/specs/framework-migration/spec.md")

        for document in (skill, router, specification):
            self.assertIn("local Forge clone", document)
            self.assertIn("preview token", document.lower())
        self.assertIn("stage the resolved release yourself", skill)
        self.assertIn("never ask the user to copy or re-enter the token", skill)
        self.assertIn("Do not ask the user to perform these staging steps", router)
        self.assertIn("the user is not asked to copy a token", specification)

    def test_maintained_user_docs_describe_current_behavior_not_release_history(self):
        for path in ("README.md", "MIGRATION.md", "FRAMEWORK.md", "RUNBOOK.md"):
            document = core.text(ROOT, path)
            self.assertNotRegex(document, r"(?i)\bv\d+\.\d+(?:\.\d+)?\b", path)
            for heading in ("Обновление до v", "Изменения v", "Совместимость v"):
                self.assertNotIn(heading, document, path)

    def test_range_filter_is_exclusive_lower_and_inclusive_upper(self):
        self.assertEqual([name for name, _ in migration.migration_entries(ROOT / ".ai", "4.10", "4.11.0")], ["4.11"])
        self.assertEqual([name for name, _ in migration.migration_entries(ROOT / ".ai", "4.2", "4.7.1")],
                         ["4.3", "4.4", "4.6", "4.7", "4.7.1"])
        self.assertEqual(migration.migration_entries(ROOT / ".ai", "4.12", "4.12"), [])
        self.assertEqual([name for name, _ in migration.migration_entries(ROOT / ".ai", "4.11", "4.12")], ["4.12"])


class YamlTextTests(unittest.TestCase):
    def test_leaf_flow_and_nested_insertion(self):
        source = ("schema_version: 2\nframework:\n  name: ai-dev-forge\nversion: 4.11.0\n"
                  "role_execution:\n  mode: null\nmodels:\n  opencode:\n    strong: {model: null}\n")
        updated = migration.update_yaml_text(source, "version", "4.12.0")
        self.assertIn("version: 4.12.0", updated)
        updated = migration.update_yaml_text(updated, "role_execution.mode", "native_subagents")
        self.assertIn("mode: native_subagents", updated)
        updated = migration.update_yaml_text(updated, "models.opencode.strong.model", "example/strong")
        self.assertIn("strong: {model: example/strong}", updated)
        updated = migration.update_yaml_text(updated, "documentation_language", "ru")
        self.assertIn("documentation_language: ru", updated)
        updated = migration.update_yaml_text(updated, "automation.authorization.mode", "strict")
        self.assertIn("automation:\n  authorization:\n    mode: strict", updated)
        parsed = core.yaml_value(updated)
        self.assertEqual(parsed["version"], "4.12.0")
        self.assertEqual(parsed["role_execution"]["mode"], "native_subagents")
        self.assertEqual(parsed["models"]["opencode"]["strong"]["model"], "example/strong")
        self.assertEqual(parsed["automation"]["authorization"]["mode"], "strict")

    def test_comment_and_layout_are_preserved(self):
        source = "# top comment\nmodels:\n  # tier comment\n  codex:\n    strong: {model: gpt-5.6-sol}\n"
        updated = migration.update_yaml_text(source, "models.codex.strong.model", "gpt-6")
        self.assertIn("# top comment", updated)
        self.assertIn("# tier comment", updated)
        self.assertIn("strong: {model: gpt-6}", updated)


class PreviewTests(Repository):
    def test_layout_and_version_gates(self):
        self.consumer()
        with self.assertRaisesRegex(core.ForgeError, "Staged"):
            migration.preview_migrate(self.root)
        active_version = str(core.load_yaml(self.root, ".ai/framework/manifest.yaml")["framework"]["version"])
        self.stage(version=active_version, modify=False)
        result, _ = migration.preview_migrate(self.root)
        self.assertIn("already_current", self.finding_ids(result))
        self.assertIsNone(result["preview_token"])
        self.unstage()
        major = active_version.split(".")[0]
        self.stage(version=f"{major}.0.0", modify=False)
        result, _ = migration.preview_migrate(self.root)
        self.assertIn("downgrade_refused", self.finding_ids(result))
        self.unstage()
        self.stage()
        self.write(".ai-next/EXTRA.md", "stray staged content\n")
        result, _ = migration.preview_migrate(self.root)
        finding = next(f for f in result["findings"]["blocking"] if f["id"] == "unexpected_staged_file")
        self.assertIn(".ai-next/EXTRA.md", finding["paths"])

    def test_router_overlay_gates(self):
        self.consumer()
        (self.root / ".ai/custom/router-shared.md").unlink()
        self.stage()
        result, _ = migration.preview_migrate(self.root)
        self.assertIn("router_extraction_required", self.finding_ids(result))
        self.assertIsNone(result["preview_token"])
        with self.assertRaisesRegex(core.ForgeError, "Router overlay file is missing"):
            migration.preview_migrate(self.root, router_shared="extracted.md")
        self.write("extracted.md", "# Extracted project rules\n")
        result, _ = migration.preview_migrate(self.root, router_shared="extracted.md")
        self.assertEqual(result["findings"]["blocking"], [])
        self.assertIn(".ai/custom/router-shared.md", [change["path"] for change in result["changes"]])
        self.write(".ai/custom/codex-router.md", "legacy codex rules\n")
        result, _ = migration.preview_migrate(self.root, router_shared="extracted.md")
        self.assertIn("legacy_overlay_present", self.finding_ids(result))

    def test_config_decisions_block_until_explicit_set(self):
        self.consumer(mode=None)
        staged_version = self.next_version()
        self.stage(version=staged_version,
                   contract={"schema_version": 1, "versions": {staged_version: {"config_decisions": [
                       {"key": "role_execution.mode", "suggest": "native_subagents", "note": "Choose one supported mode"}]}}})
        result, _ = migration.preview_migrate(self.root)
        finding = next(f for f in result["findings"]["blocking"] if f["id"] == "config_decision_required")
        self.assertEqual(finding["suggestions"][0]["key"], "role_execution.mode")
        self.assertEqual(finding["suggestions"][0]["suggest"], "native_subagents")
        self.assertIsNone(result["preview_token"])
        with self.assertRaisesRegex(core.ForgeError, r"--set refuses"):
            migration.preview_migrate(self.root, sets={"models.codex.strong.model": "gpt-6"})
        result, _ = migration.preview_migrate(self.root, sets={"role_execution.mode": "native_subagents"})
        self.assertEqual(result["findings"]["blocking"], [])
        self.assertEqual(result["config"]["sets_applied"], {"role_execution.mode": "native_subagents"})

    def test_deletion_requires_recorded_provenance(self):
        self.consumer()
        self.write(".ai/tools/legacy_helper.py", "legacy\n")
        adapters.apply(self.root, adapters.preview(self.root)[0]["preview_token"])
        self.stage()
        (self.root / ".ai-next/tools/legacy_helper.py").unlink()
        self.write(".ai/framework/unknown_extra.md", "unknown\n")
        result, _ = migration.preview_migrate(self.root)
        self.assertEqual(result["deletions"], [".ai/tools/legacy_helper.py"])
        self.assertEqual(result["preserved_unknown"], [".ai/framework/unknown_extra.md"])
        (self.root / ".ai/framework.lock").unlink()
        result, _ = migration.preview_migrate(self.root)
        self.assertEqual(result["deletions"], [])
        self.assertIn(".ai/tools/legacy_helper.py", result["preserved_unknown"])

    def test_integration_offline_classification(self):
        self.consumer()
        self.stage()
        self.write(".ai/integrations/kaiten.yaml", "schema_version: 1\nid: kaiten\nprofile: work_source\n")
        self.write(".ai/integrations/kaiten-copy.yaml", "schema_version: 1\nid: kaiten\nprofile: work_source\n")
        self.write(".ai/integrations/older.yaml", "schema_version: 0\nid: older\nprofile: work_source\n")
        self.write(".ai/integrations/future.yaml", "schema_version: 2\nid: future\nprofile: work_source\n")
        self.write(".ai/integrations/custom.yaml", "schema_version: 1\nid: custom\nprofile: my-thing\n")
        self.write(".ai/integrations/broken.yaml", "schema_version: [oops\n")
        self.write(".ai/integrations/notes.txt", "plain text\n")
        self.write(".ai/integrations/work-items.yaml", "schema_version: 1\nitems: []\n")
        result, _ = migration.preview_migrate(self.root)
        by_path = {item["path"]: item["classification"] for item in result["integrations"]}
        self.assertEqual(by_path[".ai/integrations/kaiten.yaml"], "ownership_collision")
        self.assertEqual(by_path[".ai/integrations/kaiten-copy.yaml"], "ownership_collision")
        self.assertEqual(by_path[".ai/integrations/older.yaml"], "older_migratable")
        self.assertEqual(by_path[".ai/integrations/future.yaml"], "unsupported_future")
        self.assertEqual(by_path[".ai/integrations/custom.yaml"], "custom_profile")
        self.assertEqual(by_path[".ai/integrations/broken.yaml"], "malformed")
        self.assertEqual(by_path[".ai/integrations/notes.txt"], "malformed")
        self.assertEqual(by_path[".ai/integrations/work-items.yaml"], "current_supported")
        self.assertIn("integration_ownership_collision", self.finding_ids(result))
        touched = {change["path"] for change in result["changes"]} | set(result["deletions"])
        self.assertFalse(any(path.startswith(".ai/integrations/") for path in touched))

    def test_preview_token_binds_inputs_and_writes_nothing(self):
        self.consumer()
        active_version = str(core.load_yaml(self.root, ".ai/framework/manifest.yaml")["framework"]["version"])
        expected = self.next_version()
        self.stage()
        before = tree_state(self.root)
        result, _ = migration.preview_migrate(self.root)
        self.assertEqual(tree_state(self.root), before)
        token = result["preview_token"]
        self.assertIsNotNone(token)
        self.assertEqual(result["old_version"], active_version)
        self.assertEqual(result["new_version"], expected)
        changed = [change["path"] for change in result["changes"]]
        self.assertIn(".ai/framework/manifest.yaml", changed)
        self.assertIn("AGENTS.md", changed)
        self.assertIn(".ai/project.yaml", changed)
        self.write("AGENTS.md", "manually changed")
        self.assertNotEqual(migration.preview_migrate(self.root)[0]["preview_token"], token)
        self.write("SPEC.md", "# Specification\n\nProtected consumer content, edited.\n")
        self.assertNotEqual(migration.preview_migrate(self.root)[0]["preview_token"], token)
        conventions = self.root / ".ai-next/CONVENTIONS.md"
        conventions.write_text(conventions.read_text(encoding="utf-8") + "\nanother staged change\n", encoding="utf-8")
        self.assertNotEqual(migration.preview_migrate(self.root)[0]["preview_token"], token)


class ApplyTests(Repository):
    def test_apply_replaces_bundle_renders_and_locks(self):
        self.consumer()
        expected = self.next_version()
        active_version = str(core.load_yaml(self.root, ".ai/framework/manifest.yaml")["framework"]["version"])
        self.write(".ai/tools/legacy_helper.py", "legacy\n")
        adapters.apply(self.root, adapters.preview(self.root)[0]["preview_token"])
        self.stage()
        (self.root / ".ai-next/tools/legacy_helper.py").unlink()
        self.write(".ai/framework/unknown_extra.md", "unknown\n")
        result, _ = migration.preview_migrate(self.root)
        outcome = migration.apply_migrate(self.root, result["preview_token"])
        self.assertIn(".ai/tools/legacy_helper.py", outcome["deleted"])
        self.assertTrue(outcome["staging_removed"])
        self.assertFalse((self.root / ".ai-next").exists())
        self.assertEqual(str(core.load_yaml(self.root, ".ai/framework/manifest.yaml")["framework"]["version"]), expected)
        self.assertIn("Staged release addition", core.text(self.root, ".ai/CONVENTIONS.md"))
        self.assertIn("(staged)", core.text(self.root, "AGENTS.md"))
        self.assertIn("# Project rules", core.text(self.root, "AGENTS.md"))
        self.assertEqual(core.text(self.root, "CLAUDE.md").strip(), "@AGENTS.md")
        self.assertEqual(core.text(self.root, ".ai/framework/unknown_extra.md"), "unknown\n")
        self.assertEqual(core.text(self.root, "SPEC.md"), "# Specification\n\nProtected consumer content.\n")
        self.assertIn("EPIC-001", core.text(self.root, "BACKLOG.md"))
        config = core.load_yaml(self.root, ".ai/project.yaml")
        self.assertEqual(str(config["version"]), expected)
        self.assertEqual(config["role_execution"]["mode"], "native_subagents")
        lock = core.load_yaml(self.root, ".ai/framework.lock")
        self.assertEqual(lock["bundle_state"]["files"][".ai/framework/manifest.yaml"],
                         core.digest((self.root / ".ai/framework/manifest.yaml").read_bytes()))
        self.assertFalse((self.root / ".ai/local/migrate-transaction").exists())
        self.assertTrue((self.root / ".agents/skills/forge-migrate-framework/SKILL.md").exists())

    def test_stale_token_and_unapproved_collision(self):
        self.consumer()
        adapters.apply(self.root, adapters.preview(self.root)[0]["preview_token"])
        self.stage()
        stale = migration.preview_migrate(self.root)[0]["preview_token"]
        self.write("AGENTS.md", core.text(self.root, "AGENTS.md") + "\nmanual line\n")
        with self.assertRaisesRegex(core.ForgeError, "Stale"):
            migration.apply_migrate(self.root, stale)
        fresh = migration.preview_migrate(self.root)[0]
        self.assertIn("AGENTS.md", fresh["collisions"])
        with self.assertRaisesRegex(core.ForgeError, "Unapproved collisions"):
            migration.apply_migrate(self.root, fresh["preview_token"])
        with self.assertRaisesRegex(core.ForgeError, "neither collisions nor preserved"):
            migration.apply_migrate(self.root, fresh["preview_token"], approved_collisions=("SPEC.md", "AGENTS.md"))
        outcome = migration.apply_migrate(self.root, fresh["preview_token"], approved_collisions=("AGENTS.md",))
        self.assertIn("AGENTS.md", outcome["applied"])
        self.assertNotIn("manual line", core.text(self.root, "AGENTS.md"))

    def test_validation_failure_rolls_back_completely(self):
        self.consumer()
        self.stage()
        manifest = core.load_yaml(self.root, ".ai-next/framework/manifest.yaml")
        manifest["skills"] = manifest["skills"] + ["ghost-skill"]
        (self.root / ".ai-next/framework/manifest.yaml").write_text(core.canonical(manifest), encoding="utf-8")
        result, _ = migration.preview_migrate(self.root)
        self.assertIsNotNone(result["preview_token"])
        before = tree_state(self.root, skip_local=True)
        with self.assertRaisesRegex(core.ForgeError, "Post-migration validation failed"):
            migration.apply_migrate(self.root, result["preview_token"])
        self.assertEqual(tree_state(self.root, skip_local=True), before)
        self.assertTrue((self.root / ".ai-next").exists())
        self.assertEqual(str(core.load_yaml(self.root, ".ai/framework/manifest.yaml")["framework"]["version"]),
                         result["old_version"])

    def test_protected_path_tamper_triggers_rollback(self):
        self.consumer()
        self.stage()
        result, _ = migration.preview_migrate(self.root)

        def tampering_validate(root, project=False):
            Path(root, "SPEC.md").write_text("tampered mid-flight", encoding="utf-8")
            return {"passed": True, "errors": []}

        with patch.object(core, "validate", side_effect=tampering_validate):
            with self.assertRaisesRegex(core.ForgeError, "Protected paths changed"):
                migration.apply_migrate(self.root, result["preview_token"])
        self.assertEqual(core.text(self.root, "SPEC.md"), "tampered mid-flight")
        self.assertEqual(str(core.load_yaml(self.root, ".ai/framework/manifest.yaml")["framework"]["version"]),
                         result["old_version"])
        self.assertTrue((self.root / ".ai-next").exists())


class RecoveryTests(Repository):
    def test_recover_restores_interrupted_transaction_and_refuses_later_edits(self):
        self.consumer()
        original = core.text(self.root, ".ai/BOOTSTRAP.md")
        self.write(".ai/framework/ghost-extra.md", "extra\n")
        transaction = core.Transaction(self.root, "migrate")
        transaction.claim()
        transaction.write({".ai/BOOTSTRAP.md": b"partial state", ".ai/framework/ghost-extra.md": None})
        self.assertEqual(core.text(self.root, ".ai/BOOTSTRAP.md"), "partial state")
        self.assertFalse((self.root / ".ai/framework/ghost-extra.md").exists())
        outcome = migration.recover_migrate(self.root)
        self.assertIn(".ai/BOOTSTRAP.md", outcome["restored"])
        self.assertIn(".ai/framework/ghost-extra.md", outcome["restored"])
        self.assertEqual(core.text(self.root, ".ai/BOOTSTRAP.md"), original)
        self.assertEqual(core.text(self.root, ".ai/framework/ghost-extra.md"), "extra\n")
        second = core.Transaction(self.root, "migrate")
        second.claim()
        second.write({".ai/MIGRATE.md": b"partial"})
        self.write(".ai/MIGRATE.md", "user edited meanwhile")
        with self.assertRaisesRegex(core.ForgeError, "Recovery conflicts"):
            migration.recover_migrate(self.root)


class CommandLineTests(Repository):
    def test_exit_codes_and_compact_json(self):
        self.consumer()
        self.stage()

        def run(*arguments):
            completed = subprocess.run(
                [sys.executable, str(ROOT / ".ai/tools/forge.py"), "--root", str(self.root), "migrate", *arguments],
                capture_output=True, text=True, encoding="utf-8")
            return completed.returncode, json.loads(completed.stdout)

        code, payload = run()
        self.assertEqual(code, 0)
        self.assertEqual(payload["command"], "migrate")
        self.assertIsNotNone(payload["preview_token"])
        code, payload = run("--apply", "deadbeef")
        self.assertEqual(code, 2)
        self.assertIn("error", payload)
        (self.root / ".ai/custom/router-shared.md").unlink()
        code, payload = run()
        self.assertEqual(code, 1)
        self.assertIs(payload["passed"], False)
        self.assertTrue(payload["findings"]["blocking"])

    def test_documented_usage_examples_run_as_written(self):
        """The USAGE.md command forms execute verbatim against a synthetic consumer."""
        self.consumer()
        expected = self.next_version()
        self.stage()

        def run(*arguments):
            completed = subprocess.run(
                [sys.executable, str(ROOT / ".ai/tools/forge.py"), "migrate", *arguments],
                cwd=self.root, capture_output=True, text=True, encoding="utf-8")
            return completed.returncode, json.loads(completed.stdout)

        code, payload = run()
        self.assertEqual(code, 0)
        token = payload["preview_token"]
        code, payload = run("--diff")
        self.assertEqual(code, 0)
        self.assertIn("diff", payload["changes"][0])
        # A second identical preview keeps the token stable; apply then succeeds.
        code, payload = run()
        self.assertEqual(payload["preview_token"], token)
        code, payload = run("--apply", token)
        self.assertEqual(code, 0)
        self.assertEqual(payload["new_version"], expected)
        self.assertFalse((self.root / ".ai-next").exists())


if __name__ == "__main__":
    unittest.main()
