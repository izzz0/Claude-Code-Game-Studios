"""Native acceptance accounting; protocol fixtures never count as host runs."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import contextlib
import io
import sys

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("native_acceptance", ROOT / "studio-tests/native/run_acceptance.py")
driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(driver)


class NativeAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="native acceptance 测试 ")
        self.root = Path(self.tmp.name)
        (self.root / "code.gd").write_text("old", encoding="utf-8")
        self.before = driver.tree_hashes(self.root)
        self.case = {"readonly": True, "expected": {"required_tools": True,
                     "response_contains": ["Target index 2 is rejected"], "files": []}}
        self.items = [{"type": "commandExecution", "status": "completed", "exitCode": 0}]
        self.hooks = [{"status": "completed"}]

    def tearDown(self):
        self.tmp.cleanup()

    def assess(self, response="Target index 2 is rejected", **kwargs):
        return driver.assess(self.case, self.root, self.before, response,
                             kwargs.get("items", self.items), kwargs.get("hooks", self.hooks), "completed")

    def test_completed_transport_does_not_mask_failed_hook_or_missing_tool(self):
        self.assertEqual(self.assess(hooks=[{"status": "failed"}])["status"], "FAIL")
        self.assertEqual(self.assess(items=[])["status"], "NOT ASSESSED")
        self.assertEqual(self.assess(response="Done")["status"], "FAIL")
        self.assertEqual(self.assess()["status"], "PASS")

    def test_host_provisioning_failure_is_not_a_skill_semantic_pass(self):
        failed = [{"type": "commandExecution", "status": "failed", "exitCode": -1,
                   "aggregatedOutput": "sandbox provisioning failed"}]
        self.assertEqual(self.assess(response="NOT ASSESSED", items=failed)["status"], "NOT ASSESSED")

    def test_readonly_and_fresh_authoring_are_enforced(self):
        (self.root / "code.gd").write_text("changed", encoding="utf-8")
        self.assertEqual(self.assess()["status"], "FAIL")
        self.case["readonly"] = False
        self.assertEqual(self.assess()["status"], "PASS")
        self.before = driver.tree_hashes(self.root)
        self.assertEqual(self.assess()["status"], "FAIL")

    def test_model_claims_do_not_supply_independent_or_rendered_evidence(self):
        self.case["required_evidence"] = ["independent_review", "rendered_input"]
        self.assertEqual(self.assess(response="Target index 2 is rejected. independent_review rendered_input PASS")["status"], "NOT ASSESSED")

    def test_repeated_story_creation_preserves_existing_file_and_total_count(self):
        self.case["readonly"] = False
        self.case["expected"]["files"] = [{"path": "code.gd", "changed": False}]
        self.case["expected"]["counts"] = [{"glob": "code*.gd", "count": 2}]
        (self.root / "code-002.gd").write_text("new story", encoding="utf-8")
        self.assertEqual(self.assess()["status"], "PASS")
        (self.root / "code-003.gd").write_text("duplicate story", encoding="utf-8")
        self.assertEqual(self.assess()["status"], "FAIL")
        (self.root / "code-003.gd").unlink()
        (self.root / "code.gd").write_text("renumbered old story", encoding="utf-8")
        self.assertEqual(self.assess()["status"], "FAIL")

    def test_setup_cannot_pass_after_losing_stage_or_unrelated_owner(self):
        (self.root / "project.yaml").write_text("project:\n  stage: Concept\nnotes:\n  owner: native-smoke\n", encoding="utf-8")
        self.case["expected"]["config"] = {"project.stage": "Concept", "notes.owner": "native-smoke"}
        self.before = driver.tree_hashes(self.root)
        self.assertEqual(self.assess()["status"], "PASS")
        (self.root / "project.yaml").write_text("engine:\n  name: Godot\n", encoding="utf-8")
        self.case["readonly"] = False
        result = self.assess()
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("project.stage" in row for row in result["findings"]))
        self.assertTrue(any("notes.owner" in row for row in result["findings"]))

    def test_resume_rejects_changed_unlisted_source_and_response(self):
        receipts = self.root / "native receipts"
        receipts.mkdir()
        response = receipts / "response.txt"
        response.write_text("review", encoding="utf-8")
        events = receipts / "events.json"
        events.write_text("[]", encoding="utf-8")
        thread = receipts / "thread.json"
        thread.write_text("{}", encoding="utf-8")
        record = {"status": "PASS", "source_fingerprint": "version", "sandbox": str(self.root),
                  "attempt": str(receipts), "response_sha256": driver.sha(response),
                  "events_sha256": driver.sha(events), "thread_sha256": driver.sha(thread),
                  "protected_hashes": driver.tree_hashes(self.root), "artifacts": {}}
        self.assertTrue(driver.can_resume(record, "version"))
        (self.root / "code.gd").write_text("new behavior", encoding="utf-8")
        self.assertFalse(driver.can_resume(record, "version"))
        self.assertFalse(driver.can_resume(record, "different version"))

    def test_resume_rejects_tampered_native_receipts_and_legacy_records(self):
        receipts = self.root / "native receipts tamper"
        receipts.mkdir()
        for name, content in (("response.txt", "review"), ("events.json", "[]"), ("thread.json", "{}")):
            (receipts / name).write_text(content, encoding="utf-8")
        record = {"status": "PASS", "source_fingerprint": "version", "sandbox": str(self.root),
                  "attempt": str(receipts), "response_sha256": driver.sha(receipts / "response.txt"),
                  "events_sha256": driver.sha(receipts / "events.json"),
                  "thread_sha256": driver.sha(receipts / "thread.json"),
                  "protected_hashes": driver.tree_hashes(self.root), "artifacts": {}}
        self.assertTrue(driver.can_resume(record, "version"))
        (receipts / "events.json").write_text('[{"tampered":true}]', encoding="utf-8")
        self.assertFalse(driver.can_resume(record, "version"))
        (receipts / "events.json").write_text("[]", encoding="utf-8")
        (receipts / "thread.json").write_text('{"tampered":true}', encoding="utf-8")
        self.assertFalse(driver.can_resume(record, "version"))
        legacy = dict(record)
        legacy.pop("events_sha256")
        legacy.pop("thread_sha256")
        self.assertFalse(driver.can_resume(legacy, "version"))

    def test_instruction_fingerprint_represents_absence_and_inherited_additions(self):
        project = self.root / "project"
        project.mkdir()
        instructions = driver.instruction_hashes(project)
        project_agents = str((project / "AGENTS.md").resolve())
        self.assertIn(project_agents, instructions)
        self.assertIsNone(instructions[project_agents])
        (project / "AGENTS.md").write_text("project rule", encoding="utf-8")
        changed = driver.instruction_hashes(project)
        self.assertNotEqual(instructions, changed)
        self.assertEqual(changed[project_agents], driver.sha(project / "AGENTS.md"))

    def test_case_resources_copy_role_profiles_without_hook_or_global_config(self):
        project = self.root / "source"
        sandbox = self.root / "sandbox"
        (project / ".agents/studio").mkdir(parents=True)
        (project / ".agents/studio/runtime.py").write_text("framework", encoding="utf-8")
        (project / ".codex/agents").mkdir(parents=True)
        (project / ".codex/agents/ccgs-test.toml").write_text("role", encoding="utf-8")
        (project / ".codex/hooks.json").parent.mkdir(exist_ok=True)
        (project / ".codex/hooks.json").write_text("hooks", encoding="utf-8")
        sandbox.mkdir()
        driver.copy_case_resources(project, sandbox)
        self.assertTrue((sandbox / ".codex/agents/ccgs-test.toml").is_file())
        self.assertFalse((sandbox / ".codex/hooks.json").exists())

    def test_catalog_coverage_reports_missing_cases_and_all_authored_cases_have_tools(self):
        catalog = json.loads((ROOT / "studio-tests/native/cases.json").read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "studio-tests/migration-manifest.json").read_text(encoding="utf-8"))
        required = {r["name"] for r in manifest["skills"]}
        authored = {r["skill"] for r in catalog["cases"]}
        self.assertEqual(len(authored), len(catalog["cases"]))
        self.assertEqual(len({r["id"] for r in catalog["cases"]}), len(catalog["cases"]))
        self.assertTrue(authored <= required)
        for case in catalog["cases"]:
            self.assertTrue(case["expected"]["required_tools"])
            self.assertTrue((ROOT / "studio-tests/native/fixtures" / case["fixture"] / "project.yaml").is_file())
        self.assertEqual(len(required), 74)

    def test_only_exact_project_source_and_trusted_current_hooks_pass_preflight(self):
        path = self.root / ".codex/hooks.json"
        path.parent.mkdir()
        path.write_text(json.dumps({"hooks": {"SessionStart": [], "Stop": []}}), encoding="utf-8")
        listing = {"data": [{"hooks": [{"sourcePath": str(path), "eventName": name,
                     "enabled": True, "trustStatus": "trusted"} for name in ("sessionStart", "stop")]}]}
        self.assertEqual(driver.check_hooks(listing, self.root), [])
        listing["data"][0]["hooks"][0]["trustStatus"] = "needsReview"
        self.assertTrue(driver.check_hooks(listing, self.root))
        listing["data"][0]["hooks"] = []
        self.assertTrue(driver.check_hooks(listing, self.root))

    def test_preflight_failure_and_attention_replace_prior_pass_summary(self):
        (self.root / ".git").mkdir()
        (self.root / ".codex").mkdir()
        (self.root / ".codex/hooks.json").write_text('{"hooks":{"Stop":[]}}', encoding="utf-8")
        output = self.root / ".scratch/driver"
        output.mkdir(parents=True)
        for attention in (False, True):
            (output / "summary.json").write_text('{"selected_result":"PASS"}', encoding="utf-8")
            class FixtureClient:
                def __init__(self, *args):
                    pass
                def request(self, method, params):
                    if method == "hooks/list" and attention:
                        raise driver.Attention("fixture host unavailable")
                    return {"data": []}
                def close(self):
                    pass
                def notify(self, method):
                    pass
            with patch.object(driver, "Client", FixtureClient), patch.object(
                    driver.subprocess, "check_output", return_value="fixture-version"), contextlib.redirect_stdout(io.StringIO()):
                code = driver.main(["--project", str(self.root), "--codex", sys.executable,
                                    "--output", str(output)])
            self.assertEqual(code, 2)
            summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["selected_result"], "NOT ASSESSED")

    def test_inspection_preserves_existing_batch_state_and_acceptance_summary(self):
        (self.root / ".git").mkdir()
        (self.root / ".codex").mkdir()
        source = self.root / ".codex/hooks.json"
        source.write_text('{"hooks":{"Stop":[]}}', encoding="utf-8")
        output = self.root / ".scratch/driver"
        output.mkdir(parents=True)
        saved = {"state.json": '{"cases":{"earlier":{"status":"PASS"}}}',
                 "summary.json": '{"selected_result":"PASS"}'}
        for name, text in saved.items():
            (output / name).write_text(text, encoding="utf-8")
        for trusted in (True, False):
            class FixtureClient:
                def __init__(self, *args):
                    pass
                def request(self, method, params):
                    if method == "hooks/list":
                        return {"data": [{"hooks": [{"sourcePath": str(source), "eventName": "stop",
                                  "enabled": True, "trustStatus": "trusted" if trusted else "modified"}]}]}
                    return {}
                def notify(self, method):
                    pass
                def close(self):
                    pass
            with patch.object(driver, "Client", FixtureClient), patch.object(
                    driver.subprocess, "check_output", return_value="fixture-version"), contextlib.redirect_stdout(io.StringIO()):
                code = driver.main(["--project", str(self.root), "--codex", sys.executable,
                                    "--output", str(output), "--inspect"])
            self.assertEqual(code, 0 if trusted else 2)
            for name, text in saved.items():
                self.assertEqual((output / name).read_text(encoding="utf-8"), text)
            self.assertTrue((output / "inspection.json").is_file())
            inspection = json.loads((output / "inspection.json").read_text(encoding="utf-8"))
            self.assertEqual(inspection.get("hooks") == "trusted", trusted)


if __name__ == "__main__":
    unittest.main()
