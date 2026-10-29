import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / ".agents/studio/runtime"
SCRIPTS = ROOT / ".agents/studio/scripts"
sys.path.insert(0, str(RUNTIME))
from checks.business import check
from context import helper


class BusinessFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ccgs business 测试 ")
        self.root = Path(self.tmp.name) / "project"
        self.root.mkdir(); (self.root / ".agents/studio/runtime/checks").mkdir(parents=True)
        shutil.copytree(RUNTIME, self.root / ".agents/studio/runtime", dirs_exist_ok=True)
        (self.root / ".agents/studio/scripts").mkdir(parents=True)
        for name in ("write-guard.sh", "registry.sh", "yaml-get.awk"):
            shutil.copy2(SCRIPTS / name, self.root / ".agents/studio/scripts" / name)
        (self.root / ".agents/studio/hooks").mkdir(parents=True)
        shutil.copy2(ROOT / ".agents/studio/hooks/yaml-helper.sh", self.root / ".agents/studio/hooks/yaml-helper.sh")
        (self.root / ".agents/studio/docs").mkdir(parents=True)
        shutil.copy2(ROOT / ".agents/studio/docs/effects-map.md", self.root / ".agents/studio/docs/effects-map.md")
        (self.root / "project.yaml").write_text("schema_version: 1\nengine:\n  name: Godot\n", encoding="utf-8")

    def tearDown(self): self.tmp.cleanup()

    def hook(self, data):
        return subprocess.run([sys.executable, str(self.root / ".agents/studio/runtime/hooks.py")], cwd=self.root,
                              input=json.dumps(data), text=True, capture_output=True)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, text=True, capture_output=True)

    def git_repo(self):
        self.git("init", "-q"); self.git("config", "user.email", "tests@example.invalid"); self.git("config", "user.name", "Tests")


class BusinessCheckTests(BusinessFixture):
    def test_lexical_path_alias_matches_reconstructed_patch_target(self):
        target = self.root / "src/main.gd"
        target.parent.mkdir()
        target.write_text("extends Node\nold\n", encoding="utf-8")
        alias = self.root / "src/../src/main.gd"
        patch = "*** Update File: src/main.gd\n@@\n extends Node\n-old\n+new\n"
        rows = check(self.root, {"tool_name": "apply_patch", "cwd": str(self.root),
                                "tool_input": {"command": patch}}, [(alias, "src/main.gd")])
        self.assertEqual(rows, [])
        self.assertEqual(target.read_text(encoding="utf-8"), "extends Node\nold\n")

    def test_ambiguous_native_context_never_checks_old_config_as_proposed(self):
        target = self.root / "project.yaml"
        target.write_text("project:\n  name: Godot\nengine:\n  name: Godot\n", encoding="utf-8")
        before = target.read_bytes()
        patch = "*** Update File: project.yaml\n@@ engine:\n-  name: Godot\n+  name: InvalidEngine\n*** End Patch"
        rows = check(self.root, {"tool_name": "apply_patch", "cwd": str(self.root),
                                "tool_input": {"command": patch}}, [(target, "project.yaml")])
        self.assertTrue(any("NOT ASSESSED: proposed content" in row for row in rows), rows)
        self.assertEqual(before, target.read_bytes())

    def test_native_add_and_namespaced_write_report_protected_overwrite(self):
        rel = "production/epics/demo/EPIC.md"
        target = self.root / rel
        target.parent.mkdir(parents=True)
        target.write_text("old", encoding="utf-8")
        patch = f"*** Add File: {rel}\n+replacement\n*** End Patch"
        for tool, inp in (("apply_patch", {"command": patch}),
                          ("functions.Write", {"content": "replacement"})):
            rows = check(self.root, {"tool_name": tool, "cwd": str(self.root), "tool_input": inp}, [(target, rel)])
            self.assertTrue(any(row.startswith("OVERWRITE\t") for row in rows), (tool, rows))
            self.assertEqual(target.read_text(encoding="utf-8"), "old")

    def test_write_edit_and_native_patch_reconstruct_exact_content(self):
        target = self.root / "src/main.gd"; target.parent.mkdir(); target.write_text("extends Node\nold\n")
        rows = check(self.root, {"tool_name":"Write", "tool_input":{"content":"extends Node\nnew\n"}}, [(target, "src/main.gd")])
        self.assertEqual(rows, [])
        rows = check(self.root, {"tool_name":"Edit", "tool_input":{"old_string":"old", "new_string":"new"}}, [(target, "src/main.gd")])
        self.assertEqual(rows, [])
        patch = "*** Update File: src/main.gd\n@@\n extends Node\n-old\n+new\n"
        rows = check(self.root, {"tool_name":"apply_patch", "tool_input":{"command":patch}}, [(target, "src/main.gd")])
        self.assertEqual(rows, [])

    def test_invalid_json_proposed_content_and_valid_working_copy_are_distinct(self):
        target = self.root / "assets/data/config.json"; target.parent.mkdir(parents=True); target.write_text("{}")
        bad = check(self.root, {"tool_name":"Write", "tool_input":{"content":"{"}}, [(target, "assets/data/config.json")])
        self.assertFalse(any("parse=invalid" in row for row in bad), bad)
        # write-guard is not the JSON validator; the actual pre-hook after path reconstruction is observable.
        result = self.hook({"hook_event_name":"PostToolUse","tool_name":"Write","cwd":str(self.root),
                            "tool_input":{"file_path":"assets/data/config.json"}})
        self.assertEqual(result.returncode, 0)

    def test_freeze_active_and_protected_epic_are_observed_without_writes(self):
        freeze = self.root / "production/localization/freeze-status.md"; freeze.parent.mkdir(parents=True); freeze.write_text("Status: ACTIVE\n")
        epic = self.root / "production/epics/demo/EPIC.md"; epic.parent.mkdir(parents=True); epic.write_text("old")
        rows = check(self.root, {"tool_name":"Write", "tool_input":{"content":"new"}},
                     [(self.root / "assets/data/strings/en.json", "assets/data/strings/en.json")])
        self.assertTrue(any(row.startswith("FREEZE\t") for row in rows), rows)
        overwrite = helper(self.root, ".agents/studio/scripts/write-guard.sh", "--root", str(self.root),
                           "overwrite", "production/epics/demo/EPIC.md", "--tool", "Write")
        self.assertIn("OVERWRITE\t", overwrite.stdout)
        self.assertEqual(epic.read_text(), "old")

    def test_registry_valid_header_compare_remove_and_native_delete_status(self):
        registry = self.root / "design/registry/entities.yaml"; registry.parent.mkdir(parents=True)
        registry.write_text("# Registry layout: entities\nentities:\n  - name: Player\n    status: active\n    source: src/player.gd\n", encoding="utf-8")
        (self.root / "src/player.gd").parent.mkdir(); (self.root / "src/player.gd").write_text("x")
        new = self.root / "new-registry.yaml"; new.write_text("# Registry layout: entities\nentities: []\n", encoding="utf-8")
        rows = check(self.root, {"tool_name":"Write", "tool_input":{"content":new.read_text()}}, [(registry, "design/registry/entities.yaml")])
        self.assertTrue(any(row.startswith("REMOVED\t") for row in rows), rows)
        patch = "*** Delete File: design/registry/entities.yaml\n*** End of File"
        rows = check(self.root, {"tool_name":"apply_patch", "tool_input":{"command":patch}}, [(registry, "design/registry/entities.yaml")])
        self.assertTrue(any(row.startswith("REMOVED\t") or row.startswith("STATUS\t") for row in rows), rows)

    def test_registry_validate_uses_no_extra_arguments_and_invalid_args_are_regression(self):
        registry = self.root / "design/registry/entities.yaml"; registry.parent.mkdir(parents=True)
        registry.write_text("entities:\n  - name: Player\n    status: active\n    source: src/player.gd\n")
        result = helper(self.root, ".agents/studio/scripts/registry.sh", "--root", str(self.root), "validate")
        self.assertEqual(result.returncode, 0, result.stderr); self.assertNotIn("unknown option", result.stderr.lower())

    def test_prototype_header_import_and_local_config_are_checked_by_real_write_guard(self):
        proto = self.root / "prototypes/demo.gd"; proto.parent.mkdir(); proto.write_text("extends Node\npreload('res://src/main.gd')\n")
        rows = check(self.root, {"tool_name":"Write", "tool_input":{"content":proto.read_text()}}, [(proto, "prototypes/demo.gd")])
        self.assertTrue(any("PROTOTYPE_HEADER" in row or "PROTOTYPE_IMPORT" in row for row in rows), rows)
        local = self.root / "project.local.yaml"; local.write_text("engine:\n  name: Unity\n")
        config = helper(self.root, ".agents/studio/scripts/write-guard.sh", "config", "project.local.yaml", str(local))
        self.assertIn("NOT_LOCAL\t", config.stdout)

    def test_commit_checks_index_vs_worktree_and_real_command_variants_without_committing(self):
        self.git_repo(); data = self.root / "assets/data/bad.json"; data.parent.mkdir(parents=True); data.write_text("{broken")
        self.git("add", str(data)); invalid_index = self.hook({"hook_event_name":"PreToolUse","tool_name":"Bash","cwd":str(self.root),"tool_input":{"command":"git commit -m x"}})
        self.assertIn('"permissionDecision": "deny"', invalid_index.stdout)
        data.write_text("{\"ok\":true}"); self.git("add", str(data)); data.write_text("{broken")
        valid_index = self.hook({"hook_event_name":"PreToolUse","tool_name":"Bash","cwd":str(self.root),"tool_input":{"command":"git commit -m x"}})
        self.assertNotIn('"permissionDecision": "deny"', valid_index.stdout)
        all_flag = self.hook({"hook_event_name":"PreToolUse","tool_name":"Bash","cwd":str(self.root),"tool_input":{"command":"git commit -a -m x"}})
        self.assertIn('"permissionDecision": "deny"', all_flag.stdout)
        self.assertEqual(self.git("status", "--porcelain").returncode, 0)

    def test_commit_add_chain_untracked_bad_file_and_explicit_path_exclusion(self):
        self.git_repo(); good = self.root / "src/good.gd"; good.parent.mkdir(); good.write_text("ok")
        self.git("add", str(good)); self.git("commit", "-m", "seed", "--quiet")
        bad = self.root / "assets/data/new.json"; bad.parent.mkdir(parents=True); bad.write_text("{bad")
        chained = self.hook({"hook_event_name":"PreToolUse","tool_name":"Bash","cwd":str(self.root),"tool_input":{"command":"git add assets/data/new.json && git commit -m x"}})
        self.assertIn('"permissionDecision": "deny"', chained.stdout)
        # A path-limited commit excludes an unrelated broken file.
        bad.write_text("{bad2"); self.git("reset", "-q", "HEAD", "--", str(bad))
        limited = self.hook({"hook_event_name":"PreToolUse","tool_name":"Bash","cwd":str(self.root),"tool_input":{"command":"git commit -m x src/good.gd"}})
        self.assertNotIn('"permissionDecision": "deny"', limited.stdout)

    def test_protected_checkpoint_hashes_are_unchanged_by_all_hook_calls(self):
        paths = ["production/session-state/active.md", "production/epics/e/EPIC.md", "production/qa/checkpoint.md", "stories/checkpoint.md"]
        for rel in paths:
            p = self.root / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text("protected")
        before = {rel: hashlib.sha256((self.root / rel).read_bytes()).hexdigest() for rel in paths}
        for rel in paths:
            self.hook({"hook_event_name":"PreToolUse","tool_name":"Write","cwd":str(self.root),"tool_input":{"file_path":rel,"content":"changed"}})
        after = {rel: hashlib.sha256((self.root / rel).read_bytes()).hexdigest() for rel in paths}
        self.assertEqual(before, after)


if __name__ == "__main__": unittest.main()
