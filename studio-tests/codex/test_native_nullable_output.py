"""Regression coverage for nullable native command output."""
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "native_acceptance_nullable", ROOT / "studio-tests/native/run_acceptance.py"
)
driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(driver)


class NullableNativeOutputTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="native nullable output ")
        self.sandbox = Path(self.tmp.name)
        (self.sandbox / "input.txt").write_text("fixture", encoding="utf-8")
        self.before = driver.tree_hashes(self.sandbox)
        self.case = {
            "readonly": True,
            "expected": {"required_tools": True, "response_contains": [], "files": []},
        }
        self.hooks = [{"status": "completed"}]

    def tearDown(self):
        self.tmp.cleanup()

    def assess(self, item, transport="completed"):
        return driver.assess(
            self.case,
            self.sandbox,
            self.before,
            "",
            [item],
            self.hooks,
            transport,
        )

    def test_completed_zero_accepts_null_missing_and_text_output(self):
        for output in (None, "", "shell inspection complete"):
            with self.subTest(output=output):
                result = self.assess(
                    {
                        "type": "commandExecution",
                        "status": "completed",
                        "exitCode": 0,
                        "aggregatedOutput": output,
                    }
                )
                self.assertEqual(result["status"], "PASS")

    def test_null_output_preserves_provisioning_and_exit_evidence(self):
        provisioning = self.assess(
            {
                "type": "commandExecution",
                "status": "failed",
                "exitCode": -1,
                "aggregatedOutput": None,
            }
        )
        self.assertEqual(provisioning["status"], "NOT ASSESSED")
        self.assertIn("sandbox", " ".join(provisioning["missing"]).lower())

        completed_nonzero = self.assess(
            {
                "type": "commandExecution",
                "status": "completed",
                "exitCode": 1,
                "aggregatedOutput": None,
            }
        )
        self.assertEqual(completed_nonzero["status"], "NOT ASSESSED")
        self.assertIn("successful native shell inspection", " ".join(completed_nonzero["missing"]))

    def test_missing_output_does_not_mask_failed_transport(self):
        result = self.assess(
            {
                "type": "commandExecution",
                "status": "completed",
                "exitCode": 0,
                # Older native event payloads omit aggregatedOutput entirely.
            },
            transport="failed",
        )
        self.assertEqual(result["status"], "NOT ASSESSED")
        self.assertTrue(result["missing"])


if __name__ == "__main__":
    unittest.main()
