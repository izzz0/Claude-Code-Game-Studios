"""Cocos adapter contract tests; all runners are local stdlib fixtures."""
from pathlib import Path
import json
import os
import shutil
import shlex
import subprocess
import tempfile
import time
import unittest

from test_helpers import bash_path, REPO


class CocosAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="CCGS Cocos "))
        self.root = self.tmp / "项目 project"
        self.root.mkdir()
        shutil.copytree(REPO / ".agents" / "studio", self.root / ".agents" / "studio")
        (self.root / "project.yaml").write_text(
            "engine:\n  name: Cocos\n  version: 3.8.8\ncommands:\n  test:\n"
            "    windows: 'bash tap-stub.sh'\n    linux: 'bash tap-stub.sh'\n",
            encoding="utf-8")
        (self.root / "project.json").write_text(json.dumps({"creator": {"version": "3.8.8"}}), encoding="utf-8")
        (self.root / "assets/scripts").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def invoke(self, *args):
        env = os.environ.copy()
        env["PATH"] = str(Path(os.sys.executable).parent) + os.pathsep + env.get("PATH", "")
        return subprocess.run([bash_path(), str(self.root / ".agents/studio/scripts/test-run.sh"), *args,
                              "--root", str(self.root)], cwd=self.root, env=env,
                             text=True, encoding="utf-8", errors="replace",
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_roots_and_unicode_path(self):
        helper = self.root / ".agents/studio/hooks/yaml-helper.sh"
        result = subprocess.run([bash_path(), str(helper), "resolve_code_roots"], cwd=self.root,
                                text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("assets/scripts\tproject.yaml", result.stdout)
        self.assertEqual(self.invoke("cocos", "--dry-run", "--os", "windows").returncode, 0)

    def test_tap_positive_skip_todo_cancelled_and_failure(self):
        stub = self.root / "tap-stub.sh"
        stub.write_text("""#!/usr/bin/env bash
case "$1" in
  pass) printf 'TAP version 13\\n1..2\\nok 1 - works\\nok 2 - optional # SKIP\\n' ;;
  todo) printf 'TAP version 13\\n1..2\\nok 1 - works\\nnot ok 2 - later # TODO\\n' ;;
  cancel) printf 'TAP version 13\\nnot ok 1 - cancelled\\n  ---\\n  type: 'test'\\n  failureType: 'cancelledByParent'\\n  ...\\n# tests 1\\n# pass 0\\n# fail 0\\n# cancelled 1\\n# skipped 0\\n# todo 0\\n1..1\\n' ;;
  skip) printf 'TAP version 13\\n1..1\\nok 1 - unavailable # SKIP\\n' ;;
  fail) printf 'TAP version 13\\n1..1\\nnot ok 1 - broken\\n'; exit 1 ;;
  zero) printf 'TAP version 13\\n1..0\\n' ;;
  sleep) sleep 2 ;;
esac
""", encoding="utf-8")
        stub.chmod(0o755)
        for mode, rule in (("pass", "cocos:pass"), ("todo", "cocos:pass"),
                           ("cancel", "cocos:test-fail"), ("fail", "cocos:test-fail"),
                           ("zero", "zero-tests")):
            result = self.invoke("cocos", "--cmd", f"bash tap-stub.sh {mode}", "--timeout", "1")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("rule\t" + rule, result.stdout)
        timed = self.invoke("cocos", "--cmd", "bash tap-stub.sh sleep", "--timeout", "1")
        self.assertIn("rule\ttimeout", timed.stdout)

    def test_node_summary_rejects_plan_only_incomplete_and_nested(self):
        adapter = REPO / ".agents/studio/scripts/cocos-run.py"
        code = "import importlib.util; s=importlib.util.spec_from_file_location('c', r'%s'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)"
        script = code % adapter
        for text in (
            "TAP version 13\n1..2\n",
            "TAP version 13\n1..2\nok 1 - only\n",
            "TAP version 13\n1..1\nok 1 - inner\n1..1\nok 1 - outer\n",
            "TAP version 13\nBail out! broken\n",
        ):
            result = subprocess.run([os.sys.executable, "-c", script + "; print(m.parse_tap(" + repr(text) + "))"],
                                    text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertIn("'recognized': False", result.stdout)

    def test_all_skip_and_todo_are_not_pass(self):
        adapter = REPO / ".agents/studio/scripts/cocos-run.py"
        source = adapter.read_text(encoding="utf-8")
        self.assertIn("executed", source)
        (self.root / "tap-stub.sh").write_text(
            "#!/usr/bin/env bash\nprintf 'TAP version 13\\n1..1\\nok 1 - unavailable # SKIP\\n'\n",
            encoding="utf-8")
        (self.root / "tap-stub.sh").chmod(0o755)
        result = self.invoke("cocos", "--cmd", "bash tap-stub.sh skip")
        self.assertIn("rule\tzero-tests", result.stdout)

    def test_explicit_stale_report_cannot_be_rescued_by_stdout(self):
        report = self.root / "stale.tap"
        report.write_text("TAP version 13\n# tests 1\n# pass 1\n# fail 0\n# cancelled 0\n# skipped 0\n# todo 0\n1..1\n", encoding="utf-8")
        old = report.stat().st_mtime - 120
        os.utime(report, (old, old))
        adapter = REPO / ".agents/studio/scripts/cocos-run.py"
        result = subprocess.run([os.sys.executable, "-X", "utf8", str(adapter), "test", "--root", str(self.root),
                                 "--cmd", "printf TAP", "--report", "stale.tap"],
                                text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertIn("rule\tmissing-report", result.stdout)

    def test_build_reports_fresh_web_artifact_but_runtime_unassessed(self):
        adapter = REPO / ".agents/studio/scripts/cocos-run.py"
        out = self.root / "build/web-mobile"
        executable = subprocess.list2cmdline([os.sys.executable]) if os.name == "nt" else shlex.quote(os.sys.executable)
        command = executable + " -X utf8 -c \"from pathlib import Path; p=Path('build/web-mobile'); p.mkdir(parents=True,exist_ok=True); (p/'index.html').write_text('<html></html>')\""
        result = subprocess.run([os.sys.executable, "-X", "utf8", str(adapter), "build", "--root", str(self.root),
                                 "--cmd", command, "--output", "build/web-mobile"],
                                text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertIn("build_result\tPASS", result.stdout)
        self.assertIn("build_web_entry\tyes", result.stdout)
        self.assertIn("build_runtime\tNOT ASSESSED", result.stdout)

    def test_timeout_kills_child_tree_without_late_marker(self):
        adapter = REPO / ".agents/studio/scripts/cocos-run.py"
        spec = __import__("importlib.util").util.spec_from_file_location("cocos_run", adapter)
        module = __import__("importlib.util").util.module_from_spec(spec)
        spec.loader.exec_module(module)
        started = time.monotonic()
        code, output, timed, _ = module._run(
            f"{os.sys.executable} -c \"import signal,time; signal.signal(signal.SIGTERM,lambda *_: None); time.sleep(2); print('late-marker')\"",
            self.root, 1)
        self.assertTrue(timed)
        self.assertEqual(code, 124)
        self.assertNotIn("late-marker", output)
        self.assertLess(time.monotonic() - started, 7)

    def test_tap_indices_and_summary_contradictions_are_rejected(self):
        adapter = REPO / ".agents/studio/scripts/cocos-run.py"
        spec = __import__("importlib.util").util.spec_from_file_location("cocos_run", adapter)
        module = __import__("importlib.util").util.module_from_spec(spec)
        spec.loader.exec_module(module)
        duplicate = "TAP version 13\nok 1 - a\nok 1 - b\n1..2\n"
        contradiction = "TAP version 13\nok 1 - a\nnot ok 2 - b\n1..2\n# tests 2\n# pass 1\n# fail 0\n# cancelled 0\n# skipped 0\n# todo 0\n"
        self.assertFalse(module.parse_tap(duplicate)["recognized"])
        self.assertFalse(module.parse_tap(contradiction)["recognized"])

    def test_captured_node_nested_leaf_summary_counts_without_suite_double_count(self):
        adapter = REPO / ".agents/studio/scripts/cocos-run.py"
        spec = __import__("importlib.util").util.spec_from_file_location("cocos_run", adapter)
        module = __import__("importlib.util").util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Genuine Node v24.14.0 output, with mixed depths, suites, a parent
        # test, and a skip. The generator is retained next to the report.
        nested = (Path(__file__).parent / "fixtures/node24-nested.tap").read_text(encoding="utf-8")
        parsed = module.parse_tap(nested)
        self.assertTrue(parsed["recognized"])
        self.assertEqual((parsed["total"], parsed["passed"], parsed["skipped"]), (6, 5, 1))

    def test_stale_web_entry_cannot_pass_from_fresh_unrelated_file(self):
        adapter = REPO / ".agents/studio/scripts/cocos-run.py"
        out = self.root / "stale-web"
        out.mkdir()
        entry = out / "index.html"
        entry.write_text("old", encoding="utf-8")
        old = entry.stat().st_mtime - 120
        os.utime(entry, (old, old))
        command = f"{os.sys.executable} -c \"from pathlib import Path; Path('stale-web/log.txt').write_text('fresh')\""
        result = subprocess.run([os.sys.executable, "-X", "utf8", str(adapter), "build", "--root", str(self.root),
                                 "--cmd", command, "--output", "stale-web"],
                                text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertIn("build_result\tFAIL", result.stdout)

    def test_missing_report_and_os_command_precedence(self):
        result = self.invoke("cocos", "--os", "macos", "--cmd", "true")
        self.assertIn("rule\tmissing-report", result.stdout)
        self.assertIn("command-unavailable", self.invoke("cocos", "--os", "macos", "--cmd", "").stdout)


if __name__ == "__main__":
    unittest.main()
