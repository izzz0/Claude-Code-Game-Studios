import hashlib
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path, PureWindowsPath
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("native_reads", ROOT / "studio-tests/native/native_reads.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
powershell_read_path = MODULE.powershell_read_path
verified_read_inputs = MODULE.verified_read_inputs


def _item(path, output="fixture output", *, status="completed", exit_code=0,
          wrapper=True, quote="single", executable=r"C:\Users\tester\.cache\codex\native\pwsh.exe",
          action=None, command=None, actions=None, cwd=None):
    script = ("Microsoft.PowerShell.Management\\Get-Content -LiteralPath '" +
              path.replace("'", "''") + "' -Raw -Encoding utf8")
    if action is None:
        action = script
    if command is None:
        if not wrapper:
            command = script
        elif quote == "double":
            command = '"' + executable + '" -Command "' + json.dumps(script)[1:-1] + '"'
        else:
            command = '"' + executable + '" -Command ' + "'" + script.replace("'", "''") + "'"
    if actions is None:
        actions = [{"type": "unknown", "command": action}]
    item = {"type": "commandExecution", "command": command, "commandActions": actions,
            "status": status, "exitCode": exit_code, "aggregatedOutput": output}
    if cwd is not None:
        item["cwd"] = str(cwd)
    return item


class NativeReadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.path = "资料/space and 'quote'.txt"
        target = self.root / self.path
        target.parent.mkdir(parents=True)
        self.content = "标题\r\nbody\r\n"
        target.write_bytes(self.content.encode("utf-8"))

    def tearDown(self):
        self.tmp.cleanup()

    def expected(self):
        return {self.path: {"sha256": hashlib.sha256(self.content.encode("utf-8")).hexdigest(),
                            "content": self.content}}

    def test_accepts_wrapped_read_with_unicode_spaces_and_quote(self):
        item = _item(self.path, self.content.replace("\r\n", "\n"))
        self.assertEqual(powershell_read_path(item, self.root), self.path)
        self.assertTrue(verified_read_inputs({"turns": [{"items": [item]}]}, self.expected(), self.root))

    def test_accepts_doublequoted_json_escaped_script_body(self):
        item = _item(self.path, self.content, quote="double")
        self.assertEqual(powershell_read_path(item, self.root), self.path)

    def test_rejects_doublequoted_wrapper_extras_and_mismatched_body(self):
        item = _item(self.path, self.content, quote="double")
        action = item["commandActions"][0]["command"] + "; whoami"
        prefix = item["command"].split(' -Command "', 1)[0]
        item["command"] = prefix + ' -Command "' + json.dumps(action)[1:-1] + '"'
        item["commandActions"][0]["command"] = action
        self.assertIsNone(powershell_read_path(item, self.root))
        item = _item(self.path, self.content, quote="double")
        item["commandActions"][0]["command"] += "; whoami"
        self.assertIsNone(powershell_read_path(item, self.root))

    def test_accepts_exact_bare_protocol_fixture(self):
        item = _item(self.path, self.content, wrapper=False)
        self.assertEqual(powershell_read_path(item, self.root), self.path)
        item["commandActions"][0]["rawCommand"] = item["commandActions"][0].pop("command")
        self.assertEqual(powershell_read_path(item, self.root), self.path)

    def test_resolves_read_literal_against_receipt_cwd_and_returns_root_relative_path(self):
        source = self.root / "src" / "file.gd"
        source.parent.mkdir()
        content = "extends Node\n"
        source.write_bytes(content.encode("utf-8"))
        item = _item("file.gd", content, cwd=source.parent)
        self.assertEqual(powershell_read_path(item, self.root), "src/file.gd")
        expected = {"src/file.gd": {"sha256": hashlib.sha256(content.encode()).hexdigest(),
                                    "content": content}}
        self.assertTrue(verified_read_inputs({"turns": [{"items": [item]}]}, expected, self.root))

    def test_rejects_outside_cwd_and_same_named_wrong_subdirectory_file(self):
        root_input = self.root / "input.txt"
        root_input.write_bytes(self.content.encode("utf-8"))
        outside = self.root.parent / (self.root.name + "-elsewhere")
        outside.mkdir()
        (outside / "input.txt").write_bytes(root_input.read_bytes())
        expected = {"input.txt": {"sha256": hashlib.sha256(self.content.encode()).hexdigest(),
                                   "content": self.content}}
        try:
            item = _item("input.txt", self.content, cwd=outside)
            self.assertIsNone(powershell_read_path(item, self.root))
            self.assertFalse(verified_read_inputs({"turns": [{"items": [item]}]}, expected, self.root))
        finally:
            (outside / "input.txt").unlink(missing_ok=True)
            outside.rmdir()

        (self.root / "src").mkdir()
        (self.root / "src" / "input.txt").write_bytes(root_input.read_bytes())
        item = _item("input.txt", self.content, cwd=self.root / "src")
        self.assertEqual(powershell_read_path(item, self.root), "src/input.txt")
        self.assertFalse(verified_read_inputs({"turns": [{"items": [item]}]}, expected, self.root))

    def test_rejects_malformed_explicit_cwd(self):
        for cwd in ("relative/path", "", None):
            item = _item(self.path, self.content)
            item["cwd"] = cwd
            self.assertIsNone(powershell_read_path(item, self.root))

    def test_accepts_one_host_added_terminal_newline_and_display_bom(self):
        item = _item(self.path, "\ufeff" + self.content + "\n")
        self.assertTrue(verified_read_inputs({"turns": [{"items": [item]}]}, self.expected(), self.root))

    def test_rejects_extra_statements_redirection_variables_and_encoded_commands(self):
        bad_scripts = [
            "Microsoft.PowerShell.Management\\Get-Content -LiteralPath '" + self.path + "' -Raw -Encoding utf8; whoami",
            "Microsoft.PowerShell.Management\\Get-Content -LiteralPath '" + self.path + "' -Raw -Encoding utf8 | Out-File x",
            "Microsoft.PowerShell.Management\\Get-Content -LiteralPath $env:FILE -Raw -Encoding utf8",
            "Invoke-Expression 'Get-Content x'",
            "Microsoft.PowerShell.Management\\Get-Content -LiteralPath '" + self.path + "' -Raw -Encoding utf8 > x",
        ]
        for script in bad_scripts:
            with self.subTest(script=script):
                item = _item(self.path, command=script, action=script, wrapper=False)
                self.assertIsNone(powershell_read_path(item, self.root))

    def test_rejects_fake_actions_mismatch_and_wrapper_extras(self):
        item = _item(self.path)
        item["commandActions"] = [{"type": "read", "command": item["commandActions"][0]["command"]}]
        self.assertIsNone(powershell_read_path(item, self.root))
        item = _item(self.path, action="Get-Content x")
        self.assertIsNone(powershell_read_path(item, self.root))
        item = _item(self.path)
        item["command"] += " -NoExit"
        self.assertIsNone(powershell_read_path(item, self.root))
        item = _item(self.path)
        item["command"] = "whoami; " + item["command"]
        self.assertIsNone(powershell_read_path(item, self.root))

    def test_rejects_relative_unc_and_workspace_local_executables(self):
        for exe in ("pwsh.exe", r"\\server\share\pwsh.exe"):
            with self.subTest(exe=exe):
                self.assertIsNone(powershell_read_path(_item(self.path, executable=exe), self.root))
        self.assertTrue(MODULE._windows_path_under(
            PureWindowsPath(r"F:\acceptance\tools\pwsh.exe"),
            PureWindowsPath(r"f:\acceptance")))
        self.assertFalse(MODULE._windows_path_under(
            PureWindowsPath(r"F:\other\pwsh.exe"),
            PureWindowsPath(r"F:\acceptance")))
        if self.root.drive:
            local_exe = str(self.root / "tools" / "pwsh.exe")
            local_exe = local_exe.replace("/", "\\")
            self.assertIsNone(powershell_read_path(
                _item(self.path, executable=local_exe), self.root))

    def test_rejects_workspace_local_executable_through_sandbox_junction(self):
        class SandboxPath:
            def __init__(self, _value):
                pass

            def absolute(self):
                return PureWindowsPath(r"F:\acceptance-alias")

            def resolve(self):
                return PureWindowsPath(r"F:\acceptance-physical")

        expected_script = _item(self.path, self.content)["commandActions"][0]["command"]
        with patch.object(MODULE, "Path", SandboxPath):
            for executable in (
                r"F:\acceptance-alias\tools\pwsh.exe",
                r"F:\acceptance-physical\tools\pwsh.exe",
            ):
                item = _item(self.path, self.content, executable=executable)
                self.assertIsNone(MODULE._script(item, "fixture-sandbox"))

            external = _item(self.path, self.content)
            self.assertEqual(MODULE._script(external, "fixture-sandbox"), expected_script)
            mismatch = _item(self.path, self.content, action=expected_script + "; whoami")
            self.assertIsNone(MODULE._script(mismatch, "fixture-sandbox"))

        if os.name != "nt":
            return

        junction = self.root.parent / (self.root.name + "-junction")
        try:
            subprocess.run(["cmd.exe", "/c", "mklink", "/J", str(junction), str(self.root)],
                           check=True, capture_output=True, text=True)
            self.assertNotEqual(str(junction.absolute()).casefold(),
                                str(junction.resolve()).casefold())
            local_exe = str(junction / "tools" / "pwsh.exe").replace("/", "\\")
            item = _item(self.path, self.content, executable=local_exe)
            self.assertIsNone(powershell_read_path(item, junction))

            external_item = _item(self.path, self.content)
            self.assertEqual(powershell_read_path(external_item, junction), self.path)
        finally:
            if junction.exists():
                subprocess.run(["cmd.exe", "/c", "rmdir", str(junction)], check=True,
                               capture_output=True, text=True)

    def test_rejects_absolute_parent_and_nonexistent_paths(self):
        for path in ("../outside.txt", "C:\\temp\\file.txt", "/etc/passwd", "missing.txt"):
            with self.subTest(path=path):
                self.assertIsNone(powershell_read_path(_item(path), self.root))

    def test_rejects_symlink_escape(self):
        outside = self.root.parent / (self.root.name + "-outside")
        outside.mkdir()
        (outside / "secret.txt").write_text("secret", encoding="utf-8")
        link = self.root / "escape"
        try:
            if os.name == "nt":
                subprocess.run(["cmd.exe", "/c", "mklink", "/J", str(link), str(outside)],
                               check=True, capture_output=True, text=True)
            else:
                link.symlink_to(outside, target_is_directory=True)
            self.assertIsNone(powershell_read_path(_item("escape/secret.txt"), self.root))
        finally:
            if link.exists():
                if os.name == "nt":
                    subprocess.run(["cmd.exe", "/c", "rmdir", str(link)], check=False,
                                   capture_output=True, text=True)
                else:
                    link.unlink(missing_ok=True)
            (outside / "secret.txt").unlink(missing_ok=True)
            outside.rmdir()

    def test_requires_completed_zero_exit_full_output_and_current_bytes(self):
        cases = [
            _item(self.path, self.content, status="failed"),
            _item(self.path, self.content, exit_code=1),
            _item(self.path, self.content[:-5]),
            _item(self.path, "wrong"),
        ]
        for item in cases:
            with self.subTest(item=item):
                self.assertFalse(verified_read_inputs({"turns": [{"items": [item]}]}, self.expected(), self.root))
        good = _item(self.path, self.content)
        (self.root / self.path).write_text("stale", encoding="utf-8")
        self.assertFalse(verified_read_inputs({"turns": [{"items": [good]}]}, self.expected(), self.root))

    def test_requires_every_expected_path_and_valid_expected_hash(self):
        other = "second.txt"
        (self.root / other).write_text("two", encoding="utf-8")
        expected = self.expected()
        expected[other] = {"sha256": hashlib.sha256(b"two").hexdigest(), "content": "two"}
        thread = {"turns": [{"items": [_item(self.path, self.content)]}]}
        self.assertFalse(verified_read_inputs(thread, expected, self.root))
        expected[other]["sha256"] = "0" * 64
        self.assertFalse(verified_read_inputs(thread, expected, self.root))


if __name__ == "__main__":
    unittest.main()
