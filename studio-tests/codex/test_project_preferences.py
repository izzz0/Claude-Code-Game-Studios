"""Project-owned technical preferences resolution and migration regressions."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from test_helpers import bash_path


ROOT = Path(__file__).resolve().parents[2]
STUDIO = ROOT / ".agents" / "studio"

class ProjectPreferencesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="project preferences ")
        self.root = Path(self.tmp.name) / "project"
        self.root.mkdir()
        shutil.copytree(STUDIO, self.root / ".agents" / "studio")
        (self.root / "production").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def write_yaml(self, text="schema_version: 1\n"):
        (self.root / "project.yaml").write_text(text, encoding="utf-8")

    def write_prefs(self, path, engine, language="GDScript"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# Technical Preferences\n\n## Engine & Language\n"
            f"- **Engine**: {engine}\n- **Language**: {language}\n",
            encoding="utf-8",
        )

    def resolve(self, keys="engine_values"):
        return subprocess.run(
            [bash_path(), str(self.root / ".agents/studio/hooks/yaml-helper.sh"),
             "resolve_config", "--keys", keys],
            cwd=self.root, text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False,
        )

    def state(self):
        return subprocess.run(
            [bash_path(), str(self.root / ".agents/studio/scripts/project-state.sh")],
            cwd=self.root, text=True, encoding="utf-8", errors="replace",
            capture_output=True, check=False,
        )

    def test_project_document_is_primary_over_legacy(self):
        self.write_yaml()
        self.write_prefs(self.root / "docs/technical-preferences.md", "Godot 4.5", "GDScript")
        self.write_prefs(self.root / ".agents/studio/docs/technical-preferences.md", "Unity 6.0", "C#")
        result = self.resolve()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("name=Godot(docs/technical-preferences.md)", result.stdout)
        self.assertIn("version=4.5(docs/technical-preferences.md)", result.stdout)
        self.assertIn("language=GDScript(docs/technical-preferences.md)", result.stdout)
        engine = self.resolve("engine")
        self.assertIn("engine: Godot 4.5 (docs/technical-preferences.md)", engine.stdout)
        code_root = subprocess.run(
            [bash_path(), str(self.root / ".agents/studio/hooks/yaml-helper.sh"), "resolve_code_root"],
            cwd=self.root, text=True, encoding="utf-8", errors="replace", capture_output=True,
        )
        self.assertIn("src\tdocs/technical-preferences.md", code_root.stdout)

    def test_legacy_project_without_new_document_still_resolves(self):
        self.write_yaml()
        self.write_prefs(self.root / ".agents/studio/docs/technical-preferences.md", "Unity 6.0", "C#")
        result = self.resolve()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("name=Unity(.agents/studio/docs/technical-preferences.md)", result.stdout)
        self.assertIn("version=6.0(.agents/studio/docs/technical-preferences.md)", result.stdout)

    def test_plain_legacy_engine_label_keeps_its_configured_code_root(self):
        self.write_yaml()
        (self.root / ".agents/studio/docs/technical-preferences.md").write_text(
            "# Legacy preferences\nEngine: Godot 4.6.1\nLanguage: GDScript\n", encoding="utf-8")
        result = subprocess.run(
            [bash_path(), str(self.root / ".agents/studio/hooks/yaml-helper.sh"), "resolve_code_root"],
            cwd=self.root, text=True, encoding="utf-8", capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("src\t.agents/studio/docs/technical-preferences.md", result.stdout)

    def test_placeholder_in_new_document_does_not_mask_legacy_value(self):
        self.write_yaml()
        self.write_prefs(self.root / "docs/technical-preferences.md", "[TO BE CONFIGURED]")
        self.write_prefs(self.root / ".agents/studio/docs/technical-preferences.md", "Unreal Engine 5.4", "C++")
        result = self.resolve()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("name=Unreal Engine(.agents/studio/docs/technical-preferences.md)", result.stdout)
        self.assertIn("version=5.4(.agents/studio/docs/technical-preferences.md)", result.stdout)

    def test_original_yaml_values_override_both_documents(self):
        self.write_yaml("schema_version: 1\nengine:\n  name: Godot\n  version: 4.6\n  language: GDScript\n")
        self.write_prefs(self.root / "docs/technical-preferences.md", "Unity 6.0", "C#")
        self.write_prefs(self.root / ".agents/studio/docs/technical-preferences.md", "Unreal 5.4", "C++")
        result = self.resolve()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("name=Godot(project.yaml)", result.stdout)
        self.assertIn("version=4.6(project.yaml)", result.stdout)
        self.assertIn("language=GDScript(project.yaml)", result.stdout)

    def test_project_state_reads_project_preferences_then_legacy(self):
        self.write_yaml()
        self.write_prefs(self.root / "docs/technical-preferences.md", "Godot 4.5")
        self.write_prefs(self.root / ".agents/studio/docs/technical-preferences.md", "Unity 6.0")
        result = self.state()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("engine\tGodot\tdocs/technical-preferences.md", result.stdout)
        self.write_prefs(self.root / "docs/technical-preferences.md", "[TO BE CONFIGURED]")
        result = self.state()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("engine\tUnity\t.agents/studio/docs/technical-preferences.md", result.stdout)

    def test_migration_reads_project_document_and_falls_back_per_key(self):
        self.write_prefs(self.root / "docs/technical-preferences.md", "Godot 4.5", "[TO BE CONFIGURED]")
        self.write_prefs(self.root / ".agents/studio/docs/technical-preferences.md", "Unity 6.0", "C#")
        legacy = self.root / ".agents/studio/docs/technical-preferences.md"
        legacy_before = legacy.read_bytes()
        result = subprocess.run(
            [bash_path(), str(self.root / ".agents/studio/scripts/migrate-v1-config.sh")],
            cwd=self.root, text=True, encoding="utf-8", errors="replace", capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        config = (self.root / "project.yaml").read_text(encoding="utf-8")
        self.assertIn('name: "Godot"', config)
        self.assertIn('version: "4.5"', config)
        self.assertIn('language: "C#"', config)
        self.assertEqual(legacy.read_bytes(), legacy_before)

    def test_setup_instructions_target_project_document_only(self):
        instructions = (ROOT / ".agents/skills/ccgs-setup-engine/references/5-technical-preferences.md").read_text(encoding="utf-8")
        workflow = (ROOT / ".agents/studio/docs/core-workflow.md").read_text(encoding="utf-8")
        self.assertIn("project's `docs/technical-preferences.md`", instructions)
        self.assertIn("never overwrite an existing project document or write the template path", instructions)
        self.assertIn("`.agents/studio/docs/technical-preferences.md` only when that template exists", instructions)
        self.assertIn("treat `.agents/studio/` as read-only framework", workflow)
        self.assertIn("This workflow rule does not restrict explicit", workflow)
        self.assertIn("maintenance of the studio framework source itself", workflow)
        stack = (ROOT / ".agents/skills/ccgs-setup-engine/references/4-agents-md-stack.md").read_text(encoding="utf-8")
        self.assertIn("ordinary engine selection does not require", stack)
        self.assertIn("rewriting instruction files", stack)
        self.assertIn("do not approve it", stack)


if __name__ == "__main__":
    unittest.main()
