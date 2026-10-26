"""Offline tests of the optional project-local update observer."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".agents/studio/runtime"))
import updates


class UpdateNoticeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ccgs update 测试 ")
        self.root = Path(self.tmp.name)
        self.cache = self.root / ".scratch/runtime/update-status.json"
        self.cache.parent.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_off_and_offline_never_launch_refresh(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(updates, "helper", return_value=subprocess.CompletedProcess([], 0, "false\tproject.yaml")), patch.object(updates.subprocess, "Popen") as launch:
            self.assertEqual(updates.notice(self.root), "")
            launch.assert_not_called()
        with patch.dict(os.environ, {"CCGS_OFFLINE": "1"}), patch.object(updates, "helper") as helper:
            self.assertIn("offline", updates.notice(self.root))
            helper.assert_not_called()
        self.assertFalse(self.cache.exists())

    def test_optional_helper_timeout_returns_unassessed(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(updates, "helper", side_effect=subprocess.TimeoutExpired("bash", 5)):
            self.assertIn("NOT ASSESSED", updates.notice(self.root))

    def test_corrupt_cache_is_unassessed_without_launching(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(updates, "helper", return_value=subprocess.CompletedProcess([], 0, "true\tproject.yaml")), patch.object(updates.subprocess, "Popen") as launch:
            for value in ([1], {"checked": "bad"}, {"checked": time.time(), "status": "OBSERVED", "upstream": "invalid"}):
                self.cache.write_text(json.dumps(value), encoding="utf-8")
                self.assertIn("NOT ASSESSED", updates.notice(self.root))
            launch.assert_not_called()

    def test_fresh_cached_version_does_not_assert_compatibility(self):
        self.cache.write_text(json.dumps({"checked": time.time(), "status": "OBSERVED", "upstream": "99.0.0"}), encoding="utf-8")
        with patch.dict(os.environ, {}, clear=True), patch.object(updates, "helper", return_value=subprocess.CompletedProcess([], 0, "true\tproject.yaml")), patch.object(updates.subprocess, "Popen") as launch:
            self.assertIn("manual compatibility review", updates.notice(self.root))
            launch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
