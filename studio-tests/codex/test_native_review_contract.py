"""Regression coverage for native code-review semantics and evidence retention."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "native_review_acceptance", ROOT / "studio-tests/native/run_acceptance.py"
)
driver = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(driver)


class NativeReviewContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="native review contract ")
        self.sandbox = Path(self.tmp.name) / "project"
        catalog = json.loads((ROOT / "studio-tests/native/cases.json").read_text(encoding="utf-8"))
        self.case = next(row for row in catalog["cases"] if row["id"] == "native-004-ccgs-code-review")
        shutil.copytree(ROOT / "studio-tests/native/fixtures/code-review", self.sandbox)
        self.before = driver.tree_hashes(self.sandbox)
        self.items = [{"type": "commandExecution", "status": "completed", "exitCode": 0}]
        self.hooks = [{"status": "completed"}]

    def tearDown(self):
        self.tmp.cleanup()

    def assess(self, response, verified=("independent_review",)):
        evidence = {"verified": list(verified), "missing": [], "findings": []}
        if not verified:
            evidence["missing"] = ["independent_review"]
        return driver.assess(self.case, self.sandbox, self.before, response, self.items,
                             self.hooks, "completed", evidence)

    def test_recorded_native004_response_satisfies_semantic_case_contract(self):
        response = (
            "**Verdict: FAIL — route to `ccgs-dev-story`.**\n\n"
            "- **BLOCKING, AC-3:** `src/gameplay/delivery.gd:6–7` rejects index `2`, "
            "contradicting `production/epics/courier/story-001-delivery.md:12`. Supplied QA "
            "confirms the failure at `production/qa/evidence/courier-evidence.md:11`. "
            "Correct the boundary and verify indices `0`, `1`, and `2`.\n"
            "- **ADVISORY:** `delivery.gd:6–8` accepts negative indices; invalid-input behavior "
            "is unspecified.\n"
            "- **ADVISORY:** `delivery.gd:3` lacks the explicit element typing required by the "
            "specialist profile.\n\n"
            "AC-1/AC-2 agree with static inspection and supplied QA. Godot parse, executed tests "
            "and runtime compatibility remain **NOT ASSESSED**.\n\n"
            "Independent reviewer `/root/independent_delivery_review` used "
            "`ccgs-godot-gdscript-specialist`, completed the five required reads, and returned "
            "after actual interruption and same-child recovery. Returned findings, verified input "
            "hashes and matching manifest are retained under `.scratch/team-observations`.\n\n"
            "```text\nReviewed-Content-Hash: src/gameplay/delivery.gd "
            "8020f9ddea2a5f71d42ce471006513ed3136c74d\n```\n\n"
            "Source, story, QA evidence, configuration and checkpoints remain unchanged."
        )
        result = self.assess(response)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["findings"], [])

        captionless = response.replace("**Verdict: FAIL — route to `ccgs-dev-story`.**",
                                       "FAIL — route to `ccgs-dev-story`.")
        self.assertEqual(self.assess(captionless)["status"], "PASS")

    def test_wrong_target_or_vague_ac3_failure_does_not_satisfy_semantic_assertions(self):
        wrong_target = (
            "Verdict: FAIL — AC-3: delivery.gd rejects target_index == 1 for Target Beta."
        )
        vague = "Verdict: FAIL — AC-3 has a problem in delivery.gd."
        for response in (wrong_target, vague):
            with self.subTest(response=response):
                result = self.assess(response)
                self.assertEqual(result["status"], "FAIL")
                self.assertTrue(any("acceptable response alternatives" in finding
                                    for finding in result["findings"]))

    def test_concrete_ac3_finding_cannot_be_reported_as_pass(self):
        for response in (
            "Verdict: PASS — AC-3 is satisfied. delivery.gd rejects target_index == 2 "
            "even though Target Gamma is the third target.",
            "**PASS** — AC-3 is satisfied. delivery.gd rejects target_index == 2 "
            "even though Target Gamma is the third target.",
            "Supplied QA has a FAIL row for AC-3, delivery.gd, and index 2.",
        ):
            with self.subTest(response=response):
                result = self.assess(response)
                self.assertEqual(result["status"], "FAIL")
                self.assertTrue(any("First response verdict is" in finding
                                    for finding in result["findings"]))

    def test_missing_independent_review_keeps_case_unassessed(self):
        response = (
            "Verdict: FAIL — AC-3: delivery.gd rejects target_index == 2; "
            "Target Gamma is the third target."
        )
        result = self.assess(response, verified=())
        self.assertEqual(result["status"], "NOT ASSESSED")
        self.assertIn("Separate evidence required: independent_review", result["missing"])

    def test_independent_review_prompt_requires_verbatim_child_artifact(self):
        guidance = driver.INDEPENDENT_REVIEW_RETENTION_INSTRUCTION
        self.assertIn("exact complete final response verbatim", guidance)
        self.assertIn("without reformatting or paraphrasing", guidance)
        self.assertIn("hash that artifact after retention", guidance)
        self.assertIn("keep coordinator summaries separate", guidance)
        self.assertIn("only that single returned-review artifact", guidance)

    def test_skill_contract_uses_shared_gate_verdicts_and_blocks_fail_or_na(self):
        skill = (ROOT / ".agents/skills/ccgs-code-review/SKILL.md").read_text(encoding="utf-8")
        workflow = (ROOT / ".agents/skills/ccgs-code-review/references/full-workflow.md").read_text(
            encoding="utf-8"
        )
        for verdict in ("PASS", "CONCERNS", "FAIL", "NOT ASSESSED"):
            self.assertIn(verdict, skill)
            self.assertIn(verdict, workflow)
        self.assertIn("explicit acceptance", skill)
        self.assertIn("Do not route an unassessed story", skill)
        self.assertIn("Never offer `$ccgs-story-done`", workflow)
        self.assertNotIn("Run $ccgs-story-done anyway", workflow)


if __name__ == "__main__":
    unittest.main()
