"""Regression checks for mode-aware skill authorization language."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".agents" / "skills"


class AutomationContractTests(unittest.TestCase):
    def test_skills_do_not_restate_obsolete_collaborative_default(self):
        obsolete = re.compile(r"default\s+`?collaborative`?", re.I)
        matches = []
        for path in SKILLS.glob("ccgs-*/**/*.md"):
            text = path.read_text(encoding="utf-8", errors="replace")
            if obsolete.search(text):
                matches.append(str(path.relative_to(ROOT)))
        self.assertEqual(matches, [], "obsolete automation default: " + ", ".join(matches))

    def test_writes_are_mode_aware_not_per_file_approval(self):
        forbidden = re.compile(
            r"always\s+ask\s+before\s+creating\s+files|"
            r"never\s+write\s+story\s+files\s+without[^\n]*approval|"
            r"ask\s+whether\s+to\s+create\s+or\s+update\s+the\s+named\s+epic",
            re.I,
        )
        matches = []
        for path in SKILLS.glob("ccgs-*/**/*.md"):
            text = path.read_text(encoding="utf-8", errors="replace")
            if forbidden.search(text):
                matches.append(str(path.relative_to(ROOT)))
        self.assertEqual(matches, [], "unconditional write prompt: " + ", ".join(matches))

    def test_mode_guidance_preserves_consequential_decisions(self):
        workflow = (ROOT / ".agents/studio/docs/automation-modes.md").read_text(encoding="utf-8")
        setup = (SKILLS / "ccgs-test-setup/references/source-contract.md").read_text(encoding="utf-8")
        stories = (SKILLS / "ccgs-create-stories/references/full-workflow.md").read_text(encoding="utf-8")
        for text in (workflow, setup, stories):
            self.assertIn("guided", text.lower())
            self.assertIn("collaborative", text.lower())
        self.assertIn("material scope", setup.lower())
        self.assertIn("material scope", stories.lower())

    def test_negative_examples_prove_scan_is_not_a_trivial_fixture_check(self):
        obsolete = re.compile(r"default\s+`?collaborative`?", re.I)
        forbidden = re.compile(r"always\s+ask\s+before\s+creating\s+files|"
                               r"never\s+write\s+story\s+files\s+without[^\n]*approval", re.I)
        self.assertTrue(obsolete.search("project.yaml -> default `collaborative`"))
        self.assertTrue(forbidden.search("Always ask before creating files"))
        self.assertTrue(forbidden.search("Never write story files without approval first"))


if __name__ == "__main__":
    unittest.main()
