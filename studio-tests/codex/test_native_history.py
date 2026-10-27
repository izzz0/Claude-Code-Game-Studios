"""Git-based cases must never borrow framework history or change host trust roots."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("native_history", ROOT / "studio-tests/native/run_acceptance.py")
driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(driver)


class NativeHistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="native history 中文 ")
        self.root = Path(self.tmp.name)
        self.source = self.root / "design/gdd/delivery.md"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("score = delivered * 125\n", encoding="utf-8")
        self.before = driver.tree_hashes(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(["git", "--git-dir", str(self.root / ".scratch/case-history.git"),
                               "--work-tree", str(self.root), *args], capture_output=True,
                              text=True, encoding="utf-8")

    def test_baseline_diff_is_real_and_current_fixture_and_host_root_are_preserved(self):
        driver.prepare_history({"history": {"baseline": {
            "design/gdd/delivery.md": "score = delivered * 100\n"}}}, self.root)
        result = self.git("diff", "HEAD", "--", "design/gdd/delivery.md")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("-score = delivered * 100", result.stdout)
        self.assertIn("+score = delivered * 125", result.stdout)
        self.assertFalse((self.root / ".git").exists())
        self.assertEqual(driver.tree_hashes(self.root), self.before)
        self.assertEqual(self.git("log", "--format=%s").stdout.strip(), "Fixture baseline")

    def test_empty_history_has_no_parent_commits_and_does_not_change_inputs(self):
        driver.prepare_history({"history": {"baseline": {}}}, self.root)
        self.assertNotEqual(self.git("log", "--oneline").returncode, 0)
        self.assertEqual(driver.tree_hashes(self.root), self.before)
        self.assertFalse((self.root / ".git").exists())

    def test_history_rejects_paths_outside_fixture_before_creating_repository(self):
        for name in ("../outside.md", ".codex/config.toml", "missing.md"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                driver.prepare_history({"history": {"baseline": {name: "old"}}}, self.root)
            self.assertFalse((self.root / ".scratch/case-history.git").exists())
        self.assertEqual(driver.tree_hashes(self.root), self.before)


if __name__ == "__main__":
    unittest.main()
