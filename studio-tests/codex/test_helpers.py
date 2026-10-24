"""Regression tests for the Codex-only CCGS shell helpers.

The fixture is deliberately copied into a temporary path containing spaces and
non-ASCII characters: helpers must not depend on the checkout's real path.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
STUDIO = REPO / ".agents" / "studio"


def bash_path():
    configured = os.environ.get("CCGS_BASH")
    if configured and Path(configured).exists():
        return configured
    found = shutil.which("bash")
    if found and "WindowsApps" not in found:
        return found
    # Resolve Git Bash from the installed git executable or standard install
    # roots; do not encode a developer-machine-specific drive path.
    git = shutil.which("git")
    candidates = []
    if git:
        candidates.append(Path(git).resolve().parent.parent / "bin" / "bash.exe")
    for root in (os.environ.get("ProgramFiles"), os.environ.get("ProgramW6432"), os.environ.get("LOCALAPPDATA")):
        if root:
            candidates.append(Path(root) / "Git" / "bin" / "bash.exe")
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    if found:
        return found
    raise unittest.SkipTest("Bash is required (set CCGS_BASH)")
    if fallback.exists():
        return str(fallback)
    raise unittest.SkipTest("Bash is required (set CCGS_BASH)")


class HelperTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="CCGS 框架测试 "))
        self.root = self.tmp / "fixture project"
        self.root.mkdir()
        shutil.copytree(STUDIO, self.root / ".agents" / "studio")
        (self.root / "project.yaml").write_text(
            "schema_version: 1\n"
            "engine:\n  name: Godot\n  version: 4.3\n"
            "modes:\n  workflow: minimal\n  rigor: minimal\n"
            "commands:\n  test: 'bash run-tests.sh'\n",
            encoding="utf-8",
        )
        (self.root / "production").mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def shell(self, script, *args, cwd=None, env=None, stdin=None):
        merged = os.environ.copy()
        merged["PATH"] = str(Path(sys.executable).parent) + os.pathsep + merged.get("PATH", "")
        if env:
            merged.update(env)
        cmd = [bash_path(), str(self.root / ".agents" / "studio" / "scripts" / script), *map(str, args)]
        return subprocess.run(cmd, cwd=str(cwd or self.root), env=merged, input=stdin,
                              text=True, encoding="utf-8", errors="replace",
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def hook(self, *args, cwd=None, env=None):
        merged = os.environ.copy()
        merged["PATH"] = str(Path(sys.executable).parent) + os.pathsep + merged.get("PATH", "")
        if env:
            merged.update(env)
        return subprocess.run([bash_path(), str(self.root / ".agents" / "studio" / "hooks" / "yaml-helper.sh"), *args],
                              cwd=str(cwd or self.root), env=merged, text=True,
                              encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    @staticmethod
    def rows(output):
        return [line.split("\t") for line in output.splitlines() if line]

    def test_config_resolution_root_nested_local_and_orphan(self):
        nested = self.root / "src" / "nested"
        nested.mkdir(parents=True)
        (self.root / "project.local.yaml").write_text("modes:\n  review_mode: solo\n", encoding="utf-8")
        root = self.hook("resolve_config", "--keys", "review_mode,engine.name", cwd=self.root)
        self.assertEqual(root.returncode, 0, root.stderr)
        self.assertIn("review_mode: solo", root.stdout)
        nested_result = self.hook("resolve_config", "--keys", "review_mode,engine.name", cwd=nested,
                                  env={"CCGS_PROJECT_DIR": str(self.root)})
        self.assertEqual(nested_result.returncode, 0, nested_result.stderr)
        self.assertIn("review_mode: solo", nested_result.stdout)
        orphan = self.root / "orphan"
        orphan.mkdir()
        (orphan / "project.local.yaml").write_text("modes:\n  workflow: autonomous\n", encoding="utf-8")
        bad = self.hook("resolve_config", "--keys", "review_mode", cwd=orphan)
        self.assertIn("project.yaml", bad.stdout + bad.stderr)
        self.assertIn("missing", (bad.stdout + bad.stderr).lower())

    def test_nested_project_own_config_is_independent(self):
        nested = self.root / "nested project"
        nested.mkdir()
        (nested / "project.yaml").write_text("engine:\n  name: Unity\n", encoding="utf-8")
        result = self.hook("get_effective_yaml_key", "engine.name", cwd=nested,
                           env={"CCGS_PROJECT_DIR": str(self.root)})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "Unity")

    def test_config_set_dry_run_then_write_and_local_whitelist(self):
        before = (self.root / "project.yaml").read_bytes()
        dry = self.shell("config-set.sh", "modes.rigor", "minimal", "--dry-run", "--root", self.root)
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertEqual(before, (self.root / "project.yaml").read_bytes())
        actual = self.shell("config-set.sh", "--local", "modes.review_mode", "solo", "--root", self.root)
        self.assertEqual(actual.returncode, 0, actual.stderr)
        self.assertIn("solo", (self.root / "project.local.yaml").read_text(encoding="utf-8"))
        readback = self.hook("get_effective_yaml_key", "modes.review_mode")
        self.assertEqual(readback.stdout.strip(), "solo")
        locked = self.shell("config-set.sh", "--local", "engine.name", "Unity", "--root", self.root)
        self.assertEqual(locked.returncode, 4)

    def test_set_stage_keeps_yaml_and_mirror_in_sync(self):
        first = self.shell("set-stage.sh", "Pre-Production", "--root", self.root)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("stage_yaml\tPre-Production", first.stdout)
        self.assertEqual((self.root / "production" / "stage.txt").read_text(), "Pre-Production")
        unchanged = self.shell("set-stage.sh", "Pre-Production", "--dry-run", "--root", self.root)
        self.assertEqual(unchanged.returncode, 0, unchanged.stderr)
        self.assertIn("unchanged", unchanged.stdout)
        (self.root / "project.yaml").unlink()
        created = self.shell("set-stage.sh", "Production", "--root", self.root)
        self.assertEqual(created.returncode, 0, created.stderr)
        self.assertIn("created", created.stdout)
        self.assertIn((self.root / ".agents/studio/VERSION").read_text().strip(),
                      (self.root / "project.yaml").read_text(encoding="utf-8"))
        invalid = self.shell("set-stage.sh", "Not A Stage", "--root", self.root)
        self.assertEqual(invalid.returncode, 3)

    def test_markdown_story_status_and_facts_are_stable(self):
        story_dir = self.root / "production" / "epics" / "demo"
        story_dir.mkdir(parents=True)
        story = story_dir / "story-002-b.md"
        story.write_text(
            "> **Status**: Ready\n> **Type**: Logic\n> **Layer**: Gameplay\n"
            "> **Estimate**: S\n\n## Acceptance Criteria\n- [ ] one\n- [x] two\n- [ ] three\n"
            "\n## QA Test Cases\n- **AC-1** runs\n\nTR-demo-2\n", encoding="utf-8")
        (story_dir / "story-001-a.md").write_text("> **Status**: Complete\n", encoding="utf-8")
        changed = self.shell("md-section.sh", "set-field", story, "Status", "In Review")
        self.assertEqual(changed.returncode, 0, changed.stderr)
        self.assertIn("> **Status**: In Review", story.read_text(encoding="utf-8"))
        status = self.shell("story-status.sh")
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn("COMPLETE", status.stdout)
        facts = self.shell("story-facts.sh", "--all", "--root", self.root)
        self.assertEqual(facts.returncode, 0, facts.stderr)
        row = next(line for line in facts.stdout.splitlines() if line.startswith("STORY\tproduction/epics/demo/story-002-b.md"))
        self.assertEqual(row.split("\t")[2:5], ["IN_REVIEW", "In Review", "Logic"])

    def test_session_checkpoint_replacement_and_idempotent_append(self):
        body = "Branch: codex/core-workflow\nNext: verify helpers\n"
        made = self.shell("session-state.sh", "checkpoint", "--root", self.root, stdin=body)
        self.assertEqual(made.returncode, 0, made.stderr)
        shown = self.shell("session-state.sh", "show", "--root", self.root)
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertIn("Branch: codex/core-workflow", shown.stdout)
        replaced = self.shell("session-state.sh", "checkpoint", "--root", self.root, stdin="Branch: changed\n")
        self.assertEqual(replaced.returncode, 0, replaced.stderr)
        self.assertNotIn("core-workflow", (self.root / "production/session-state/active.md").read_text())
        narrative = "Observed: helper rows stable\n"
        self.assertEqual(self.shell("session-state.sh", "append", "--root", self.root, stdin=narrative).returncode, 0)
        once = (self.root / "production/session-state/active.md").read_bytes()
        again = self.shell("session-state.sh", "append", "--root", self.root, stdin=narrative)
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(once, (self.root / "production/session-state/active.md").read_bytes())

    def test_review_receipts_hash_unchanged_changed_and_gone(self):
        target = self.root / "evidence.txt"
        target.write_text("one\n", encoding="utf-8")
        stamp = self.shell("review-receipts.sh", "hash", target)
        self.assertEqual(stamp.returncode, 0, stamp.stderr)
        receipt = self.root / "receipt.txt"
        receipt.write_text(stamp.stdout, encoding="utf-8")
        same = self.shell("review-receipts.sh", "check", receipt, target)
        self.assertIn("UNCHANGED:", same.stdout)
        target.write_text("two\n", encoding="utf-8")
        changed = self.shell("review-receipts.sh", "check", receipt, target)
        self.assertIn("CHANGED:", changed.stdout)
        target.unlink()
        gone = self.shell("review-receipts.sh", "check", receipt)
        self.assertIn("GONE:", gone.stdout)

    def make_runner_fixture(self, engine, command, extra=""):
        (self.root / "project.yaml").write_text(
            f"engine:\n  name: {engine}\ncommands:\n  test: '{command}'\n{extra}", encoding="utf-8")
        return self.root

    def runner(self, engine, *args):
        return self.shell("test-run.sh", engine, *args, "--root", self.root)

    def test_godot_runner_success_nonzero_zero_tests_timeout_and_missing(self):
        (self.root / "addons/gdUnit4/bin").mkdir(parents=True)
        (self.root / "addons/gdUnit4/bin/GdUnitCmdTool.gd").write_text("", encoding="utf-8")
        stub = self.root / "godot-stub.sh"
        stub.write_text("#!/usr/bin/env bash\ncase \"$*\" in *--import*) exit 0;; *NoTests*) echo 'No test cases found'; exit 0;; *ParseFail*) echo 'Failed to load script'; exit 105;; *Orphan*) echo 'Orphan nodes'; exit 101;; *Fail*) exit 100;; *Sleep*) sleep 3;; esac\nexit 0\n", encoding="utf-8")
        stub.chmod(0o755)
        for label, expected in (("Success", "godot:0"), ("NoTests", "godot:0-zero"),
                                ("Fail", "godot:100"), ("ParseFail", "godot:105"),
                                ("Orphan", "godot:101")):
            self.make_runner_fixture("Godot", "bash godot-stub.sh " + label)
            result = self.runner("godot", "--exe", "godot-stub.sh", "--timeout", "2")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("ran\tyes", result.stdout)
            self.assertIn("rule\t" + expected, result.stdout)
        self.make_runner_fixture("Godot", "bash godot-stub.sh Sleep")
        timed = self.runner("godot", "--exe", "godot-stub.sh", "--timeout", "1")
        self.assertIn("timed_out\tyes", timed.stdout)
        (self.root / "addons/gdUnit4/bin/GdUnitCmdTool.gd").unlink()
        missing = self.runner("godot", "--exe", "missing-godot")
        self.assertIn("ran\tno", missing.stdout)
        self.assertIn("godot:no-gdunit4", missing.stdout)
        (self.root / "addons/gdUnit4/bin/GdUnitCmdTool.gd").write_text("", encoding="utf-8")
        self.make_runner_fixture("Godot", "missing-editor")
        unavailable = self.runner("godot", "--exe", "missing-godot")
        self.assertIn("rule\trunner-unavailable", unavailable.stdout)
        badlog = self.runner("godot", "--exe", "godot-stub.sh", "--log", "missing-dir/run.log")
        self.assertEqual(badlog.returncode, 0, badlog.stderr)
        self.assertTrue((self.root / "missing-dir" / "run.log").exists())
        self.assertTrue((self.root / "missing-dir" / "run.log.pre").exists())

    def test_unity_runner_result_ladder(self):
        manifest = self.root / "Packages"
        manifest.mkdir()
        (manifest / "manifest.json").write_text('{"dependencies":{"com.unity.test-framework":"1.0"}}', encoding="utf-8")
        stub = self.root / "unity-stub.sh"
        stub.write_text("#!/usr/bin/env bash\nfor a in \"$@\"; do if [ \"$a\" = test-results/editmode.xml ]; then mkdir -p test-results; echo '<test-run testcasecount=\"1\" passed=\"1\" failed=\"0\" />' > \"$a\"; fi; done\nexit 0\n", encoding="utf-8")
        stub.chmod(0o755)
        self.make_runner_fixture("Unity", "bash unity-stub.sh -testResults test-results/editmode.xml")
        result = self.runner("unity", "--exe", "unity-stub.sh")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("results_file\ttest-results/editmode.xml\tpresent", result.stdout)
        self.assertIn("tests\ttotal=1 passed=1 failed=0", result.stdout)
        self.assertIn("rule\tunity:0", result.stdout)
        self.make_runner_fixture("Unity", "true")
        self.assertIn("unity:no-results", self.runner("unity", "--exe", "unity-stub.sh").stdout)
        for xml, rule in (("<test-run testcasecount=\"0\" passed=\"0\" failed=\"0\" />", "unity:zero-tests"),
                          ("<test-run passed=\"1\" failed=\"0\" />", "unity:no-count"),
                          ("<test-run testcasecount=\"1\" passed=\"0\" failed=\"1\" />", "unity:result-fail")):
            variant = self.root / "unity-variant.sh"
            variant.write_text("#!/usr/bin/env bash\nmkdir -p test-results\nprintf '%s\\n' '" + xml + "' > test-results/editmode.xml\n", encoding="utf-8")
            variant.chmod(0o755)
            self.make_runner_fixture("Unity", "bash unity-variant.sh")
            self.assertIn("rule\t" + rule, self.runner("unity", "--exe", "unity-variant.sh").stdout)
        fail_runner = self.root / "unity-fail.sh"
        fail_runner.write_text("#!/usr/bin/env bash\nexit 2\n", encoding="utf-8")
        fail_runner.chmod(0o755)
        self.make_runner_fixture("Unity", "bash unity-fail.sh")
        failed = self.runner("unity", "--exe", "unity-fail.sh")
        self.assertIn("rule\tunity:2", failed.stdout)

    def test_runner_selects_os_specific_commands_test(self):
        manifest = self.root / "Packages"
        manifest.mkdir()
        (manifest / "manifest.json").write_text('{"dependencies":{"com.unity.test-framework":"1.0"}}', encoding="utf-8")
        for name, marker in (("win-stub.sh", "WINDOWS"), ("linux-stub.sh", "LINUX")):
            stub = self.root / name
            stub.write_text(
                "#!/usr/bin/env bash\n"
                f"echo {marker} > executed-{marker.lower()}\n"
                "for a in \"$@\"; do if [ \"$a\" = test-results/editmode.xml ]; then mkdir -p test-results; echo '<test-run testcasecount=\"1\" passed=\"1\" failed=\"0\" />' > \"$a\"; fi; done\n",
                encoding="utf-8")
            stub.chmod(0o755)
        (self.root / "project.yaml").write_text(
            "engine:\n  name: Unity\ncommands:\n  test:\n"
            "    windows: 'bash win-stub.sh -testResults test-results/editmode.xml'\n"
            "    linux: 'bash linux-stub.sh -testResults test-results/editmode.xml'\n",
            encoding="utf-8")
        result = self.runner("unity", "--os", "linux")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("command\tcommands.test", result.stdout)
        self.assertTrue((self.root / "executed-linux").exists())
        self.assertFalse((self.root / "executed-windows").exists())
        unavailable = self.runner("unity", "--os", "macos")
        self.assertIn("ran\tno", unavailable.stdout)
        self.assertIn("command-unavailable", unavailable.stdout)
        self.assertFalse((self.root / "executed-macos").exists())

    def test_unreal_runner_build_and_result_observations(self):
        (self.root / "demo.uproject").write_text("{}", encoding="utf-8")
        stub = self.root / "ue-stub.sh"
        stub.write_text("#!/usr/bin/env bash\necho 'Result={Success}'\nexit 0\n", encoding="utf-8")
        stub.chmod(0o755)
        self.make_runner_fixture("Unreal", "bash ue-stub.sh")
        result = self.runner("unreal", "--exe", str(self.root), "--no-build", "--os", "linux")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ran\tyes", result.stdout)
        self.assertIn("rule\tunreal:pass", result.stdout)
        fail_stub = self.root / "ue-fail.sh"
        fail_stub.write_text("#!/usr/bin/env bash\necho 'Result={Fail}'\nexit 1\n", encoding="utf-8")
        fail_stub.chmod(0o755)
        self.make_runner_fixture("Unreal", "bash ue-fail.sh")
        failed = self.runner("unreal", "--exe", str(self.root), "--no-build", "--os", "linux")
        self.assertIn("rule\tunreal:result-fail", failed.stdout)
        build_failed = self.runner("unreal", "--exe", str(self.root), "--os", "linux")
        self.assertIn("ran\tno", build_failed.stdout)
        self.assertIn("rule\tunreal:build-failed", build_failed.stdout)


if __name__ == "__main__":
    unittest.main()
