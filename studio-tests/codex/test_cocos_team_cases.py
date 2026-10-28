"""Cocos team inputs are executable contracts, not native execution receipts."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / "studio-tests/native"


class CocosTeamCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = [case for case in json.loads((NATIVE / "cases.json").read_text(encoding="utf-8"))["cases"]
                     if case["skill"].startswith("ccgs-team-")]

    def test_nine_cases_resolve_the_supplied_cocos_inputs(self):
        self.assertEqual(len(self.cases), 9)
        for case in self.cases:
            with self.subTest(skill=case["skill"]):
                root = NATIVE / "fixtures" / case["fixture"]
                config = (root / "project.yaml").read_text(encoding="utf-8")
                self.assertIn("name: Cocos\n", config)
                self.assertIn("version: 3.8.8\n", config)
                self.assertIn("language: TypeScript\n", config)
                expected = case["expected"]["config"]
                self.assertEqual(expected["engine.name"], "Cocos")
                self.assertEqual(expected["engine.version"], "3.8.8")
                self.assertEqual(expected["engine.language"], "TypeScript")
                package = json.loads((root / "client/package.json").read_text(encoding="utf-8"))
                self.assertEqual(package["creator"]["version"], "3.8.8")
                script = (root / "client/assets/scripts/chase-contract.ts").read_text(encoding="utf-8")
                self.assertIn("captureDistance: 24", script)
                self.assertIn("captureHoldMs: 300", script)
                self.assertIn("durationMs: 60_000", script)
                self.assertLess(script.index("if (captured)"), script.index("elapsedMs >="))

    def test_recovery_and_missing_runtime_are_not_prefilled_as_success(self):
        for case in self.cases:
            with self.subTest(skill=case["skill"]):
                self.assertEqual(case["required_evidence"], ["native_agents", "team_recovery", "independent_review"])
                prompt = case["prompt"]
                self.assertIn("exact", prompt)
                self.assertIn("NOT ASSESSED", prompt)
                self.assertIn("design/scenario.md", prompt)
                self.assertIn("init --id takes a fresh local record slug", prompt)
                self.assertIn("event --agent-id takes the actual returned child UUID or exact host agent path", prompt)
                self.assertNotIn("fresh real coordinator ID", prompt)
                self.assertNotIn("and Godot specialist", prompt)
                scenario = (NATIVE / "fixtures" / case["fixture"] / "design/scenario.md").read_text(encoding="utf-8")
                self.assertIn("no native execution, agent identity or runtime evidence is prefilled", scenario)
                self.assertTrue((ROOT / ".agents/skills" / case["skill"] / "references/workflow.md").is_file())
                preferences = (NATIVE / "fixtures" / case["fixture"] / "docs/technical-preferences.md").read_text(encoding="utf-8")
                self.assertIn("**Primary**: ccgs-engine-programmer", preferences)
                self.assertTrue((ROOT / ".codex/agents/ccgs-engine-programmer.toml").is_file())
                self.assertTrue((NATIVE / "fixtures" / case["fixture"] / "production/team/recovery-brief.md").is_file())

    def test_parts_and_catalog_keep_the_same_team_expectations(self):
        catalog = {case["skill"]: case for case in self.cases}
        for part in ("teams-combat-ui-qa", "runtime-teams"):
            for case in json.loads((NATIVE / "case-parts" / (part + ".json")).read_text(encoding="utf-8"))["cases"]:
                if case["skill"] not in catalog:
                    continue
                actual = catalog[case["skill"]]
                self.assertEqual(actual["prompt"], case["prompt"])
                self.assertEqual(actual["expected"]["config"], case["expected"]["config"])
                for field in ("response_contains", "response_not_contains"):
                    self.assertEqual(actual["expected"][field], case["expected"][field])
                for expected, observed in zip(case["expected"]["files"], actual["expected"]["files"], strict=True):
                    for key, value in expected.items():
                        self.assertEqual(observed[key], value)

    def test_qa_and_release_check_missing_evidence_without_approval(self):
        cases = {case["fixture"]: case for case in self.cases}
        qa = cases["team-qa"]
        self.assertTrue(qa["readonly"])
        self.assertFalse(qa["files_changed"])
        smoke = (NATIVE / "fixtures/team-qa/production/qa/smoke-2026-10-26.md").read_text(encoding="utf-8")
        self.assertIn("FAIL", smoke)
        self.assertIn("Web entry index.html is missing", smoke)
        self.assertIn("do not claim a QA approval", qa["prompt"])
        release = (NATIVE / "fixtures/team-release/design/scenario.md").read_text(encoding="utf-8")
        self.assertIn("no built Web entry", release)
        self.assertIn("NOT ASSESSED", release)
        self.assertEqual(cases["team-release"]["expected"]["response_verdict_any"], ["NOT ASSESSED"])
        for spec in cases["team-release"]["expected"]["files"]:
            if any(name in spec["path"] for name in ("qa-gate", "build-", "signoff", "go-no-go")):
                self.assertIn("NOT ASSESSED", spec["contains"])
                self.assertIn("Verdict: PASS", spec["not_contains"])
        narrative = cases["team-narrative"]["prompt"]
        self.assertIn("distinct read-only ND-CONSISTENCY review", narrative)
        self.assertIn("exact complete independent review response", narrative)


if __name__ == "__main__":
    unittest.main()
