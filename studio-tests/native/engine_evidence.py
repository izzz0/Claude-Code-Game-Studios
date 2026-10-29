"""Real Godot/gdUnit4 evidence plumbing for native acceptance integration.

This module is intentionally not wired into the acceptance driver.  The caller
must invoke it only after a completed native implementation turn and must keep
its returned observation separate from model claims.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET


TEST_COMMAND = (
    "--headless", "--path", "{sandbox}", "-s", "-d",
    "--remote-debug", "tcp://127.0.0.1:0",
    "res://addons/gdUnit4/bin/GdUnitCmdTool.gd",
    "-a", "res://tests", "--ignoreHeadlessMode",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _tree_hash(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(item.relative_to(path).as_posix().encode("utf-8"))
        digest.update(_sha256(item).encode("ascii"))
    return digest.hexdigest().upper()


def _resource_config(project: Path) -> tuple[Path, dict] | tuple[None, None]:
    config_path = project / ".scratch" / "native-resources" / "godot.json"
    if not config_path.is_file():
        return None, None
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, None
    if not isinstance(config, dict):
        return None, None
    return config_path, config


def _decode_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value


def _version_is_exact(version: str) -> bool:
    return version.strip() == "4.6.1" or version.strip().startswith("4.6.1.")


def prepare_engine(case: dict, sandbox: Path | str, project: Path | str) -> dict | None:
    """Prepare a real Godot/gdUnit4 sandbox and return resource observations.

    A non-Godot case is outside this helper and returns ``None``.  Missing or
    invalid real resources return a runtime object marked unavailable so the
    caller can report NOT ASSESSED without fabricating an engine result.
    """
    if case.get("engine_test") != "godot":
        return None
    sandbox = Path(sandbox)
    project = Path(project)
    config_path, config = _resource_config(project)
    runtime = {
        "engine": "godot",
        "available": False,
        "missing": [],
        "config_path": str(config_path) if config_path else None,
        "observation": {},
    }
    if config is None:
        runtime["missing"].append(".scratch/native-resources/godot.json")
        return runtime
    executable = Path(config.get("executable", ""))
    addon_source = project / config.get("gdunit4_source", "")
    if not executable.is_file():
        runtime["missing"].append(f"Godot executable: {executable}")
    if not addon_source.is_dir() or not (addon_source / "plugin.cfg").is_file():
        runtime["missing"].append(f"gdUnit4 addon: {addon_source}")
    if runtime["missing"]:
        return runtime
    try:
        probe = subprocess.run(
            [str(executable), "--version"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        runtime["missing"].append(f"Godot version probe: {exc}")
        return runtime
    version = (probe.stdout or probe.stderr).strip()
    if probe.returncode != 0 or not _version_is_exact(version):
        runtime["missing"].append(
            f"Godot version mismatch: expected 4.6.1, observed {version!r}"
        )
        return runtime
    destination = sandbox / "addons" / "gdUnit4"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(addon_source, destination, dirs_exist_ok=True)
    project_file = sandbox / "project.godot"
    if not project_file.exists():
        project_file.write_text(
            "[application]\nconfig/name=\"Native Engine Evidence\"\n"
            "[rendering]\nrenderer/rendering_method=\"gl_compatibility\"\n",
            encoding="utf-8",
        )
    runtime.update({
        "available": True,
        "executable": str(executable),
        "version": version,
        "executable_sha256": _sha256(executable),
        "gdunit4_source": str(addon_source),
        "gdunit4_sha256": _tree_hash(addon_source),
        "gdunit4_sandbox_sha256": _tree_hash(destination),
        "observation": {"version_probe_returncode": probe.returncode},
    })
    return runtime


def _result_files(sandbox: Path) -> set[Path]:
    return {path for path in (sandbox / "reports").glob("**/results.xml") if path.is_file()}


def _parse_results(path: Path) -> dict:
    root = ET.parse(path).getroot()
    if root.tag not in {"testsuites", "testsuite"}:
        raise ValueError(f"unrecognized JUnit root element: {root.tag}")
    suites = [root] if root.tag == "testsuite" else list(root.findall(".//testsuite"))
    if not suites:
        raise ValueError("JUnit results contain no testsuite")
    required_root = ("tests", "failures", "skipped", "flaky")

    def count(element, key, required=True):
        raw = element.attrib.get(key)
        if raw is None:
            if required:
                raise ValueError(f"JUnit {element.tag} has missing {key} count")
            return None
        if not raw.isdecimal():
            raise ValueError(f"JUnit {element.tag} has invalid {key} count")
        return int(raw)

    def counts_for_suite(element):
        values = {}
        for key in ("tests", "failures", "errors", "skipped", "flaky"):
            values[key] = count(element, key)
        values["orphans"] = count(element, "orphans", required=False)
        return values

    root_counts = {key: count(root, key) for key in required_root}
    root_counts["errors"] = count(root, "errors", required=False)
    root_counts["orphans"] = count(root, "orphans", required=False)
    for value in root_counts.values():
        if value is not None and value < 0:
            raise ValueError("JUnit counts cannot be negative")

    aggregate = {key: 0 for key in ("tests", "failures", "errors", "skipped", "flaky")}
    for suite in suites:
        suite_counts = counts_for_suite(suite)
        if any(value is not None and value < 0 for value in suite_counts.values()):
            raise ValueError("JUnit counts cannot be negative")
        testcases = suite.findall(".//testcase")
        if len(testcases) != suite_counts["tests"]:
            raise ValueError("JUnit testsuite count does not match testcase elements")
        for key, tag in (("failures", "failure"), ("errors", "error"), ("skipped", "skipped")):
            nodes = suite.findall(f".//{tag}")
            if len(nodes) != suite_counts[key]:
                raise ValueError(f"JUnit testsuite {key} count does not match result elements")
        for key in aggregate:
            aggregate[key] += suite_counts[key]

    counts = dict(root_counts)
    for key in ("tests", "failures", "skipped", "flaky"):
        if aggregate[key] != root_counts[key]:
            raise ValueError(f"JUnit root {key} count does not match testsuite aggregate")
    if root_counts["errors"] is not None and aggregate["errors"] != root_counts["errors"]:
        raise ValueError("JUnit root errors count does not match testsuite aggregate")
    counts["errors"] = aggregate["errors"]
    if root_counts["orphans"] is None:
        counts["orphans"] = None
    return counts


def assess_engine(case: dict, sandbox: Path | str, runtime: dict | None) -> dict:
    """Run actual import/tests and classify fresh JUnit evidence."""
    sandbox = Path(sandbox)
    result = {"verified": [], "missing": [], "findings": [], "observation": {}}
    if runtime is None or case.get("engine_test") != "godot":
        result["missing"].append("Godot engine test is not configured")
        return result
    if not runtime.get("available"):
        result["missing"].extend(runtime.get("missing", ["Godot resources unavailable"]))
        return result
    source_files = list((sandbox / "src").rglob("*.gd"))
    test_files = list((sandbox / "tests").rglob("*.gd"))
    if not source_files:
        result["missing"].append("No produced GDScript source under src/")
    if not test_files:
        result["missing"].append("No produced tests under tests/")
    if result["missing"]:
        return result
    logs = sandbox / ".native-engine-evidence"
    logs.mkdir(parents=True, exist_ok=True)
    executable = runtime["executable"]

    def run(label: str, args: list[str], timeout: int = 120):
        started = time.time()
        try:
            completed = subprocess.run(
                [executable, *args], cwd=sandbox, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=timeout, check=False,
            )
            stdout = _decode_output(completed.stdout)
            stderr = _decode_output(completed.stderr)
            stdout_path = logs / f"{label}.stdout.log"
            stderr_path = logs / f"{label}.stderr.log"
            stdout_path.write_text(stdout, encoding="utf-8")
            stderr_path.write_text(stderr, encoding="utf-8")
            return completed.returncode, time.time() - started, [executable, *args], stdout_path, stderr_path
        except subprocess.TimeoutExpired as exc:
            stdout_path = logs / f"{label}.stdout.log"
            stderr_path = logs / f"{label}.stderr.log"
            stdout_path.write_text(_decode_output(exc.stdout), encoding="utf-8")
            stderr_path.write_text(_decode_output(exc.stderr), encoding="utf-8")
            return "timeout", time.time() - started, [executable, *args], stdout_path, stderr_path

    # Revalidate both prepared resources immediately before running the engine.
    executable_path = Path(runtime["executable"])
    addon_path = sandbox / "addons" / "gdUnit4"
    try:
        executable_hash = _sha256(executable_path)
        addon_hash = _tree_hash(addon_path)
        source_hash = _tree_hash(Path(runtime["gdunit4_source"]))
        probe = subprocess.run([str(executable_path), "--version"], capture_output=True,
                               text=True, encoding="utf-8", errors="replace", timeout=15, check=False)
        observed_version = (probe.stdout or probe.stderr).strip()
    except (OSError, subprocess.TimeoutExpired, KeyError) as exc:
        result["missing"].append(f"Prepared Godot resources could not be revalidated: {exc}")
        return result
    result["observation"].update({"version_command": [str(executable_path), "--version"],
                                  "version_probe_returncode": probe.returncode,
                                  "version": observed_version})
    if (executable_hash != runtime.get("executable_sha256") or
            addon_hash != runtime.get("gdunit4_sandbox_sha256") or
            source_hash != runtime.get("gdunit4_sha256") or
            probe.returncode != 0 or not _version_is_exact(observed_version) or
            observed_version != runtime.get("version")):
        result["missing"].append("Prepared Godot executable or gdUnit4 resources changed or failed exact-version revalidation")
        return result

    import_code, import_time, import_command, import_stdout, import_stderr = run("import", ["--headless", "--path", str(sandbox), "--import"])
    result["observation"].update({"import_exit": import_code, "import_seconds": round(import_time, 3),
                                  "import_command": import_command,
                                  "import_stdout_log": str(import_stdout),
                                  "import_stderr_log": str(import_stderr)})
    result["observation"].update({"import_stdout_sha256": _sha256(import_stdout),
                                  "import_stderr_sha256": _sha256(import_stderr)})
    if import_code == "timeout":
        result["findings"].append("Required Godot import timed out")
        return result
    if import_code != 0:
        result["findings"].append(f"Godot import exited {import_code}")
        return result
    before = {p: (_sha256(p), p.stat().st_mtime_ns) for p in _result_files(sandbox)}
    test_args = [arg.format(sandbox=sandbox) for arg in TEST_COMMAND]
    test_code, test_time, test_command, test_stdout, test_stderr = run("gdunit4", test_args)
    result["observation"].update({"test_exit": test_code, "test_seconds": round(test_time, 3),
                                  "test_command": test_command,
                                  "test_stdout_log": str(test_stdout),
                                  "test_stderr_log": str(test_stderr),
                                  "test_stdout_sha256": _sha256(test_stdout),
                                  "test_stderr_sha256": _sha256(test_stderr)})
    after = _result_files(sandbox)
    fresh = sorted((p for p in after if p not in before or
                    (p.stat().st_mtime_ns != before[p][1] or _sha256(p) != before[p][0])),
                   key=lambda p: p.stat().st_mtime_ns)
    if test_code == "timeout":
        result["findings"].append("Required gdUnit4 test run timed out")
        return result
    if test_code != 0:
        result["findings"].append(f"Required gdUnit4 test run exited {test_code}")
    if not fresh:
        result["missing"].append("No fresh gdUnit4 JUnit XML result")
        return result
    result_path = fresh[-1]
    try:
        counts = _parse_results(result_path)
    except (ET.ParseError, OSError, ValueError) as exc:
        result["missing"].append(f"Fresh gdUnit4 JUnit XML is malformed or unrecognized: {exc}")
        return result
    result["observation"].update({"junit": str(result_path), "counts": counts,
                                  "junit_sha256": _sha256(result_path)})
    if counts["tests"] == 0:
        result["missing"].append("Fresh gdUnit4 result contains zero tests")
        return result
    if any(counts[key] for key in ("errors", "failures", "skipped", "flaky")) or counts["orphans"] not in (None, 0):
        result["findings"].append(f"gdUnit4 result has nonzero counts: {counts}")
    if test_code != 0 and not any(counts[key] for key in ("errors", "failures", "skipped", "flaky", "orphans")):
        result["findings"].append(f"gdUnit4 exit {test_code} disagrees with clean JUnit result")
    if test_code == 0 and result["findings"]:
        result["findings"].append("gdUnit4 exit 0 disagrees with non-clean JUnit result")
    if not result["findings"]:
        result["verified"].append("engine_tests")
    return result
