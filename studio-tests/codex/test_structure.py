"""Repository contracts for the nine Codex skills and their executable resources."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".agents" / "skills"
NAMES = {
    "ccgs-start", "ccgs-setup-engine", "ccgs-brainstorm", "ccgs-prototype",
    "ccgs-create-stories", "ccgs-dev-story", "ccgs-smoke-check",
    "ccgs-code-review", "ccgs-story-done",
}


class StructureTests(unittest.TestCase):
    def test_discoverable_skill_metadata(self):
        files = list(SKILLS.glob("*/SKILL.md"))
        self.assertEqual({p.parent.name for p in files}, NAMES)
        for path in files:
            with self.subTest(skill=path.parent.name):
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"))
                header, body = text[4:].split("\n---\n", 1)
                # The skills intentionally use only two single-line YAML scalars.
                fields = dict(line.split(":", 1) for line in header.splitlines())
                self.assertEqual(set(fields), {"name", "description"})
                self.assertEqual(fields["name"].strip(), path.parent.name)
                description = fields["description"].strip()
                self.assertTrue(description)
                if not description.startswith(('"', "'")):
                    self.assertNotIn(": ", description)
                    self.assertNotIn(" #", description)
                self.assertTrue(body.strip())

    def test_every_skill_route_exists(self):
        texts = [p.read_text(encoding="utf-8") for p in SKILLS.glob("*/SKILL.md")]
        for text in texts:
            routes = set(re.findall(r"\bccgs-[a-z-]+", text))
            self.assertLessEqual(routes, NAMES)

    def test_explicit_framework_references_exist(self):
        documents = list(SKILLS.glob("*/SKILL.md"))
        documents += list((ROOT / ".agents" / "studio" / "docs").rglob("*.md"))
        documents += [ROOT / "AGENTS.md", ROOT / "README.md"]
        for document in documents:
            text = document.read_text(encoding="utf-8")
            for reference in re.findall(r"\.agents/[A-Za-z0-9_./-]+", text):
                if reference.endswith("/"):
                    reference = reference.rstrip("/")
                with self.subTest(document=document.relative_to(ROOT), reference=reference):
                    self.assertTrue((ROOT / reference).exists(), reference)

    def test_codex_only_active_resources(self):
        self.assertFalse((ROOT / ".claude").exists())
        self.assertFalse(list(ROOT.rglob("CLAUDE.md")))
        for path in (ROOT / ".agents").rglob("*"):
            if path.suffix not in {".md", ".sh", ".gd", ".awk"}:
                continue
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertNotRegex(text, r"CLAUDE_(?:SKILL|PROJECT)_DIR|\.claude/")
                self.assertNotRegex(text, r"(?m)^!\x60|^allowed-tools:|^model:")

    def test_fresh_template_does_not_shadow_rigor(self):
        text = (ROOT / "project.yaml").read_text(encoding="utf-8-sig")
        active = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
        self.assertNotRegex(active, r"(?m)^modes:|^team:|^qa:|^docs:")
        self.assertFalse((ROOT / ".codex" / "config.toml").exists())
        self.assertEqual((ROOT / ".agents/studio/VERSION").read_text().strip(), "1.2.0-codex.1")
        self.assertIn("version: 1.2.0-codex.1", active)


if __name__ == "__main__":
    unittest.main()
