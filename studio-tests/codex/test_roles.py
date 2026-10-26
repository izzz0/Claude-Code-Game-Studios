"""Contracts for the 49 native Codex role agents."""

from pathlib import Path
import re
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / ".codex" / "agents"
CATALOG = ROOT / ".agents" / "studio" / "docs" / "role-catalog.md"
REQUIRED = {"name", "description", "developer_instructions"}
FORBIDDEN_KEYS = {
    "model", "model_reasoning_effort", "model_reasoning_summary", "model_verbosity",
    "model_provider", "provider", "sandbox_mode", "approval_policy", "mcp_servers",
    "permissions", "permission", "tools", "disallowed_tools",
}
LEGACY_MARKERS = (".claude/", "CLAUDE_", "allowed-tools:", "model:")
ROLE_NAME = re.compile(r"^ccgs-[a-z0-9]+(?:-[a-z0-9]+)*$")


class RoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = sorted(AGENTS.glob("*.toml"))
        cls.data = {}
        for path in cls.files:
            with path.open("rb") as handle:
                cls.data[path] = tomllib.load(handle)

    def test_exactly_49_standalone_agents_are_discoverable(self):
        self.assertEqual(len(self.files), 49)
        names = {item["name"] for item in self.data.values()}
        expected = {path.stem for path in self.files}
        self.assertEqual(names, expected)
        self.assertTrue(all(ROLE_NAME.fullmatch(name) for name in names))

    def test_official_standalone_schema_and_no_parent_overrides(self):
        for path, item in self.data.items():
            with self.subTest(path=path.name):
                self.assertEqual(set(item), REQUIRED)
                self.assertFalse(FORBIDDEN_KEYS.intersection(item))
                self.assertTrue(item["description"].strip())
                self.assertGreater(len(item["developer_instructions"].strip()), 500)

    def test_contracts_are_role_specific_and_preserve_native_boundaries(self):
        instructions = [item["developer_instructions"] for item in self.data.values()]
        self.assertEqual(len(set(instructions)), 49)
        for path, item in self.data.items():
            with self.subTest(path=path.name):
                text = item["developer_instructions"]
                self.assertTrue("accepted brief" in text or "accepted work" in text)
                self.assertIn("read-only", text)
                self.assertIn("independent reviewer", text)
                self.assertTrue("Must NOT Do" in text or "Coordination" in text or "Workflow" in text)
        # Engine specialists retain unmistakable engine/language expertise.
        for role, marker in {
            "godot-gdscript-specialist": "GDScript",
            "godot-csharp-specialist": "C#",
            "unity-dots-specialist": "DOTS",
            "ue-gas-specialist": "Gameplay Ability System",
            "network-programmer": "network",
        }.items():
            self.assertIn(marker.lower(), self.data[AGENTS / f"ccgs-{role}.toml"]["developer_instructions"].lower())

    def test_migration_has_no_legacy_paths_or_claude_metadata(self):
        for path, item in self.data.items():
            text = path.read_text(encoding="utf-8") + item["developer_instructions"]
            with self.subTest(path=path.name):
                for marker in LEGACY_MARKERS:
                    self.assertNotIn(marker, text)
                self.assertNotRegex(text, r"(?m)^\s*(?:model|provider|sandbox_mode|approval_policy)\s*=")
                self.assertNotRegex(text, r"(?m)^\s*tools\s*=")

    def test_role_references_and_catalog_are_complete(self):
        role_names = {item["name"] for item in self.data.values()}
        skill_names = {p.parent.name for p in (ROOT / ".agents" / "skills").glob("*/SKILL.md")}
        # Team skills are owned by the root agent but are valid native routes.
        skill_names.update({"ccgs-team-qa", "ccgs-team-release"})
        known_names = role_names | skill_names
        catalog = CATALOG.read_text(encoding="utf-8")
        self.assertEqual(set(re.findall(r"^### `(ccgs-[a-z0-9-]+)`$", catalog, re.M)), role_names)
        unknown = set()
        for path, item in self.data.items():
            refs = set(re.findall(r"\bccgs-[a-z0-9-]+\b", item["developer_instructions"]))
            unknown.update(refs - known_names)
        self.assertFalse(unknown, f"unknown native role/skill reference(s): {sorted(unknown)}")
        # Counterexample: the validator must reject a prefixed name that is not in the union.
        synthetic_unknown = {"ccgs-not-a-real-role-or-skill"} - known_names
        self.assertEqual(synthetic_unknown, {"ccgs-not-a-real-role-or-skill"})


if __name__ == "__main__":
    unittest.main()
