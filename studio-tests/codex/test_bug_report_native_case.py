"""Semantic regressions for native case 005 using sanitized captured artifacts."""

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
DRIVER_SPEC = importlib.util.spec_from_file_location(
    "native_acceptance_case005", ROOT / "studio-tests/native/run_acceptance.py"
)
driver = importlib.util.module_from_spec(DRIVER_SPEC)
DRIVER_SPEC.loader.exec_module(driver)
FIXTURES = ROOT / "studio-tests/codex/fixtures/native-bug-report"
REPORT_PATH = "production/qa/bugs/BUG-0001.md"


class BugReportNativeCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog = json.loads((ROOT / "studio-tests/native/cases.json").read_text(encoding="utf-8"))
        cls.case = next(item for item in catalog["cases"] if item["id"] == "native-005-ccgs-bug-report")
        part = json.loads((ROOT / "studio-tests/native/case-parts/design-quality.json").read_text(encoding="utf-8"))
        cls.part_case = next(item for item in part["cases"] if item["id"] == cls.case["id"])
        cls.report = (FIXTURES / "BUG-0001.md").read_text(encoding="utf-8")
        cls.response = (FIXTURES / "response.txt").read_text(encoding="utf-8")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="bug report case 005 ")
        self.addCleanup(self.temp.cleanup)
        self.sandbox = Path(self.temp.name) / "project"
        self.reset_sandbox()

    def reset_sandbox(self):
        if self.sandbox.exists():
            shutil.rmtree(self.sandbox)
        shutil.copytree(ROOT / "studio-tests/native/fixtures/bug-report", self.sandbox)
        hooks = self.sandbox / ".agents/studio/hooks"
        hooks.mkdir(parents=True)
        shutil.copy2(ROOT / ".agents/studio/hooks/yaml-helper.sh", hooks / "yaml-helper.sh")

    def assess(self, report=None, response=None, source=None, duplicate=False, native_inputs=False):
        self.reset_sandbox()
        case = copy.deepcopy(self.case)
        if not native_inputs:
            # Exercise artifact semantics only. The test intentionally lacks
            # native host/tool observations and must never mint a native PASS.
            case["expected"]["config"] = {}
            case["expected"]["required_tools"] = False
        before = driver.tree_hashes(self.sandbox)
        path = driver.safe_path(self.sandbox, REPORT_PATH)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.report if report is None else report, encoding="utf-8")
        if duplicate:
            path.with_name("BUG-0002.md").write_text("duplicate", encoding="utf-8")
        if source is not None:
            (self.sandbox / "src/game.gd").write_text(source, encoding="utf-8")
        hooks = [{"status": "completed"}]
        result = driver.assess(
            case, self.sandbox, before,
            self.response if response is None else response,
            [], hooks, "completed",
        )
        return result

    def test_captured_report_and_response_pass_semantics_without_native_pass(self):
        part_expected = copy.deepcopy(self.part_case["expected"])
        part_expected["config"] = self.part_case["config"]
        self.assertEqual(self.case["expected"], part_expected)
        self.assertIsNone(self.case["fixture_stdout"])
        self.assertIsNone(self.case["actual_result_stub"])
        self.assertTrue(self.case["expected_native_until_run"])
        result = self.assess(native_inputs=True)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["status"], "NOT ASSESSED")
        self.assertTrue(result["missing"])
        self.assertIn(REPORT_PATH, result["artifacts"])

    def test_report_identity_severity_priority_and_open_status_are_required(self):
        cases = (
            (self.report.replace("**ID**: BUG-0001", "**ID**: BUG-0002"), "missing **ID**: BUG-0001"),
            (self.report.replace("**Severity**: S2-High", "**Severity**: S1-Critical"), "missing **Severity**: S2-High"),
            (self.report.replace("**Priority**: P1-Fix this sprint", "**Priority**: P3-Backlog"), "missing **Priority**: P1-Fix this sprint"),
            (self.report.replace("**Status**: Open", "**Status**: Closed"), "forbidden **Status**: Closed"),
            (self.report.replace("**Status**: Open", "Status: Open"), "missing **Status**: Open"),
        )
        for report, finding in cases:
            with self.subTest(finding=finding):
                result = self.assess(report=report)
                self.assertEqual(result["status"], "FAIL")
                self.assertTrue(any(finding in item for item in result["findings"]))

    def test_reproduction_results_and_next_triage_must_be_in_report(self):
        cases = (
            (self.report.replace("## Reproduction Steps", "## Steps"), "missing ## Reproduction Steps"),
            (self.report.replace("**Expected Result**:", "**Expected**:"), "missing **Expected Result**:"),
            (self.report.replace("**Actual Result**:", "**Actual**:"), "missing **Actual Result**:"),
            (self.report.replace("$ccgs-bug-triage", "$ccgs-settings"), "missing $ccgs-bug-triage"),
        )
        for report, finding in cases:
            with self.subTest(finding=finding):
                result = self.assess(report=report)
                self.assertEqual(result["status"], "FAIL")
                self.assertTrue(any(finding in item for item in result["findings"]))

    def test_exactly_one_report_and_unchanged_source_are_required(self):
        duplicate = self.assess(duplicate=True)
        self.assertEqual(duplicate["status"], "FAIL")
        self.assertTrue(any("expected 1 files, found 2" in item for item in duplicate["findings"]))
        original_source = (self.sandbox / "src/game.gd").read_text(encoding="utf-8")
        patched_source = self.assess(source=original_source + "\n# Fix applied\n")
        self.assertEqual(patched_source["status"], "FAIL")
        self.assertTrue(any("Preserved artifact changed: src/game.gd" in item
                            for item in patched_source["findings"]))


if __name__ == "__main__":
    unittest.main()
