"""Regressions for native-case configuration assertions read by assess()."""

import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / "studio-tests/native"
sys.path.insert(0, str(NATIVE))
import run_acceptance


def load_cases(path):
    return {case["id"]: case for case in json.loads(path.read_text(encoding="utf-8"))["cases"]}


class NativeConfigCaseInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_cases(NATIVE / "cases.json")
        cls.parts = [
            load_cases(NATIVE / "case-parts/quality-release.json"),
            load_cases(NATIVE / "case-parts/teams-combat-ui-qa.json"),
            load_cases(NATIVE / "case-parts/utility-context.json"),
        ]

    def test_all_native_configs_are_expected_assertions_and_string_values(self):
        self.assertEqual(len(self.catalog), 74)
        for case_id, case in self.catalog.items():
            self.assertNotIn("config", case, case_id)
            if case_id not in {"native-001-ccgs-help", "native-004-ccgs-code-review"}:
                self.assertIn("config", case["expected"], case_id)
            for key, value in case.get("expected", {}).get("config", {}).items():
                self.assertIsInstance(value, str, f"{case_id}: {key}")

    def test_cases_021_to_031_match_literal_base_yaml_via_original_parser(self):
        for number in range(21, 32):
            case_id = next(case_id for case_id in self.catalog if case_id.startswith(f"native-{number:03d}-"))
            case = self.catalog[case_id]
            fixture = NATIVE / "fixtures" / case["fixture"]
            for key, expected in case["expected"]["config"].items():
                result = run_acceptance.helper(
                    fixture,
                    ".agents/studio/hooks/yaml-helper.sh",
                    "get_yaml_key",
                    str((fixture / "project.yaml").resolve()),
                    key,
                )
                self.assertEqual(result.returncode, 0, f"{case_id}: {key} parser exited nonzero")
                self.assertEqual(result.stdout.strip(), expected, f"{case_id}: {key}")

    def test_settings_case_keeps_base_collaborative_and_local_autonomous_values(self):
        case = self.catalog["native-028-ccgs-settings"]
        fixture = NATIVE / "fixtures/settings"
        base = (fixture / "project.yaml").read_text(encoding="utf-8")
        local = (fixture / "project.local.yaml").read_text(encoding="utf-8")
        self.assertEqual(case["expected"]["config"]["modes.automation"], "collaborative")
        self.assertIn("automation: collaborative", base)
        self.assertIn("automation: autonomous", local)

    def test_assess_uses_original_yaml_parser_for_engine_and_boolean_mismatches(self):
        case = copy.deepcopy(self.catalog["native-021-ccgs-test-evidence-review"])
        case["expected"] = {"files": [], "required_tools": True,
                            "config": case["expected"]["config"]}
        case["readonly"] = True
        with tempfile.TemporaryDirectory(dir=ROOT / "studio-tests") as temp_dir:
            sandbox = Path(temp_dir) / "fixture"
            shutil.copytree(NATIVE / "fixtures/test-evidence-review", sandbox)
            project = sandbox / "project.yaml"
            text = project.read_text(encoding="utf-8")
            text = text.replace("name: Godot", "name: OtherEngine", 1)
            text = text.replace("strict: true", "strict: false", 1)
            project.write_text(text, encoding="utf-8")
            before = run_acceptance.tree_hashes(sandbox)
            result = run_acceptance.assess(
                case,
                sandbox,
                before,
                "",
                [{"type": "commandExecution", "status": "completed", "exitCode": 0}],
                [{"status": "completed"}],
                "completed",
            )
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("Configuration mismatch for engine.name" in item for item in result["findings"]))
        self.assertTrue(any("Configuration mismatch for testing.strict" in item for item in result["findings"]))

    def test_partition_cases_021_to_031_match_assembled_expected_config(self):
        part_cases = {case_id: case for part in self.parts for case_id, case in part.items()}
        for number in range(21, 32):
            case_id = next(case_id for case_id in self.catalog if case_id.startswith(f"native-{number:03d}-"))
            native = self.catalog[case_id]
            suffix = case_id.replace("native-", "", 1)
            part_key = next(key for key in part_cases if key.endswith(suffix))
            self.assertEqual(native["expected"]["config"], part_cases[part_key]["expected"]["config"])
            self.assertNotIn("config", part_cases[part_key])


if __name__ == "__main__":
    unittest.main()
