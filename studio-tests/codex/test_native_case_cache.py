"""Resume invalidation follows the selected scenario and all shared runtime inputs."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("native_case_cache", ROOT / "studio-tests/native/run_acceptance.py")
driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(driver)


class NativeCaseCacheTests(unittest.TestCase):
    def test_unrelated_case_changes_do_not_reuse_or_invalidate_the_wrong_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".git").mkdir()
            (root / ".codex").mkdir()
            hook = root / ".codex/hooks.json"
            hook.write_text('{"hooks":{"Stop":[]}}', encoding="utf-8")
            catalog_dir = root / "catalog"
            catalog_dir.mkdir()
            cases = [{"id": name, "skill": "ccgs-" + name, "fixture": name,
                      "prompt": "Inspect " + name} for name in ("first", "other")]
            for case in cases:
                fixture = catalog_dir / "fixtures" / case["fixture"]
                fixture.mkdir(parents=True)
                (fixture / "project.yaml").write_text("schema_version: 1\n", encoding="utf-8")
            for module in ("team_evidence.py", "engine_evidence.py"):
                (catalog_dir / module).write_text("protocol fixture", encoding="utf-8")
            observed = []

            class Client:
                def __init__(self, *args): pass
                def notify(self, *args): pass
                def close(self): pass
                def request(self, method, params):
                    return {"data": [{"hooks": [{"sourcePath": str(hook), "eventName": "stop",
                            "enabled": True, "trustStatus": "trusted"}]}]} if method == "hooks/list" else {}

            def run():
                (catalog_dir / "cases.json").write_text(json.dumps({"version": 2, "cases": cases}), encoding="utf-8")
                with patch.object(driver, "HERE", catalog_dir), patch.object(driver, "Client", Client), patch.object(
                        driver.subprocess, "check_output", return_value="synthetic-host"), patch.object(
                        driver, "can_resume", side_effect=lambda record, digest: observed.append(digest) or False), patch.object(
                        driver, "run_case", return_value={"id": "first", "status": "PASS"}), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(driver.main(["--project", str(root), "--codex", sys.executable,
                                                  "--case", "first", "--resume"]), 0)
                return observed[-1]

            original = run()
            cases[1]["prompt"] = "A different unrelated scenario"
            (catalog_dir / "fixtures/other/project.yaml").write_text("other input", encoding="utf-8")
            self.assertEqual(run(), original)
            cases[0]["prompt"] = "A changed selected scenario"
            self.assertNotEqual(run(), original)
            selected = run()
            (catalog_dir / "fixtures/first/project.yaml").write_text("changed selected input", encoding="utf-8")
            self.assertNotEqual(run(), selected)
            selected = run()
            (catalog_dir / "team_evidence.py").write_text("shared verifier changed", encoding="utf-8")
            self.assertNotEqual(run(), selected)
