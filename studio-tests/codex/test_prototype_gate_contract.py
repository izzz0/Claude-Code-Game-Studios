"""Regression contract for prototype evidence gates and stage retention."""
from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".agents/skills/ccgs-prototype/SKILL.md"


class PrototypeGateContractTests(unittest.TestCase):
    def test_missing_runtime_evidence_cannot_advance_stage(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("NOT ASSESSED", text)
        self.assertIn("retain the current stage", text)
        self.assertIn("do not call `set-stage.sh`", text)
        self.assertIn("missing engine, timeout, runtime, or screenshot evidence", text)

    def test_stage_recording_is_conditional_on_a_verified_decision(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("For a verified `PROCEED`, `PIVOT`, or `KILL` result", text)
        self.assertIn("when `features.session_state` is enabled", text)
        self.assertIn("otherwise do not create session-state files", text)

    def test_native_fixture_requires_report_and_preserved_stage_without_broad_bans(self):
        catalog = json.loads(
            (ROOT / "studio-tests/native/case-parts/runtime-teams.json").read_text(
                encoding="utf-8"
            )
        )
        case = catalog["cases"][0]
        self.assertEqual(case["id"], "native-062-ccgs-prototype")
        self.assertEqual(case["expected"]["config"]["project.stage"], "Pre-Production")
        report = next(item for item in case["expected"]["files"] if item["path"].endswith("REPORT.md"))
        self.assertIn("NOT ASSESSED", report["contains"])
        self.assertIn("project.stage unchanged", report["contains"])
        self.assertNotIn("PROCEED", report["not_contains"])
        self.assertIn("Decision: PROCEED", case["expected"]["response_not_contains"])


if __name__ == "__main__":
    unittest.main()
