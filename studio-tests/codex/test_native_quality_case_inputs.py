"""Input-completeness regressions for native cases 008 and 010–012."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / "studio-tests/native"
FIXTURES = NATIVE / "fixtures"


def load_cases(path):
    return {case["id"]: case for case in json.loads(path.read_text(encoding="utf-8"))["cases"]}


class NativeQualityCaseInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_cases(NATIVE / "cases.json")
        cls.design_quality = load_cases(NATIVE / "case-parts/design-quality.json")
        cls.qa_management = load_cases(NATIVE / "case-parts/qa-management.json")

    def assert_catalog_matches_part(self, case_id, part_case):
        case = self.catalog[case_id]
        runner_suffixes = {
            "native-010-ccgs-bug-triage": " Write the explicitly requested output path(s): production/qa/bug-triage-2026-10-26.md. Any date in these filenames is the fixed scenario date, not a claim about the current run timestamp.",
            "native-011-ccgs-tech-debt": " Write the explicitly requested output path(s): docs/tech-debt-register.md. Any date in these filenames is the fixed scenario date, not a claim about the current run timestamp.",
            "native-012-ccgs-test-flakiness": " Write the explicitly requested output path(s): production/qa/flakiness-report-2026-10-26.md. Any date in these filenames is the fixed scenario date, not a claim about the current run timestamp.",
        }
        self.assertEqual(case["prompt"], part_case["prompt"] + runner_suffixes.get(case_id, ""))
        for key, value in part_case["expected"].items():
            if key == "config":
                continue
            if key == "files":
                actual_files = {item["path"]: item for item in case["expected"]["files"]}
                for file_check in value:
                    actual = actual_files[file_check["path"]]
                    for field in ("contains", "not_contains"):
                        if field in file_check:
                            self.assertEqual(actual[field], file_check[field], f"{case_id}: {field}")
            else:
                self.assertEqual(case["expected"][key], value, f"{case_id}: {key}")

    def test_consistency_case_has_authoritative_value_and_deterministic_correction(self):
        case_id = "native-008-ccgs-consistency-check"
        case = self.design_quality[case_id]
        fixture = FIXTURES / "consistency-check"
        registry = (fixture / "design/registry/entities.yaml").read_text(encoding="utf-8")
        source_gdd = (fixture / "design/gdd/player.md").read_text(encoding="utf-8")
        conflicting_gdd = (fixture / "design/gdd/combat.md").read_text(encoding="utf-8")
        self.assertIn("source: design/gdd/player.md", registry)
        self.assertIn("health: 120", registry)
        self.assertIn("120 HP", source_gdd)
        self.assertIn("80 HP", conflicting_gdd)
        self.assertIn("propose updating combat.md from 80 HP to 120 HP", case["prompt"])
        self.assertTrue(any("120 HP" in item for item in case["expected"]["response_contains"]))
        self.assertTrue(any("registry updated" in item for item in case["expected"]["response_not_contains"]))
        self.assert_catalog_matches_part(case_id, case)

    def test_bug_triage_case_has_capacity_for_required_p1_assignment(self):
        case_id = "native-010-ccgs-bug-triage"
        case = self.qa_management[case_id]
        sprint = (FIXTURES / "bug-triage/production/sprints/sprint-004.md").read_text(encoding="utf-8")
        self.assertIn("3 engineers", sprint)
        self.assertIn("2 assigned", sprint)
        self.assertIn("1 available for a P1 bug", sprint)
        self.assertIn("assigned to the documented remaining sprint capacity", case["prompt"])
        self.assertIn("Sprint 004", case["expected"]["files"][0]["contains"])
        self.assertTrue(any("BUG-0003 | Open" in item for item in case["expected"]["files"][0]["not_contains"]))
        self.assert_catalog_matches_part(case_id, case)

    def test_tech_debt_case_supplies_the_reason_required_for_register_entry(self):
        case_id = "native-011-ccgs-tech-debt"
        case = self.qa_management[case_id]
        rationale = (FIXTURES / "tech-debt/docs/debt-acceptance-context.md").read_text(encoding="utf-8")
        self.assertIn("deferred until profiling can confirm its", rationale)
        self.assertIn("impact", rationale)
        self.assertIn("docs/debt-acceptance-context.md", case["prompt"])
        self.assertIn("deferred until profiling", case["expected"]["files"][0]["contains"])
        self.assertTrue(any("src/game.gd modified" in item for item in case["expected"]["files"][0]["not_contains"]))
        self.assert_catalog_matches_part(case_id, case)

    def test_flakiness_case_proves_runs_share_source_revision_and_keeps_negative_gates(self):
        case_id = "native-012-ccgs-test-flakiness"
        case = self.qa_management[case_id]
        fixture = FIXTURES / "test-flakiness"
        provenance = (fixture / "test-results/history-provenance.md").read_text(encoding="utf-8")
        self.assertIn("fixture-revision-7f3a21c", provenance)
        self.assertIn("No source files changed between those runs", provenance)
        self.assertIn("history-provenance.md", case["prompt"])
        expected = case["expected"]
        self.assertIn("fixture-revision-7f3a21c", expected["files"][0]["contains"])
        self.assertIn("no current-game execution", expected["response_contains"])
        self.assertTrue(any("quarantined" in item for item in expected["files"][0]["not_contains"]))
        self.assertTrue(any("current game PASS" in item for item in expected["response_not_contains"]))
        self.assert_catalog_matches_part(case_id, case)

    def test_ui_recovery_targets_the_art_director_design_task_and_keeps_accessibility_review_read_only(self):
        case_id = "native-026-ccgs-team-ui"
        case = self.catalog[case_id]
        part = load_cases(NATIVE / "case-parts/teams-combat-ui-qa.json")["team-026-ccgs-team-ui"]
        prompt = case["prompt"]
        brief = (FIXTURES / "team-ui/production/team/recovery-brief.md").read_text(encoding="utf-8")
        self.assertEqual(prompt, part["prompt"])
        self.assertIn("ccgs-art-director", prompt)
        self.assertIn("Interrupt or fail the real art-direction task", prompt)
        self.assertIn("resume that exact returned task", prompt)
        self.assertIn("production/ui/courier-hud/visual-design.md", prompt)
        self.assertIn("dependent read-only ccgs-accessibility-specialist review", prompt)
        self.assertIn("ccgs-art-director design task", brief)
        self.assertIn("interrupt the art-direction task", brief)
        self.assertIn("dependent read-only accessibility review", brief)
        self.assertNotIn("interrupt the implementation task", brief)
        self.assertEqual(case["required_evidence"], ["native_agents", "team_recovery"])
        self.assertEqual(case["expected"]["files"][0]["path"], "production/ui/courier-hud/visual-design.md")
        self.assertIn("fake-agent", case["expected"]["files"][0]["not_contains"])
        self.assertIn("runtime PASS", case["expected"]["response_not_contains"])


if __name__ == "__main__":
    unittest.main()
