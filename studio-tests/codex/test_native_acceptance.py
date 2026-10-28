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
import shutil

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

    def test_final_review_bundle_includes_new_and_replaces_changed_outputs(self):
        initial = {"code.gd": {"sha256": self.before["code.gd"], "content": "old"}}
        (self.root / "code.gd").write_text("updated", encoding="utf-8")
        (self.root / "draft.md").write_text("new deliverable", encoding="utf-8")
        case = {"expected": {"files": [{"path": "code.gd", "changed": True}, {"path": "draft.md"}]}}
        bundle, missing = driver.final_review_inputs(case, self.root, self.before, initial)
        self.assertEqual(missing, [])
        self.assertEqual(bundle["code.gd"], {"sha256": driver.sha(self.root / "code.gd"), "content": "updated"})
        self.assertEqual(bundle["draft.md"], {"sha256": driver.sha(self.root / "draft.md"), "content": "new deliverable"})
        self.assertEqual(initial["code.gd"]["content"], "old")

    def test_final_review_missing_or_unreadable_outputs_cannot_be_omitted(self):
        (self.root / "binary.md").write_bytes(b"\xff\xfe")
        case = {"expected": {"files": [{"path": "missing.md", "changed": True}, {"path": "binary.md"}]}}
        _, missing = driver.final_review_inputs(case, self.root, self.before, {})
        self.assertEqual(missing, ["missing.md", "binary.md"])
        readonly = {"expected": {"files": [{"path": "code.gd", "changed": False}]}}
        initial = {"code.gd": {"sha256": self.before["code.gd"], "content": "old"}}
        self.assertEqual(driver.final_review_inputs(readonly, self.root, self.before, initial), (initial, []))

    def test_qa_response_wording_does_not_replace_actual_readonly_and_native_guards(self):
        # Protocol-only supplied evidence; this is not a new native case result.
        fixture = ROOT / "studio-tests/native/fixtures/team-qa"
        shutil.copytree(fixture, self.root, dirs_exist_ok=True)
        driver.copy_case_resources(ROOT, self.root)
        cases = json.loads((ROOT / "studio-tests/native/cases.json").read_text(encoding="utf-8"))["cases"]
        case = next(case for case in cases if case["skill"] == "ccgs-team-qa")
        before = driver.tree_hashes(self.root)
        response = (ROOT / "studio-tests/codex/fixtures/native-cocos-qa-blocked.md").read_text(encoding="utf-8")
        self.assertNotIn("read-only", response)
        evidence = {"verified": case["required_evidence"], "findings": []}
        result = driver.assess(case, self.root, before, response, self.items, self.hooks, "completed", evidence)
        self.assertEqual(result["status"], "PASS", result)
        unproven = driver.assess(case, self.root, before, response, self.items, self.hooks, "completed")
        self.assertEqual(unproven["status"], "NOT ASSESSED")
        (self.root / "code.gd").write_text("unauthorized mutation", encoding="utf-8")
        changed = driver.assess(case, self.root, before, response, self.items, self.hooks, "completed", evidence)
        self.assertEqual(changed["status"], "FAIL")

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

    def test_failed_turn_skips_unassessed_content_but_keeps_protection_failures(self):
        result = driver.assess(self.case, self.root, self.before, "", [], self.hooks, "failed")
        self.assertEqual(result["status"], "NOT ASSESSED")
        self.assertEqual(result["findings"], [])
        self.assertTrue(result["missing"])
        (self.root / "code.gd").write_text("unexpected write", encoding="utf-8")
        result = driver.assess(self.case, self.root, self.before, "", [], self.hooks, "failed")
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("Read-only case changed protected sandbox files.", result["findings"])

    def test_failed_native_run_retains_terminal_host_error(self):
        error = {"message": "Selected model is at capacity. Please try a different model.",
                 "codexErrorInfo": "serverOverloaded"}
        class FixtureClient:
            def __init__(self):
                self.events = []
            def request(self, method, params):
                if method == "thread/start":
                    return {"thread": {"id": "fixture-capacity"}, "model": "fixture"}
                self.completed = {"method": "turn/completed", "params": {"threadId": "fixture-capacity",
                                  "turn": {"status": "failed", "error": error}}}
                self.events.append(self.completed)
                return {}
            def receive(self, timeout):
                return self.completed
        catalog = json.loads((ROOT / "studio-tests/native/cases.json").read_text(encoding="utf-8"))
        case = next(row for row in catalog["cases"] if row["skill"] == "ccgs-help")
        result = driver.run_case(FixtureClient(), ROOT, self.root / "output", case, 10)
        self.assertEqual(result["status"], "NOT ASSESSED")
        self.assertEqual(result["native_error"], error)
        self.assertEqual(result["findings"], [])
        self.assertTrue(any(error["message"] in line for line in result["missing"]))
        saved = json.loads((Path(result["attempt"]) / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["native_error"]["codexErrorInfo"], "serverOverloaded")

    def test_readonly_and_fresh_authoring_are_enforced(self):
        (self.root / "code.gd").write_text("changed", encoding="utf-8")
        self.assertEqual(self.assess()["status"], "FAIL")
        self.case["readonly"] = False
        self.assertEqual(self.assess()["status"], "PASS")
        self.before = driver.tree_hashes(self.root)
        self.assertEqual(self.assess()["status"], "FAIL")

    def test_project_authoring_never_rewrites_framework_templates(self):
        template = self.root / ".agents/studio/docs/technical-preferences.md"
        template.parent.mkdir(parents=True)
        template.write_text("read-only template", encoding="utf-8")
        self.before = driver.tree_hashes(self.root)
        self.case["readonly"] = False
        preferences = self.root / "docs/technical-preferences.md"
        preferences.parent.mkdir()
        preferences.write_text("Godot 4.6.1", encoding="utf-8")
        self.assertEqual(self.assess()["status"], "PASS")
        template.write_text("rewritten", encoding="utf-8")
        result = self.assess()
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("Framework resources changed" in x for x in result["findings"]))

    def test_model_claims_do_not_supply_independent_or_rendered_evidence(self):
        self.case["required_evidence"] = ["independent_review", "rendered_input"]
        self.assertEqual(self.assess(response="Target index 2 is rejected. independent_review rendered_input PASS")["status"], "NOT ASSESSED")

    def test_help_checks_actual_state_and_next_step_without_requiring_a_heading(self):
        catalog = json.loads((ROOT / "studio-tests/native/cases.json").read_text(encoding="utf-8"))
        self.case = next(row for row in catalog["cases"] if row["skill"] == "ccgs-help")
        fixture = ROOT / "studio-tests/native/fixtures/help/project.yaml"
        (self.root / "project.yaml").write_bytes(fixture.read_bytes())
        driver.copy_case_resources(ROOT, self.root)
        self.before = driver.tree_hashes(self.root)
        response = ("Next step: $ccgs-setup-engine. The configuration is minimal, guided, "
                    "stage Concept; engine ABSENT. COMPLETE — navigation identified.")
        self.assertEqual(self.assess(response=response)["status"], "PASS")
        captured = (ROOT / "studio-tests/codex/fixtures/native-help-bold-inventory.md").read_text(encoding="utf-8")
        self.assertEqual(self.assess(response=captured)["status"], "PASS")
        for title in ("### Also installed (not in workflow)", "**Also installed (not in workflow)**",
                      "__Also installed (not in workflow)__", "### **Also installed (not in workflow)**",
                      "### Also installed (not in workflow) ###", "**Also installed (not in workflow):**",
                      "**Also installed (not in workflow)**:"):
            inventory = f"\n{title}\n\n- `$ccgs-onboard` — Project orientation notes\n"
            with self.subTest(title=title):
                self.assertEqual(self.assess(response=response + inventory)["status"], "PASS")
                for suffix in ("Also run `$ccgs-dev-story` now.",
                               "- `$ccgs-settings` — Also run `$ccgs-dev-story` now.",
                               "Next task:\n- `$ccgs-dev-story` — Implement the story",
                               "**Next task**\n- `$ccgs-dev-story` — Implement the story",
                               "## Next task\n- `$ccgs-dev-story` — Implement the story"):
                    self.assertEqual(self.assess(response=response + inventory + suffix)["status"], "FAIL")
                self.assertEqual(self.assess(response=response + " Also run `$ccgs-dev-story` now.\n" + inventory)["status"], "FAIL")
        self.assertEqual(self.assess(response=response + "\n**Also installed: run `$ccgs-dev-story` now**")["status"], "FAIL")
        for wrong in (response.replace("$ccgs-setup-engine", "$ccgs-dev-story"),
                      response.replace("minimal", "full"),
                      response.replace("Concept", "Production"),
                      response.replace("ABSENT", "PRESENT"),
                      response + " The engine configured successfully.",
                      response + " Also run `$ccgs-dev-story` now.",
                      response + inventory + "Also run `$ccgs-dev-story` now."):
            with self.subTest(response=wrong):
                self.assertEqual(self.assess(response=wrong)["status"], "FAIL")
        self.assertEqual(self.assess(response=response, items=[])["status"], "NOT ASSESSED")

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

    def test_start_checks_preserved_identity_in_config_without_a_display_name_literal(self):
        catalog = json.loads((ROOT / "studio-tests/native/cases.json").read_text(encoding="utf-8"))
        self.case = next(row for row in catalog["cases"] if row["skill"] == "ccgs-start")
        fixture = ROOT / "studio-tests/native/fixtures/start/project.yaml"
        original = fixture.read_text(encoding="utf-8")
        target = self.root / "project.yaml"
        target.write_text(original, encoding="utf-8")
        self.before = driver.tree_hashes(self.root)
        response = (ROOT / "studio-tests/codex/fixtures/native-start-preserved-settings.md").read_text(encoding="utf-8")
        self.assertNotIn("Velocity Courier", response)
        self.assertEqual(self.assess(response=response)["status"], "PASS")
        for wrong in (response.replace("$ccgs-setup-engine", "$ccgs-dev-story"),
                      response.replace("minimal", "full"), response.replace("guided", "autonomous"),
                      response.replace("Concept", "Production"), response + " The engine selected successfully.",
                      response + " Also run `$ccgs-dev-story` now."):
            self.assertEqual(self.assess(response=wrong)["status"], "FAIL")
        for old, new in (("Velocity Courier Start", "Another Project"), ("stage: Concept", "stage: Production"),
                         ("rigor: minimal", "rigor: full"), ("automation: guided", "automation: autonomous")):
            target.write_text(original.replace(old, new), encoding="utf-8")
            # Even if a caller supplied a fresh snapshot, exact config readback
            # must reject the wrong project or changed settings independently.
            self.before = driver.tree_hashes(self.root)
            result = self.assess(response=response)
            self.assertEqual(result["status"], "FAIL")
            self.assertTrue(any("Configuration mismatch" in row for row in result["findings"]))
        target.write_text(original, encoding="utf-8")
        self.before = driver.tree_hashes(self.root)
        self.assertEqual(self.assess(response=response, items=[])["status"], "NOT ASSESSED")
        (self.root / "code.gd").write_text("unexpected write", encoding="utf-8")
        self.assertEqual(self.assess(response=response)["status"], "FAIL")

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

    def test_setup_checks_identity_in_actual_config_not_repeated_response_name(self):
        catalog = json.loads((ROOT / "studio-tests/native/cases.json").read_text(encoding="utf-8"))
        self.case = next(c for c in catalog["cases"] if c["skill"] == "ccgs-setup-engine")
        target = self.root / "project.yaml"
        target.write_bytes((ROOT / "studio-tests/native/fixtures/setup-engine/project.yaml").read_bytes())
        self.before = driver.tree_hashes(self.root)
        configured = (ROOT / "studio-tests/codex/fixtures/native-setup-project.yaml").read_text(encoding="utf-8")
        response = (ROOT / "studio-tests/codex/fixtures/native-setup-configured.md").read_text(encoding="utf-8")
        self.assertNotIn("Preserve This Project Name", response)
        target.write_text(configured, encoding="utf-8")
        self.assertEqual(self.assess(response=response)["status"], "PASS")
        for old, new in (("Preserve This Project Name", "Wrong Project"),
                         ("stage: Concept", "stage: Production"),
                         ("owner: native-smoke", "owner: unrelated"),
                         ("language: GDScript", "language: CSharp")):
            with self.subTest(field=old):
                self.assertIn(old, configured)
                target.write_text(configured.replace(old, new), encoding="utf-8")
                result = self.assess(response=response)
                self.assertEqual(result["status"], "FAIL")
                self.assertTrue(any("Configuration mismatch" in x for x in result["findings"]))

    def test_resume_rejects_changed_unlisted_source_and_response(self):
        receipts = self.root / "native receipts"
        receipts.mkdir()
        response = receipts / "response.txt"
        response.write_text("review", encoding="utf-8")
        events = receipts / "events.json"
        events.write_text("[]", encoding="utf-8")
        thread = receipts / "thread.json"
        thread.write_text("{}", encoding="utf-8")
        baseline = receipts / "before.json"
        baseline.write_text("{}", encoding="utf-8")
        children = receipts / "child-threads.json"
        children.write_text("{}", encoding="utf-8")
        for name in ("engine-runtime.json", "engine-observation.json"):
            (receipts / name).write_text("null", encoding="utf-8")
        record = {"status": "PASS", "source_fingerprint": "version", "sandbox": str(self.root),
                  "attempt": str(receipts), "response_sha256": driver.sha(response),
                  "events_sha256": driver.sha(events), "thread_sha256": driver.sha(thread),
                  "before_sha256": driver.sha(baseline),
                  "child_threads_sha256": driver.sha(children),
                  "engine_runtime_sha256": driver.sha(receipts / "engine-runtime.json"),
                  "engine_observation_sha256": driver.sha(receipts / "engine-observation.json"),
                  "observation_hashes": {},
                  "protected_hashes": driver.tree_hashes(self.root), "artifacts": {}}
        self.assertTrue(driver.can_resume(record, "version"))
        observations = self.root / ".scratch/team-observations/production/team-runs"
        observations.mkdir(parents=True)
        (observations / "review.json").write_text("{}", encoding="utf-8")
        self.assertFalse(driver.can_resume(record, "version"))
        record["observation_hashes"] = driver.tree_hashes(self.root / ".scratch/team-observations")
        self.assertTrue(driver.can_resume(record, "version"))
        (observations / "review.json").write_text('{"stale":true}', encoding="utf-8")
        self.assertFalse(driver.can_resume(record, "version"))
        (observations / "review.json").write_text("{}", encoding="utf-8")
        (self.root / "code.gd").write_text("new behavior", encoding="utf-8")
        self.assertFalse(driver.can_resume(record, "version"))
        self.assertFalse(driver.can_resume(record, "different version"))

    def test_resume_rejects_tampered_native_receipts_and_legacy_records(self):
        receipts = self.root / "native receipts tamper"
        receipts.mkdir()
        for name, content in (("response.txt", "review"), ("events.json", "[]"),
                              ("thread.json", "{}"), ("before.json", "{}"),
                              ("child-threads.json", "{}"), ("engine-runtime.json", "null"),
                              ("engine-observation.json", "null")):
            (receipts / name).write_text(content, encoding="utf-8")
        record = {"status": "PASS", "source_fingerprint": "version", "sandbox": str(self.root),
                  "attempt": str(receipts), "response_sha256": driver.sha(receipts / "response.txt"),
                  "events_sha256": driver.sha(receipts / "events.json"),
                  "thread_sha256": driver.sha(receipts / "thread.json"),
                  "before_sha256": driver.sha(receipts / "before.json"),
                  "child_threads_sha256": driver.sha(receipts / "child-threads.json"),
                  "engine_runtime_sha256": driver.sha(receipts / "engine-runtime.json"),
                  "engine_observation_sha256": driver.sha(receipts / "engine-observation.json"),
                  "observation_hashes": {},
                  "protected_hashes": driver.tree_hashes(self.root), "artifacts": {}}
        self.assertTrue(driver.can_resume(record, "version"))
        (receipts / "events.json").write_text('[{"tampered":true}]', encoding="utf-8")
        self.assertFalse(driver.can_resume(record, "version"))
        (receipts / "events.json").write_text("[]", encoding="utf-8")
        (receipts / "thread.json").write_text('{"tampered":true}', encoding="utf-8")
        self.assertFalse(driver.can_resume(record, "version"))
        (receipts / "thread.json").write_text("{}", encoding="utf-8")
        (receipts / "before.json").write_text('{"tampered":true}', encoding="utf-8")
        self.assertFalse(driver.can_resume(record, "version"))
        (receipts / "before.json").write_text("{}", encoding="utf-8")
        (receipts / "child-threads.json").write_text('{"tampered":true}', encoding="utf-8")
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
        (project / ".agents/skills/ccgs-help").mkdir(parents=True)
        (project / ".agents/skills/ccgs-help/SKILL.md").write_text("skill", encoding="utf-8")
        (project / ".codex/agents").mkdir(parents=True)
        (project / ".codex/agents/ccgs-test.toml").write_text("role", encoding="utf-8")
        (project / ".codex/hooks.json").parent.mkdir(exist_ok=True)
        (project / ".codex/hooks.json").write_text("hooks", encoding="utf-8")
        (project / "docs").mkdir()
        (project / "docs/technical-preferences.md").write_text("source preferences", encoding="utf-8")
        sandbox.mkdir()
        (sandbox / "docs").mkdir()
        (sandbox / "docs/technical-preferences.md").write_text("existing choices", encoding="utf-8")
        driver.copy_case_resources(project, sandbox)
        self.assertTrue((sandbox / ".codex/agents/ccgs-test.toml").is_file())
        self.assertEqual((sandbox / ".agents/skills/ccgs-help/SKILL.md").read_text(encoding="utf-8"), "skill")
        self.assertFalse((sandbox / ".codex/hooks.json").exists())
        self.assertEqual((sandbox / "docs/technical-preferences.md").read_text(encoding="utf-8"), "existing choices")
        fresh = self.root / "fresh sandbox"
        fresh.mkdir()
        driver.copy_case_resources(project, fresh)
        self.assertEqual((fresh / "docs/technical-preferences.md").read_text(encoding="utf-8"), "source preferences")

    def test_catalog_coverage_reports_missing_cases_and_all_authored_cases_have_tools(self):
        catalog = json.loads((ROOT / "studio-tests/native/cases.json").read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "studio-tests/migration-manifest.json").read_text(encoding="utf-8"))
        required = {r["name"] for r in manifest["skills"]}
        authored = {r["skill"] for r in catalog["cases"]}
        self.assertEqual(len(authored), len(catalog["cases"]))
        self.assertEqual(len({r["id"] for r in catalog["cases"]}), len(catalog["cases"]))
        self.assertTrue(authored <= required)
        self.assertEqual(catalog["coverage"]["authored_cases"], len(authored))
        self.assertEqual(catalog["coverage"]["unauthored_manifest_skills"], len(required - authored))
        for case in catalog["cases"]:
            self.assertTrue(case["expected"]["required_tools"])
            self.assertIn("$" + case["skill"], case["prompt"])
            self.assertIsNone(case["fixture_stdout"])
            self.assertIsNone(case["actual_result_stub"])
            self.assertIs(case["expected_native_until_run"], True)
            fixture = ROOT / "studio-tests/native/fixtures" / case["fixture"]
            self.assertTrue((fixture / "project.yaml").is_file())
            for name, content in case.get("history", {}).get("baseline", {}).items():
                self.assertTrue(driver.safe_path(fixture, name).is_file(), case["id"])
                self.assertIsInstance(content, str)
            for spec in case["expected"].get("files", []):
                driver.safe_path(fixture, spec["path"])
                if spec.get("changed") is True:
                    self.assertFalse(case["readonly"], f"{case['id']}: read-only case requires writes")
                if spec.get("changed") is False:
                    self.assertTrue(driver.safe_path(fixture, spec["path"]).is_file(),
                                    f"{case['id']}: preserved fixture input is missing: {spec['path']}")
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

    def test_batch_summary_ignores_unvisited_history_and_counts_current_results(self):
        (self.root / ".git").mkdir()
        output = self.root / ".scratch/batch"
        output.mkdir(parents=True)
        catalog = json.loads((ROOT / "studio-tests/native/cases.json").read_text(encoding="utf-8"))
        first, second = catalog["cases"][:2]
        class FixtureClient:
            def __init__(self, *args): pass
            def request(self, *args): return {}
            def notify(self, *args): pass
            def close(self): pass
        scenarios = [
            ("NOT ASSESSED", False, "NOT ASSESSED", 2),
            ("FAIL", False, "FAIL", 1),
            ("PASS", True, "PASS", 0),
        ]
        for actual, reuse_second, expected, exit_code in scenarios:
            with self.subTest(actual=actual):
                historical = {"status": "PASS" if reuse_second else "FAIL", "historical": True}
                (output / "state.json").write_text(json.dumps({"cases": {second["id"]: historical}}), encoding="utf-8")
                result = {"status": actual, "findings": [], "missing": []}
                with patch.object(driver, "Client", FixtureClient), patch.object(
                        driver.subprocess, "check_output", return_value="fixture-version"), patch.object(
                        driver, "check_hooks", return_value=[]), patch.object(
                        driver, "can_resume", side_effect=lambda record, _: reuse_second and record == historical), patch.object(
                        driver, "run_case", return_value=result) as run, contextlib.redirect_stdout(io.StringIO()):
                    code = driver.main(["--project", str(self.root), "--codex", sys.executable,
                                        "--output", str(output), "--resume",
                                        "--case", first["id"], "--case", second["id"]])
                self.assertEqual(code, exit_code)
                self.assertEqual(json.loads((output / "summary.json").read_text())["selected_result"], expected)
                self.assertEqual(run.call_count, 1)
                saved = json.loads((output / "state.json").read_text())
                self.assertEqual(saved["cases"][second["id"]], historical)

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
