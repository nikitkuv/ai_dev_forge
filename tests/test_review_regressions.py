"""Consumer and Git regressions from the November framework review."""
from pathlib import Path
from unittest.mock import patch

import test_forge_migrate as migration_tests
import test_python_tools as fixtures

core = fixtures.core
adapters = fixtures.adapters
lifecycle = fixtures.lifecycle
migration = migration_tests.migration
ROOT = fixtures.ROOT


class ReleaseTests(migration_tests.Repository):
    def test_shipped_release_metadata_agrees_and_covers_migration_notes(self):
        version = core.load_yaml(ROOT, ".ai/framework/manifest.yaml")["framework"]["version"]
        self.assertEqual(core.load_yaml(ROOT, ".ai/templates/project.yaml")["version"], version)
        self.assertGreater(migration.version_tuple(version), migration.version_tuple("4.12.0"))
        for entry in core.load_yaml(ROOT, ".ai/framework/migrations.yaml")["versions"]:
            self.assertLessEqual(migration.version_tuple(entry), migration.version_tuple(version))

    def test_upgrade_from_412_uses_unmodified_shipped_target_and_staged_rule_contract(self):
        self.consumer()
        shipped = core.load_yaml(ROOT, ".ai/framework/manifest.yaml")["framework"]["version"]
        self.stage(version=shipped, modify=False)
        # Only the active fixture is downgraded; the shipped target is never bumped.
        manifest = core.load_yaml(self.root, ".ai/framework/manifest.yaml")
        manifest["framework"]["version"] = "4.12.0"
        self.write(".ai/framework/manifest.yaml", core.canonical(manifest))
        self.write(".ai/project.yaml", migration.update_yaml_text(
            core.text(self.root, ".ai/project.yaml"), "version", "4.12.0"))
        contracts = core.load_yaml(self.root, ".ai/framework/contracts.yaml")
        del contracts["enums"]["project_rule_kinds"]
        self.write(".ai/framework/contracts.yaml", core.canonical(contracts))
        declaration = "schema_version: 1\nrules:\n- id: keep\n  statement: Keep the public contract.\n  kind: code\n  scope: [src]\n"
        self.write(".ai/custom/rules.yaml", declaration)
        before = {p: core.text(self.root, p) for p in ("SPEC.md", "BACKLOG.md", ".ai/custom/rules.yaml")}
        preview, _ = migration.preview_migrate(self.root)
        self.assertEqual(preview["findings"]["blocking"], [])
        self.assertIsNotNone(preview["preview_token"])
        self.assertTrue(any(item.get("version") == "4.13" for item in preview["findings"]["advisory"]))
        migration.apply_migrate(self.root, preview["preview_token"])
        self.assertEqual(core.load_yaml(self.root, ".ai/project.yaml")["version"], shipped)
        self.assertIn("- keep: Keep the public contract.", core.text(self.root, "AGENTS.md"))
        for path, content in before.items():
            self.assertEqual(core.text(self.root, path), content)


class RuleTests(fixtures.Repository):
    def test_render_rule_contract_is_a_fingerprinted_input(self):
        self.consumer(False)
        self.write(".ai/custom/rules.yaml", "schema_version: 1\nrules: []\n")
        preview, _, inputs, _ = adapters.preview(self.root)
        self.assertIn(".ai/framework/contracts.yaml", [item["path"] for item in inputs["files"]])
        path = ".ai/framework/contracts.yaml"
        self.write(path, core.text(self.root, path) + "\n# Updated rule contract revision\n")
        with self.assertRaisesRegex(core.ForgeError, "Stale preview"):
            adapters.apply(self.root, preview["preview_token"])

    def test_removing_last_rule_requires_sync_for_empty_and_absent_declaration(self):
        self.consumer(False)
        self.write("BACKLOG.md", "## Epic Roadmap\n"
                   "| ID | Priority | Readiness | Status | Dependencies | Blocked by |\n"
                   "| --- | --- | --- | --- | --- | --- |\n")
        overlay = "Project-owned overlay stays intact.\n"
        self.write(".ai/custom/router-shared.md", overlay)
        for remove_file in (False, True):
            with self.subTest(remove_file=remove_file):
                self.write(".ai/custom/rules.yaml", "schema_version: 1\nrules:\n"
                           "- id: old\n  statement: Obsolete rule.\n  kind: code\n  scope: [src]\n")
                adapters.apply(self.root, adapters.preview(self.root)[0]["preview_token"])
                if remove_file:
                    (self.root / ".ai/custom/rules.yaml").unlink()
                else:
                    self.write(".ai/custom/rules.yaml", "schema_version: 1\nrules: []\n")
                result = core.validate(self.root, True)
                self.assertTrue(any("old" in error and "no .ai/custom/rules.yaml entry" in error
                                    for error in result["errors"]), result)
                adapters.apply(self.root, adapters.preview(self.root)[0]["preview_token"])
                self.assertEqual(core.rules_router_divergence(self.root), [])
                self.assertNotIn("Obsolete rule.", core.text(self.root, "AGENTS.md"))
                self.assertEqual(core.text(self.root, ".ai/custom/router-shared.md"), overlay)


class AcceptanceTests(fixtures.Repository):
    seeded = fixtures.MutationTests.seeded
    write_task_with_state = fixtures.MutationTests.write_task_with_state

    def task_from_template_sections(self):
        task = self.seeded(active=True, task_status="AWAITING USER ACCEPTANCE")
        template = core.text(ROOT, ".ai/templates/TASK.md")
        blocks = template[template.index("## User Validation"):template.index("## Iteration History")]
        self.write(task, core.text(self.root, task).replace("## Iteration History", blocks + "## Iteration History"))
        return task

    def test_clean_acceptance_ignores_template_choice_row(self):
        task = self.task_from_template_sections()
        preview = lifecycle.accept_record(self.root, task, "user", "accepted without corrections")
        lifecycle.accept_record(self.root, task, "user", "accepted without corrections", apply_token=preview["preview_token"])
        self.assertEqual(core.frontmatter(core.text(self.root, task))["status"], "DONE")

    def test_real_rejection_alongside_template_still_requires_followup(self):
        task = self.task_from_template_sections()
        self.write(task, core.text(self.root, task).replace("## Process Follow-up",
                   "| 2026-11-08 | behavior | changes requested | wrong result |\n\n## Process Follow-up"))
        with self.assertRaisesRegex(core.ForgeError, "requires a recorded Process Follow-up"):
            lifecycle.accept_record(self.root, task, "user", "accepted after correction")


class ScopedCommitTests(fixtures.Repository):
    def git(self, *args):
        result = core.git_capture(self.root, ["--literal-pathspecs", *args])
        self.assertEqual(result["exit_code"], 0, result)
        return result["stdout"]

    def setUp(self):
        super().setUp()
        self.git("init", "--quiet")
        self.git("config", "user.name", "Forge tests")
        self.git("config", "user.email", "forge@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.write(".ai/project.yaml", "git:\n  policy: auto_commit_after_acceptance\n")
        self.task = "TASK.md"
        self.write(self.task, "---\nid: TASK-001\nstatus: DONE\n---\n# Task\n"
                   "## Workflow State\n```yaml\nreview_packet:\n  changed_paths: [src/code.py]\n```\n")
        self.write("src/code.py", "before\n")
        self.write("unrelated.txt", "before\n")
        self.git("add", ".")
        self.git("commit", "-qm", "baseline")

    def state(self):
        index_path = Path(self.git("rev-parse", "--git-path", "index").strip())
        if not index_path.is_absolute():
            index_path = self.root / index_path
        return (self.git("rev-parse", "HEAD"), index_path.read_bytes(),
                {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob("*")
                 if p.is_file() and ".git" not in p.relative_to(self.root).parts})

    def test_unrelated_staged_modification_refused_before_any_mutation(self):
        self.write("unrelated.txt", "user's staged content\n")
        self.git("add", "unrelated.txt")
        self.write("src/code.py", "accepted content\n")
        before = self.state()
        with self.assertRaisesRegex(core.ForgeError, "Unrelated staged.*unrelated.txt"):
            lifecycle.commit_scoped(self.root, self.task, authorized=True)
        self.assertEqual(self.state(), before)

    def test_staged_rename_checks_both_endpoints(self):
        self.git("mv", "unrelated.txt", "renamed file.txt")
        before = self.state()
        with self.assertRaisesRegex(core.ForgeError, "Unrelated staged"):
            lifecycle.commit_scoped(self.root, self.task, paths=["renamed file.txt"], authorized=True)
        self.assertEqual(self.state(), before)

    def test_tracked_deletions_staged_and_unstaged_with_unicode(self):
        for staged in (False, True):
            with self.subTest(staged=staged):
                name = f"src/старый файл {staged}.py"
                self.write(name, "obsolete\n")
                self.git("add", name)
                self.git("commit", "-qm", "add obsolete file")
                (self.root / name).unlink()
                if staged:
                    self.git("add", name)
                result = lifecycle.commit_scoped(self.root, self.task, paths=[name], authorized=True)
                self.assertTrue(result["committed"])
                self.assertNotIn(name, self.git("ls-tree", "-r", "--name-only", "-z", "HEAD").split("\0"))
                self.assertEqual(self.git("diff-tree", "--no-commit-id", "--name-only", "-z", "-r", "HEAD").split("\0")[:-1], [name])

    def test_unknown_missing_path_rejected_without_mutation(self):
        before = self.state()
        with self.assertRaisesRegex(core.ForgeError, "missing.*absent.py"):
            lifecycle.commit_scoped(self.root, self.task, paths=["absent.py"], authorized=True)
        self.assertEqual(self.state(), before)

    def test_literal_filename_and_directory_scope_exclude_unrelated_work(self):
        name = "src/[draft] пример.txt"
        self.write(name, "scoped addition\n")
        self.write("unrelated.txt", "unstaged user work\n")
        result = lifecycle.commit_scoped(self.root, self.task, paths=["src"], authorized=True)
        self.assertTrue(result["committed"])
        self.assertEqual(self.git("diff-tree", "--no-commit-id", "--name-only", "-z", "-r", "HEAD").split("\0")[:-1], [name])
        self.assertIn("unrelated.txt", result["excluded_unrelated"])

    def test_explicit_filename_is_not_a_glob(self):
        self.write("src/[ab].py", "literal file\n")
        self.write("src/a.py", "unrelated match\n")
        result = lifecycle.commit_scoped(self.root, self.task, paths=["src/[ab].py"], authorized=True)
        self.assertTrue(result["committed"])
        self.assertEqual(self.git("diff-tree", "--no-commit-id", "--name-only", "-z", "-r", "HEAD").split("\0")[:-1], ["src/[ab].py"])
        self.assertIn("src/a.py", result["excluded_unrelated"])

    def test_first_commit_on_unborn_branch_keeps_scope(self):
        self.git("checkout", "--orphan", "first-commit")
        self.git("rm", "-r", "--cached", ".")
        result = lifecycle.commit_scoped(self.root, self.task, authorized=True)
        self.assertTrue(result["committed"])
        self.assertEqual(set(self.git("ls-tree", "-r", "--name-only", "-z", "HEAD").split("\0")[:-1]),
                         {self.task, "src/code.py"})

    def test_manual_deletion_preview_does_not_change_index(self):
        self.write(".ai/project.yaml", "git:\n  policy: manual\n")
        (self.root / "src/code.py").unlink()
        before = self.state()
        result = lifecycle.commit_scoped(self.root, self.task, authorized=True)
        self.assertFalse(result["committed"])
        self.assertEqual(self.state(), before)

    def test_git_read_failure_prevents_mutation(self):
        before = self.state()
        with patch.object(lifecycle, "git_capture", return_value={"exit_code": 128, "stdout": "", "stderr": "read failed"}) as capture:
            with self.assertRaisesRegex(core.ForgeError, "read failed"):
                lifecycle.commit_scoped(self.root, self.task, authorized=True)
            self.assertFalse(any("add" in call.args[1] or "commit" in call.args[1] for call in capture.call_args_list))
        self.assertEqual(self.state(), before)
