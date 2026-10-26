"""Repository contracts for the native Codex skills and executable resources."""
from pathlib import Path
import re
import os
import subprocess
import sys
import tempfile
import unittest
import json

from test_helpers import bash_path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".agents" / "skills"
ALLOWED_INITIALIZED_MODE_KEYS = {"modes.rigor", "modes.automation"}
EXPANDED_RIGOR_KEYS = (
    "modes.review_mode", "modes.workflow", "docs.density", "qa.level",
    "modes.story_granularity", "team.size",
)
NON_FIRST_PARTY_DIRS = {
    ".scratch", "node_modules", "examples", "sandbox", "sandboxes",
    "qa-sandbox", "vendor", "third_party", "third-party",
}
MANIFEST = ROOT / "studio-tests" / "migration-manifest.json"
NAMES = {row["name"] for row in json.loads(MANIFEST.read_text(encoding="utf-8"))["skills"]}


class StructureTests(unittest.TestCase):
    @staticmethod
    def _yaml_key(root, dotted):
        env = os.environ.copy()
        env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
        helper = root / ".agents" / "studio" / "hooks" / "yaml-helper.sh"
        result = subprocess.run(
            [bash_path(), str(helper), "get_yaml_key", str(root / "project.yaml"), dotted],
            cwd=root, env=env, text=True, encoding="utf-8", errors="replace",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if result.returncode:
            raise AssertionError(f"get_yaml_key failed for {dotted}: {result.stderr}")
        return result.stdout.strip()

    @classmethod
    def _config_values(cls, root):
        keys = (*ALLOWED_INITIALIZED_MODE_KEYS, *EXPANDED_RIGOR_KEYS)
        return {key: cls._yaml_key(root, key) for key in keys}

    def _assert_config_contract(self, root):
        values = self._config_values(root)
        self.assertIn(
            (values["modes.rigor"], values["modes.automation"]),
            (("", ""), ("minimal", "guided")),
        )
        for key in EXPANDED_RIGOR_KEYS:
            self.assertEqual(values[key], "", key)
        return values

    @staticmethod
    def _first_party_claude_files(root):
        matches = []
        for path in root.rglob("CLAUDE.md"):
            relative_parts = path.relative_to(root).parts
            if any(part in NON_FIRST_PARTY_DIRS for part in relative_parts):
                continue
            if relative_parts[:2] == ("addons", "gdUnit4"):
                continue
            matches.append(path)
        return matches

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
        role_names = {p.stem for p in (ROOT / ".codex" / "agents").glob("*.toml")}
        for text in texts:
            routes = set(re.findall(r"\bccgs-[a-z-]+", text))
            routes -= role_names
            self.assertLessEqual(routes, NAMES)

    def test_explicit_framework_references_exist(self):
        documents = list(SKILLS.glob("*/SKILL.md"))
        documents += list((ROOT / ".agents" / "studio" / "docs").rglob("*.md"))
        documents += [ROOT / "AGENTS.md", ROOT / "README.md"]
        for document in documents:
            text = document.read_text(encoding="utf-8")
            for reference in re.findall(r"\.agents/[A-Za-z0-9_./-]+", text):
                reference = reference.rstrip(".")
                if reference.endswith("-"):
                    continue
                if reference.endswith("/"):
                    reference = reference.rstrip("/")
                with self.subTest(document=document.relative_to(ROOT), reference=reference):
                    self.assertTrue((ROOT / reference).exists(), reference)

    def test_codex_only_active_resources(self):
        self.assertFalse((ROOT / ".claude").exists())
        self.assertFalse(self._first_party_claude_files(ROOT))
        for path in (ROOT / ".agents").rglob("*"):
            if path.suffix not in {".md", ".sh", ".gd", ".awk"}:
                continue
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT)):
                if path.name == "compat-inventory.sh":
                    continue
                self.assertNotRegex(text, r"CLAUDE_(?:SKILL|PROJECT)_DIR|\.claude/")
                self.assertNotRegex(text, r"(?m)^!\x60|^allowed-tools:|^model:")

    def test_fresh_or_initialized_config_does_not_shadow_rigor(self):
        self._assert_config_contract(ROOT)
        active = (ROOT / "project.yaml").read_text(encoding="utf-8-sig")
        self.assertTrue((ROOT / ".codex" / "hooks.json").exists())
        self.assertEqual((ROOT / ".agents/studio/VERSION").read_text().strip(), "1.2.0-codex.2")
        self.assertIn("version: 1.2.0-codex.2", active)

    def test_initialized_minimal_guided_config_is_allowed(self):
        with tempfile.TemporaryDirectory(prefix="ccgs initialized ") as directory:
            root = Path(directory)
            (root / ".agents/studio/hooks").mkdir(parents=True)
            (root / ".agents/studio/hooks/yaml-helper.sh").write_bytes(
                (ROOT / ".agents/studio/hooks/yaml-helper.sh").read_bytes()
            )
            (root / "project.yaml").write_text(
                "schema_version: 1\n"
                "notes: |\n"
                "  workflow: documentation text\n"
                "metadata:\n"
                "  size: 3\n"
                "modes:\n"
                "  rigor: minimal\n"
                "  automation: guided\n",
                encoding="utf-8",
            )
            initialized = (root / "project.yaml").read_text(encoding="utf-8")
            for text, expected in (("schema_version: 1\n", ("", "")),
                                   (initialized, ("minimal", "guided"))):
                with self.subTest(expected=expected):
                    (root / "project.yaml").write_text(text, encoding="utf-8")
                    values = self._assert_config_contract(root)
                    self.assertEqual((values["modes.rigor"], values["modes.automation"]), expected)
                    for key in EXPANDED_RIGOR_KEYS:
                        self.assertEqual(values[key], "", key)

    def test_seeded_expanded_rigor_keys_are_rejected(self):
        for key in EXPANDED_RIGOR_KEYS:
            with self.subTest(key=key):
                with tempfile.TemporaryDirectory(prefix="ccgs seeded ") as directory:
                    root = Path(directory)
                    (root / ".agents/studio/hooks").mkdir(parents=True)
                    (root / ".agents/studio/hooks/yaml-helper.sh").write_bytes(
                        (ROOT / ".agents/studio/hooks/yaml-helper.sh").read_bytes()
                    )
                    path, leaf = key.split(".")
                    (root / "project.yaml").write_text(
                        f"schema_version: 1\n{path}:\n  {leaf}: seeded\n",
                        encoding="utf-8",
                    )
                    with self.assertRaises(AssertionError):
                        self._assert_config_contract(root)

    def test_ignored_scratch_and_third_party_claude_files_are_not_first_party(self):
        with tempfile.TemporaryDirectory(prefix="ccgs claude files ") as directory:
            root = Path(directory)
            paths = [root / ".scratch" / "addon" / "CLAUDE.md",
                     root / "addons" / "gdUnit4" / "CLAUDE.md"]
            for path in paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("third-party instructions\n", encoding="utf-8")
                self.assertTrue(path.exists())
                with self.subTest(path=path):
                    self.assertNotIn(path, self._first_party_claude_files(root))

    def test_first_party_legacy_claude_files_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="ccgs first-party ") as directory:
            root = Path(directory)
            for path in (root / "CLAUDE.md", root / ".claude" / "CLAUDE.md",
                         root / "addons" / "my_game_tools" / "CLAUDE.md"):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("legacy instructions\n", encoding="utf-8")
                with self.subTest(path=path):
                    self.assertIn(path, self._first_party_claude_files(root))


if __name__ == "__main__":
    unittest.main()
