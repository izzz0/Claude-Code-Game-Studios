"""Protocol tests for native engine evidence; no fake engine is treated as real."""

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "native_engine_evidence", ROOT / "studio-tests/native/engine_evidence.py"
)
engine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engine)


class NativeEngineEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="native engine evidence ")
        self.sandbox = Path(self.tmp.name)
        (self.sandbox / "src").mkdir()
        (self.sandbox / "tests").mkdir()
        (self.sandbox / "src/game.gd").write_text("extends Node\n", encoding="utf-8")
        (self.sandbox / "tests/test_game.gd").write_text("extends Node\n", encoding="utf-8")
        executable = self.sandbox / "fixture-godot.exe"
        executable.write_bytes(b"fake executable fixture")
        addon_source = self.sandbox / "fixture-addon"
        addon_source.mkdir()
        (addon_source / "plugin.cfg").write_text("[plugin]\n", encoding="utf-8")
        addon_copy = self.sandbox / "addons/gdUnit4"
        addon_copy.parent.mkdir()
        import shutil
        shutil.copytree(addon_source, addon_copy)
        self.runtime = {
            "available": True, "executable": str(executable),
            "executable_sha256": engine._sha256(executable),
            "gdunit4_source": str(addon_source),
            "gdunit4_sha256": engine._tree_hash(addon_source),
            "gdunit4_sandbox_sha256": engine._tree_hash(addon_copy),
            "version": "4.6.1",
        }
        self.case = {"engine_test": "godot"}

    def tearDown(self):
        self.tmp.cleanup()

    def xml(self, tests=2, failures=0, errors=0, skipped=0, flaky=0, orphans=0):
        cases = []
        for index in range(tests):
            details = (("<failure/>" if index < failures else "")
                       + ("<error/>" if index < errors else "")
                       + ("<skipped/>" if index < skipped else ""))
            cases.append("<testcase name=\"case%d\">%s</testcase>" % (index, details))
        case_xml = "".join(cases)
        return (
            '<?xml version="1.0"?><testsuites tests="%d" failures="%d" '
            'errors="%d" skipped="%d" flaky="%d" orphans="%d">'
            '<testsuite tests="%d" failures="%d" errors="%d" skipped="%d" '
            'flaky="%d" orphans="%d">%s</testsuite></testsuites>'
            % (tests, failures, errors, skipped, flaky, orphans,
               tests, failures, errors, skipped, flaky, orphans, case_xml)
        )

    def mocked_run(self, xml_text=None, test_code=0, timeout=False):
        def run(args, **kwargs):
            if "--version" in args:
                return subprocess.CompletedProcess(args, 0, "4.6.1", "")
            if "--import" in args:
                return subprocess.CompletedProcess(args, 0, "", "")
            if timeout:
                raise subprocess.TimeoutExpired(args, 120, output="partial")
            if xml_text is not None:
                result = self.sandbox / "reports/report_1/results.xml"
                result.parent.mkdir(parents=True, exist_ok=True)
                result.write_text(xml_text, encoding="utf-8")
            return subprocess.CompletedProcess(args, test_code, "", "")
        return run

    def assess(self, **kwargs):
        with patch.object(engine.subprocess, "run", side_effect=self.mocked_run(**kwargs)):
            return engine.assess_engine(self.case, self.sandbox, self.runtime)

    def test_protocol_clean_nonzero_result_is_verified(self):
        result = self.assess(xml_text=self.xml(tests=9), test_code=0)
        self.assertEqual(result["verified"], ["engine_tests"])
        self.assertFalse(result["missing"])
        self.assertFalse(result["findings"])

    def test_zero_tests_is_not_assessed(self):
        result = self.assess(xml_text=self.xml(tests=0), test_code=0)
        self.assertFalse(result["verified"])
        self.assertTrue(any("zero tests" in item for item in result["missing"]))

    def test_missing_xml_is_not_assessed(self):
        result = self.assess(xml_text=None, test_code=0)
        self.assertTrue(any("fresh gdUnit4" in item for item in result["missing"]))

    def test_nonzero_runner_without_report_remains_a_confirmed_failure(self):
        result = self.assess(xml_text=None, test_code=100)
        self.assertFalse(result["verified"])
        self.assertTrue(any("exited 100" in item for item in result["findings"]))
        self.assertTrue(any("fresh gdUnit4" in item for item in result["missing"]))

    def test_unchanged_existing_xml_is_stale(self):
        path = self.sandbox / "reports/report_1/results.xml"
        path.parent.mkdir(parents=True)
        path.write_text(self.xml(tests=2), encoding="utf-8")
        result = self.assess(xml_text=None, test_code=0)
        self.assertTrue(any("fresh gdUnit4" in item for item in result["missing"]))

    def test_malformed_xml_is_not_crash_or_pass(self):
        result = self.assess(xml_text="<testsuites", test_code=0)
        self.assertTrue(any("malformed" in item for item in result["missing"]))
        self.assertFalse(result["verified"])

    def test_missing_numeric_count_is_not_zeroed(self):
        malformed = '<testsuites tests="1" errors="0" failures="0" skipped="0" flaky="0" orphans="0"><testsuite tests="1" errors="0" failures="0" flaky="0" orphans="0"><testcase/></testsuite></testsuites>'
        result = self.assess(xml_text=malformed, test_code=0)
        self.assertTrue(any("missing" in item for item in result["missing"]))
        self.assertFalse(result["verified"])

    def test_gdunit_6_1_3_format_accepts_omitted_root_errors_and_orphans(self):
        path = Path(__file__).resolve().parent / "fixtures/gdunit4-6.1.3-results.xml"
        counts = engine._parse_results(path)
        self.assertEqual(counts["tests"], 9)
        self.assertEqual(counts["errors"], 0)
        self.assertIsNone(counts["orphans"])

    def test_failures_are_findings_even_when_runner_returns_zero(self):
        result = self.assess(xml_text=self.xml(tests=2, failures=1), test_code=0)
        self.assertFalse(result["verified"])
        self.assertTrue(result["findings"])

    def test_timeout_is_not_assessed(self):
        result = self.assess(timeout=True)
        self.assertTrue(any("timed out" in item for item in result["findings"]))

    def test_exit_mismatch_is_a_finding(self):
        result = self.assess(xml_text=self.xml(tests=2), test_code=1)
        self.assertFalse(result["verified"])
        self.assertTrue(any("disagrees" in item for item in result["findings"]))

    def test_prepare_non_godot_case_does_not_probe(self):
        self.assertIsNone(engine.prepare_engine({"engine_test": "unity"}, self.sandbox, ROOT))

    def test_prepare_uses_deterministic_resource_and_records_hashes(self):
        project = self.sandbox / "project"
        executable = project / "godot.exe"
        addon = project / "gdunit4"
        addon.mkdir(parents=True)
        (addon / "plugin.cfg").write_text("[plugin]\n", encoding="utf-8")
        executable.parent.mkdir(parents=True, exist_ok=True)
        executable.write_bytes(b"deterministic executable fixture")
        config_dir = project / ".scratch/native-resources"
        config_dir.mkdir(parents=True)
        (config_dir / "godot.json").write_text(
            '{"executable":"%s","gdunit4_source":"%s","version":"4.6.1"}'
            % (str(executable).replace("\\", "\\\\"), str(addon).replace("\\", "\\\\")),
            encoding="utf-8",
        )
        with patch.object(engine.subprocess, "run", return_value=subprocess.CompletedProcess(
            [str(executable), "--version"], 0, "4.6.10", "")):
            unavailable = engine.prepare_engine(self.case, self.sandbox, project)
        self.assertFalse(unavailable["available"])
        self.assertIn("version mismatch", unavailable["missing"][0])
        with patch.object(engine.subprocess, "run", return_value=subprocess.CompletedProcess(
            [str(executable), "--version"], 0, "4.6.1", "")):
            runtime = engine.prepare_engine(self.case, self.sandbox, project)
        self.assertTrue(runtime["available"], runtime)
        self.assertTrue(runtime["executable_sha256"])
        self.assertTrue(runtime["gdunit4_sha256"])
        self.assertTrue((self.sandbox / "addons/gdUnit4/plugin.cfg").is_file())
        self.assertTrue((self.sandbox / "project.godot").is_file())


if __name__ == "__main__":
    unittest.main()
