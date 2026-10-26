import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / ".agents/studio/runtime"
YAML_HELPER = ROOT / ".agents/studio/hooks/yaml-helper.sh"


class RuntimeFixture(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(prefix="ccgs fixture 测试 ")
        self.root = Path(self._td.name) / "project 测试"
        self.root.mkdir()
        shutil.copytree(RUNTIME, self.root / ".agents/studio/runtime")
        (self.root / ".agents/studio/scripts").mkdir(parents=True)
        for name in ("write-guard.sh", "read-guard.sh", "registry.sh", "yaml-get.awk"):
            shutil.copy2(ROOT / ".agents/studio/scripts" / name,
                         self.root / ".agents/studio/scripts" / name)
        (self.root / ".agents/studio/docs").mkdir(parents=True)
        shutil.copy2(ROOT / ".agents/studio/docs/effects-map.md",
                     self.root / ".agents/studio/docs/effects-map.md")
        (self.root / ".agents/studio/hooks").mkdir(parents=True)
        shutil.copy2(YAML_HELPER, self.root / ".agents/studio/hooks/yaml-helper.sh")
        (self.root / ".codex").mkdir()
        shutil.copy2(ROOT / ".codex/hooks.json", self.root / ".codex/hooks.json")

    def tearDown(self):
        self._td.cleanup()

    def state(self, *args):
        return subprocess.run([sys.executable, str(self.root / ".agents/studio/runtime/state.py"),
                               "--root", str(self.root), *map(str, args)], text=True, capture_output=True)

    def hook(self, data, *, cwd=None):
        return subprocess.run([sys.executable, str(self.root / ".agents/studio/runtime/hooks.py")], cwd=cwd or self.root,
                              input=json.dumps(data), text=True, capture_output=True)

    def configured_hook(self, event, payload, *, cwd=None):
        config = json.loads((self.root / ".codex/hooks.json").read_text(encoding="utf-8"))
        entry = config["hooks"][event][0]["hooks"][0]
        command = entry.get("commandWindows") if os.name == "nt" else entry["command"]
        if os.name == "nt":
            argv = command
        else:
            argv = ["bash", "-lc", command]
        env = os.environ.copy()
        env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
        return subprocess.run(argv, cwd=cwd or self.root, input=json.dumps(payload), text=True,
                              shell=(os.name == "nt"),
                              capture_output=True, env=env)

    def configured_hook_powershell(self, event, payload, *, cwd=None):
        config = json.loads((self.root / ".codex/hooks.json").read_text(encoding="utf-8"))
        command = config["hooks"][event][0]["hooks"][0]["commandWindows"]
        return subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                              cwd=cwd or self.root, input=json.dumps(payload), text=True,
                              capture_output=True, env=os.environ.copy())

    def git_init(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        (self.root / "project.yaml").write_text("engine:\n  name: Godot\n", encoding="utf-8")


class StateRegressionTests(RuntimeFixture):
    def test_cas_changed_first_write_and_original_hash_retry(self):
        target = self.root / "状态 folder" / "state.md"; target.parent.mkdir(); target.write_text("old", encoding="utf-8")
        src = self.root / "new.tmp"; src.write_text("new", encoding="utf-8"); old = hashlib.sha256(b"old").hexdigest()
        self.assertEqual(self.state("--path", "状态 folder/state.md", "--source", src, "--expected-sha256", old, "--operation", "first").returncode, 0)
        retry = self.state("--path", "状态 folder/state.md", "--source", src, "--expected-sha256", old, "--operation", "retry")
        self.assertEqual(retry.returncode, 0, retry.stderr); self.assertTrue(json.loads(retry.stdout)["unchanged"])
        other = self.root / "other.tmp"; other.write_text("different")
        self.assertEqual(self.state("--path", "状态 folder/state.md", "--source", other, "--expected-sha256", old, "--operation", "conflict").returncode, 3)

    def test_concurrent_distinct_writers_one_wins(self):
        sources = []
        for value in "ABCD":
            p = self.root / f"{value}.tmp"; p.write_text(value); sources.append(p)
        def attempt(p):
            return self.state("--path", "winner.txt", "--source", p, "--expected-sha256", "MISSING", "--operation", p.stem).returncode
        with ThreadPoolExecutor(max_workers=4) as pool: codes = list(pool.map(attempt, sources))
        self.assertEqual(codes.count(0), 1, codes); self.assertEqual(codes.count(3), 3)

    def test_concurrent_identical_writers_all_succeed(self):
        src = self.root / "same.tmp"; src.write_text("same")
        def attempt(i):
            return self.state("--path", "same.txt", "--source", src, "--expected-sha256", "MISSING", "--operation", i)
        with ThreadPoolExecutor(max_workers=6) as pool: results = list(pool.map(attempt, range(6)))
        self.assertTrue(all(r.returncode == 0 for r in results), [(r.returncode, r.stderr) for r in results])

    def test_live_lock_ignores_old_mtime_and_process_exit_keeps_inode(self):
        holder = self.root / "hold.py"
        holder.write_text("import sys,time\nsys.path.insert(0,sys.argv[1])\nfrom state import file_lock\nfrom pathlib import Path\nwith file_lock(Path(sys.argv[2]),10): print('held',flush=True); time.sleep(30)\n")
        lock = self.root / "held.lock"; proc = subprocess.Popen([sys.executable, str(holder), str(RUNTIME), str(lock)], stdout=subprocess.PIPE, text=True)
        try:
            self.assertEqual(proc.stdout.readline().strip(), "held"); old = time.time() - 3600; os.utime(lock, (old, old))
            code = "import sys;sys.path.insert(0,sys.argv[1]);from state import file_lock;from pathlib import Path\ntry:\n with file_lock(Path(sys.argv[2]),.15): pass\nexcept Exception as e: raise SystemExit(getattr(e,'code',1))"
            timed = subprocess.run([sys.executable, "-c", code, str(RUNTIME), str(lock)], capture_output=True)
            self.assertEqual(timed.returncode, 4); inode = lock.stat().st_ino; proc.terminate(); proc.wait(timeout=5)
            self.assertTrue(lock.exists()); self.assertEqual(lock.stat().st_ino, inode)
            reacquire = subprocess.run([sys.executable, "-c", code.replace(".15", "1"), str(RUNTIME), str(lock)], capture_output=True)
            self.assertEqual(reacquire.returncode, 0, reacquire.stderr)
        finally:
            if proc.poll() is None: proc.kill()
            if proc.stdout is not None: proc.stdout.close()
            proc.wait(timeout=5)


class HookBoundaryTests(RuntimeFixture):
    def test_engine_whitelist_has_positive_and_negative_paths(self):
        self.git_init(); (self.root / "src").mkdir(); (self.root / "src/main.gd").write_text("x")
        allowed = self.hook({"hook_event_name":"PreToolUse","tool_name":"Write","cwd":str(self.root),"tool_input":{"file_path":"src/main.gd","content":"extends Node\n"}})
        self.assertEqual(allowed.returncode, 0); self.assertNotIn('"permissionDecision": "deny"', allowed.stdout)
        self.assertNotIn("NOT ASSESSED", allowed.stdout); self.assertNotIn('"error"', allowed.stdout)
        test_code = self.hook({"hook_event_name":"PreToolUse","tool_name":"Write","cwd":str(self.root),"tool_input":{"file_path":"tests/test_case.gd"}})
        self.assertEqual(test_code.returncode, 0); self.assertNotIn('"permissionDecision": "deny"', test_code.stdout)
        denied = self.hook({"hook_event_name":"PreToolUse","tool_name":"Write","cwd":str(self.root),"tool_input":{"file_path":"other/main.gd"}})
        self.assertIn('"permissionDecision": "deny"', denied.stdout)

    def test_unset_engine_and_local_override_are_denied(self):
        (self.root / "project.yaml").write_text("name: no-engine\n"); (self.root / "src").mkdir(); (self.root / "project.local.yaml").write_text("engine:\n  name: Godot\n")
        result = self.hook({"hook_event_name":"PreToolUse","tool_name":"Write","cwd":str(self.root),"tool_input":{"file_path":"src/main.gd"}})
        self.assertIn('"permissionDecision": "deny"', result.stdout)

    def test_cocos_confirmed_roots_and_external_reads(self):
        self.git_init()
        (self.root / "project.yaml").write_text("engine:\n  name: Cocos\n", encoding="utf-8")
        (self.root / "project.json").write_text('{"creator":{"version":"3.8"}}', encoding="utf-8")
        (self.root / "assets/scripts").mkdir(parents=True)
        allowed = self.hook({"hook_event_name":"PreToolUse", "tool_name":"Write", "cwd":str(self.root),
                             "tool_input":{"file_path":"assets/scripts/main.ts"}})
        self.assertNotIn('"permissionDecision": "deny"', allowed.stdout)
        denied = self.hook({"hook_event_name":"PreToolUse", "tool_name":"Write", "cwd":str(self.root),
                            "tool_input":{"file_path":"shared/generated/main.ts"}})
        self.assertIn('"permissionDecision": "deny"', denied.stdout)
        external = self.root.parent / "外部参考 文件.md"
        external.write_text("reference", encoding="utf-8")
        read = self.hook({"hook_event_name":"PreToolUse", "tool_name":"Read", "cwd":str(self.root),
                          "tool_input":{"file_path":str(external)}})
        self.assertNotIn('"permissionDecision": "deny"', read.stdout)

    def test_checkpoint_and_all_patch_destinations_are_denied(self):
        self.git_init(); (self.root / "production/session-state").mkdir(parents=True)
        patch = "\n".join((f"*** {kind} File: {path}" for kind,path in (("Add","a.txt"),("Update","b.txt"),("Delete","c.txt"))))
        patch += "\n*** Move to: d.txt"
        patch += "\n*** Add File: production/session-state/active.md\n*** Add File: ../outside.txt"
        result = self.hook({"hook_event_name":"PreToolUse","tool_name":"apply_patch","cwd":str(self.root),"tool_input":{"command":patch}})
        self.assertIn('"permissionDecision": "deny"', result.stdout)

    def test_checkpoint_relative_to_production_is_denied(self):
        self.git_init(); (self.root / "production/session-state").mkdir(parents=True)
        result = self.hook({"hook_event_name":"PreToolUse","tool_name":"Write","cwd":str(self.root / "production"),
                            "tool_input":{"file_path":"session-state/active.md"}}, cwd=self.root / "production")
        self.assertIn('"permissionDecision": "deny"', result.stdout)

    def test_each_patch_destination_is_checked_independently(self):
        self.git_init()
        for line in ("*** Add File: ../add.txt", "*** Update File: ../update.txt",
                     "*** Delete File: ../delete.txt", "*** Move to: ../moved.txt"):
            result = self.hook({"hook_event_name":"PreToolUse","tool_name":"apply_patch","cwd":str(self.root),
                                "tool_input":{"command":line}})
            self.assertIn('"permissionDecision": "deny"', result.stdout, line)

    def test_nested_project_wins_and_foreign_git_isolated(self):
        self.git_init(); nested = self.root / "nested"; nested.mkdir(); (nested / "project.yaml").write_text("engine:\n  name: Godot\n")
        result = self.hook({"hook_event_name":"PreToolUse","tool_name":"Write","cwd":str(nested),"tool_input":{"file_path":"src/main.gd"}}, cwd=nested)
        self.assertNotIn('"permissionDecision": "deny"', result.stdout)
        subprocess.run(["git","init","-q"], cwd=nested, check=True)
        isolated = self.hook({"hook_event_name":"SessionStart","cwd":str(nested)}, cwd=nested)
        self.assertEqual(isolated.returncode, 0); self.assertIn("NOT ASSESSED", isolated.stdout)

    def test_actual_hook_commands_emit_one_json_object_and_receipts(self):
        self.git_init(); payload = json.dumps({"hook_event_name":"Stop","cwd":str(self.root),"session_id":"s","turn_id":"t"})
        cmd = ["cmd","/d","/s","/c","python -X utf8 .agents/studio/runtime/hooks.py"] if os.name == "nt" else ["bash","-lc","python3 -X utf8 .agents/studio/runtime/hooks.py"]
        env = os.environ.copy(); env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH","")
        for _ in range(2):
            out = subprocess.run(cmd, cwd=self.root, input=payload, text=True, capture_output=True, env=env)
            self.assertEqual(out.returncode, 0, out.stderr); json.loads(out.stdout)
        self.assertTrue(list((self.root / ".scratch/runtime/receipts").glob("*.json")))

    def test_configured_command_stop_family_is_json_bounded_and_deduplicated(self):
        self.git_init(); protected = self.root / "protected.txt"; protected.write_text("keep")
        before = hashlib.sha256(protected.read_bytes()).hexdigest()
        def call(event):
            return self.configured_hook(event, {"hook_event_name":event,"cwd":str(self.root),
                "session_id":"parallel","turn_id":"same","event_id":"duplicate"})
        results = []
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(call, ["Stop"] * 8))
        self.assertTrue(all(r.returncode == 0 for r in results), [(r.returncode, r.stderr, r.stdout) for r in results])
        for event in ("Stop", "SubagentStop", "Interrupt"):
            result = call(event); self.assertEqual(result.returncode, 0, result.stderr); json.loads(result.stdout)
        self.assertEqual(hashlib.sha256(protected.read_bytes()).hexdigest(), before)
        receipts = list((self.root / ".scratch/runtime/receipts").glob("*.json"))
        self.assertEqual(sum(1 for p in receipts if json.loads(p.read_text())["kind"] == "Stop"), 1)
        self.assertTrue((self.root / ".scratch/runtime/receipts").is_dir())

    def test_exact_configured_commands_work_in_native_shells_without_mutating_protected_files(self):
        self.git_init()
        config = json.loads((self.root / ".codex/hooks.json").read_text(encoding="utf-8"))
        command_windows = [entry["hooks"][0]["commandWindows"]
                           for entries in config["hooks"].values() for entry in entries]
        self.assertEqual(len(command_windows), 10)
        self.assertEqual(len(set(command_windows)), 1)
        portable_launcher = command_windows[0]
        self.assertTrue(portable_launcher.startswith("python -X utf8 -c "))
        command_posix = [entry["hooks"][0]["command"]
                         for entries in config["hooks"].values() for entry in entries]
        self.assertEqual(len(command_posix), 10)
        self.assertEqual(len(set(command_posix)), 1)
        self.assertTrue(command_posix[0].startswith("python3 -X utf8 "))
        protected = {
            "src/protected.gd": "code\n",
            "design/story.md": "story\n",
            "production/qa/report.md": "qa\n",
            "production/session-state/active.md": "checkpoint\n",
        }
        for relative, content in protected.items():
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        before = {relative: hashlib.sha256((self.root / relative).read_bytes()).hexdigest()
                  for relative in protected}
        nested = self.root / "子目录 with spaces"
        nested.mkdir()
        event_payloads = {
            "SessionStart": {"source": "startup"},
            "PreToolUse": {"tool_name": "Write",
                            "tool_input": {"file_path": str(self.root / "production/session-state/active.md")}},
            "PostToolUse": {"tool_name": "Write",
                             "tool_input": {"file_path": str(self.root / ".agents/skills/example/SKILL.md")}},
            "PreCompact": {},
            "PostCompact": {},
            "SubagentStart": {"agent_id": "agent"},
            "SubagentStop": {"agent_id": "agent"},
            "Stop": {},
            "Interrupt": {},
            "SessionEnd": {},
        }
        runners = [("cmd", self.configured_hook)]
        if os.name == "nt":
            self.assertIsNotNone(shutil.which("powershell.exe"), "PowerShell 5 is required")
            runners.append(("powershell", self.configured_hook_powershell))
        for shell_name, runner in runners:
            for cwd_index, cwd in enumerate((self.root, nested)):
                for event_index, (event, extra) in enumerate(event_payloads.items()):
                    payload = {"hook_event_name": event, "cwd": str(cwd),
                               "session_id": f"native-{cwd_index}",
                               "turn_id": f"{event_index}-{cwd_index}", **extra}
                    result = runner(event, payload, cwd=cwd)
                    self.assertEqual(result.returncode, 0,
                                     f"{shell_name} {cwd.name} {event}: {result.stderr}")
                    output = [line for line in result.stdout.splitlines() if line.strip()]
                    self.assertEqual(len(output), 1,
                                     f"{shell_name} {cwd.name} {event}: {result.stdout!r}")
                    message = json.loads(output[0])
                    self.assertIsInstance(message, dict)
                    if event == "PreToolUse":
                        specific = message["hookSpecificOutput"]
                        self.assertEqual(specific["hookEventName"], "PreToolUse")
                        self.assertEqual(specific["permissionDecision"], "deny")
        after = {relative: hashlib.sha256((self.root / relative).read_bytes()).hexdigest()
                 for relative in protected}
        self.assertEqual(after, before)
        receipts = list((self.root / ".scratch/runtime/receipts").glob("*.json"))
        self.assertTrue(receipts)
        self.assertEqual({json.loads(path.read_text(encoding="utf-8"))["kind"] for path in receipts},
                         {"SessionStart", "PostToolUse", "PreCompact", "PostCompact",
                          "SubagentStart", "SubagentStop", "Stop", "Interrupt", "SessionEnd"})


if __name__ == "__main__": unittest.main()
