"""Fixed source obligations for nine native routes, separate from execution evidence."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".agents/skills"
CONTRACTS = {
    "combat": ({"ccgs-gameplay-programmer"}, "production/combat/[feature]-gdd-draft.md"),
    "narrative": ({"ccgs-writer"}, "production/narrative/[content-slug]/brief.md"),
    "ui": ({"ccgs-ui-programmer", "ccgs-ux-designer"}, "production/ui/[feature-name]/visual-design.md"),
    "release": ({"ccgs-release-manager"}, "production/releases/go-no-go-[version].md"),
    "polish": ({"ccgs-performance-analyst", "ccgs-technical-artist"}, "production/polish/[area]-report-[date].md"),
    "audio": ({"ccgs-sound-designer"}, "production/audio/[feature]/direction.md"),
    "level": ({"ccgs-level-designer"}, "production/levels/[level-name]/layout.md"),
    "live-ops": ({"ccgs-live-ops-designer", "ccgs-economy-designer"}, "production/live-ops/[season-slug]/brief.md"),
    "qa": ({"ccgs-qa-tester"}, "production/qa/qa-plan-[sprint]-[date].md"),
}


class TeamSkillTests(unittest.TestCase):
    def test_all_nine_routes_have_source_phases_and_artifact_destinations(self):
        self.assertEqual({p.name for p in SKILLS.glob("ccgs-team-*") if (p / "SKILL.md").is_file()},
                         {f"ccgs-team-{name}" for name in CONTRACTS})
        for name, (roles, artifact) in CONTRACTS.items():
            with self.subTest(team=name):
                folder = SKILLS / f"ccgs-team-{name}"
                text = (folder / "references/workflow.md").read_text(encoding="utf-8")
                individual = next(line for line in text.splitlines() if line.startswith("- **`individual`**"))
                self.assertTrue(roles <= set(re.findall(r"ccgs-[a-z-]+", individual)))
                self.assertIn(artifact, text)
                self.assertRegex(text, r"(?m)^### (?:Phase|Step) [1-6]:")
                self.assertIn("Error Recovery Protocol", text)
                self.assertIn("NOT ASSESSED", text)

    def test_native_lifecycle_routes_and_conditional_role_contracts(self):
        for name in CONTRACTS:
            text = (SKILLS / f"ccgs-team-{name}/SKILL.md").read_text(encoding="utf-8")
            with self.subTest(team=name):
                for command in ("team-run.py", "assign", "event", "show", "resume", "--read-only"):
                    self.assertIn(command, text)
                self.assertIn("actual IDs", text)
                self.assertIn("references/workflow.md", text)
        combat = (SKILLS / "ccgs-team-combat/references/workflow.md").read_text(encoding="utf-8")
        polish = (SKILLS / "ccgs-team-polish/references/workflow.md").read_text(encoding="utf-8")
        narrative = (SKILLS / "ccgs-team-narrative/references/workflow.md").read_text(encoding="utf-8")
        self.assertIn("only if the feature flags AI work", combat)
        self.assertIn("No programmer is active", polish)
        self.assertIn("ND-CONSISTENCY", narrative)
        self.assertIn("self-checked by ccgs-writer", narrative)

    def test_no_legacy_host_execution_or_implicit_public_release(self):
        for name in CONTRACTS:
            for path in (SKILLS / f"ccgs-team-{name}").rglob("*.md"):
                with self.subTest(path=path.name, team=name):
                    self.assertNotRegex(path.read_text(encoding="utf-8"), r"subagent_type|Task(?:Create|Get|List|Update)|CLAUDE_|AskUserQuestion|`Agent`")
        release = (SKILLS / "ccgs-team-release/references/workflow.md").read_text(encoding="utf-8")
        self.assertIn("Verified Local Release Package", release)
        self.assertIn("separate explicit user request", release)
        self.assertNotIn("Only then proceed to Phase 6", release)


if __name__ == "__main__":
    unittest.main()
