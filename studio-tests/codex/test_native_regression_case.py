"""Input and negative-coverage regressions for native case 022."""

import json
import shutil
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / "studio-tests/native"
FIXTURE = NATIVE / "fixtures/regression-suite"
CASE_ID = "native-022-ccgs-regression-suite"
sys.path.insert(0, str(NATIVE))
from run_acceptance import assess, tree_hashes


def load_cases(path):
    return {case["id"]: case for case in json.loads(path.read_text(encoding="utf-8"))["cases"]}


class NativeRegressionCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = load_cases(NATIVE / "cases.json")[CASE_ID]
        cls.part = load_cases(NATIVE / "case-parts/quality-release.json")["quality-022-ccgs-regression-suite"]

    def test_case_and_partition_require_truthful_missing_coverage(self):
        self.assertEqual(self.case["prompt"], self.part["prompt"])
        for key, value in self.part["expected"].items():
            if key == "files":
                self.assertEqual(self.case["expected"][key][0]["contains"], value[0]["contains"])
                self.assertEqual(self.case["expected"][key][0]["not_contains"], value[0]["not_contains"])
            elif key != "config":
                self.assertEqual(self.case["expected"][key], value)

        prompt = self.case["prompt"]
        for fact in (
            "constant-only assertions",
            "do not treat them as covering",
            "movement_wall first and collect_three_targets second",
            "BUG-0001 as MISSING REGRESSION TEST",
            "suggest a real wall-boundary regression test",
        ):
            self.assertIn(fact, prompt)

    def test_stub_fixtures_cannot_support_the_requested_coverage_claim(self):
        movement = (FIXTURE / "tests/unit/movement/test_wall_boundary.gd").read_text(encoding="utf-8")
        collection = (FIXTURE / "tests/integration/collection/test_collect_three_targets.gd").read_text(
            encoding="utf-8"
        )
        self.assertIn("assert(98 <= 100)", movement)
        self.assertIn("assert(100 == 100)", movement)
        self.assertIn("assert(3 == 3)", collection)
        self.assertIn("assert(true)", collection)

    def test_valid_missing_finding_passes_and_false_bug_coverage_or_no_gap_fails(self):
        valid_response = (
            "tests/regression-suite.md: movement_wall, collect_three_targets; "
            "BUG-0001 is MISSING REGRESSION TEST; ordered."
        )
        valid_artifact = (
            "movement_wall then collect_three_targets; tests/unit/movement/test_wall_boundary.gd; "
            "tests/integration/collection/test_collect_three_targets.gd; BUG-0001; "
            "MISSING REGRESSION TEST; ordered"
        )

        def run_assessment(artifact, response):
            with tempfile.TemporaryDirectory(dir=ROOT / "studio-tests") as temp_dir:
                sandbox = Path(temp_dir) / "fixture"
                shutil.copytree(FIXTURE, sandbox)
                output = sandbox / "tests/regression-suite.md"
                output.parent.mkdir(parents=True, exist_ok=True)
                before = tree_hashes(sandbox)
                output.write_text(artifact, encoding="utf-8")
                return assess(
                    self.case,
                    sandbox,
                    before,
                    response,
                    [{"type": "commandExecution", "status": "completed", "exitCode": 0}],
                    [{"status": "completed"}],
                    "completed",
                )

        self.assertEqual(run_assessment(valid_artifact, valid_response)["status"], "PASS")
        for false_claim in ("BUG-0001 | HAS REGRESSION TEST", "BUG-0001 | COVERED"):
            result = run_assessment(valid_artifact + "; " + false_claim, valid_response)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("forbidden" in finding for finding in result["findings"]))
        for false_claim in ("BUG-0001 has a regression test", "BUG-0001 is covered"):
            result = run_assessment(valid_artifact, valid_response + " " + false_claim)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("Forbidden response claim" in finding for finding in result["findings"]))
        result = run_assessment(valid_artifact.replace("MISSING REGRESSION TEST", ""), valid_response)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("missing MISSING REGRESSION TEST" in finding for finding in result["findings"]))


if __name__ == "__main__":
    unittest.main()
