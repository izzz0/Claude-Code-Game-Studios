"""Paths and process environment shared by repository-local runtime helpers."""
from pathlib import Path
import os
import shutil
import subprocess
import sys

FRAMEWORK_ROOT = Path(__file__).resolve().parents[3]


def bash_executable() -> str:
    configured = os.environ.get("CCGS_BASH")
    candidates = [Path(configured)] if configured else []
    found = shutil.which("bash")
    if found and "windowsapps" not in found.lower():
        candidates.append(Path(found))
    git = shutil.which("git")
    if git:
        candidates.append(Path(git).resolve().parent.parent / "bin/bash.exe")
    for key in ("ProgramFiles", "ProgramW6432", "LOCALAPPDATA"):
        if os.environ.get(key):
            candidates.append(Path(os.environ[key]) / "Git/bin/bash.exe")
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise OSError("Git Bash/POSIX Bash is unavailable; configure CCGS_BASH explicitly")


def project_root(cwd: str) -> Path:
    here = Path(cwd).resolve()
    here.relative_to(FRAMEWORK_ROOT)
    # No child process on short lifecycle deadlines. A Git worktree's .git
    # marker may be a file, so test existence rather than is_dir().
    for candidate in (here, *here.parents):
        if (candidate / ".git").exists():
            if candidate != FRAMEWORK_ROOT:
                raise ValueError("Nested/foreign Git worktree requires its own studio runtime")
            break
        if candidate == FRAMEWORK_ROOT:
            break
    for candidate in (here, *here.parents):
        if (candidate / "project.yaml").is_file() or (candidate / "project.local.yaml").is_file():
            return candidate
        if candidate == FRAMEWORK_ROOT:
            break
    raise ValueError("No project configuration inside the bound framework worktree")


def helper(root: Path, name: str, *arguments: str, timeout: int = 5, stdin=None):
    env = os.environ.copy()
    env["CCGS_PROJECT_DIR"] = str(root)
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    env["PYTHONUTF8"] = "1"
    return subprocess.run([bash_executable(), str(FRAMEWORK_ROOT / name), *arguments],
                          cwd=root, env=env, input=stdin, capture_output=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def code_roots(root: Path) -> list[str]:
    """Return only roots confirmed by the project's existing YAML resolver.

    Cocos projects can have several authoritative roots, emitted as TSV rows by
    ``resolve_code_roots``.  The singular resolver remains the compatibility
    path for Godot/Unity/Unreal and intentionally does not guess when engine
    configuration is absent.
    """
    plural = helper(root, ".agents/studio/hooks/yaml-helper.sh", "resolve_code_roots")
    if plural.returncode != 0:
        return []
    if plural.stdout.strip():
        confirmed = []
        root = Path(root).resolve()
        for row in plural.stdout.splitlines():
            fields = row.split("\t", 1)
            if len(fields) != 2 or fields[1].strip() in {"detected", "unset"}:
                return []
            raw = fields[0].strip().replace("\\", "/")
            candidate = (root / raw).resolve()
            if not raw or Path(raw).is_absolute() or ".." in Path(raw).parts:
                return []
            try:
                candidate.relative_to(root)
            except ValueError:
                return []
            if not candidate.is_dir():
                return []
            confirmed.append(candidate.relative_to(root).as_posix())
        return confirmed
    result = helper(root, ".agents/studio/hooks/yaml-helper.sh", "resolve_code_root")
    value, separator, origin = result.stdout.strip().partition("\t")
    if result.returncode or not separator or origin in {"detected", "unset"}:
        return []
    return [value] if value in {"src", "Assets", "Source"} else []


def code_root(root: Path) -> str | None:
    """Backwards-compatible first configured code root."""
    roots = code_roots(root)
    return roots[0] if roots else None
