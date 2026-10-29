"""Daily upstream release notice, cached only inside this project."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.request

from context import FRAMEWORK_ROOT, helper
from state import atomic_bytes, file_lock, lock_path
from state import StateError

URL = "https://api.github.com/repos/Donchitos/Claude-Code-Game-Studios/releases/latest"


def refresh(root):
    path = root / ".scratch/runtime/update-status.json"
    result = {"checked": time.time(), "status": "NOT ASSESSED"}
    try:
        request = urllib.request.Request(URL, headers={"Accept": "application/vnd.github+json",
                                                     "User-Agent": "Codex-Game-Studios"})
        with urllib.request.urlopen(request, timeout=8) as response:
            tag = json.load(response)["tag_name"].removeprefix("v")
        if not re.fullmatch(r"\d+\.\d+\.\d+", tag):
            raise ValueError("unrecognized upstream release tag")
        result.update(status="OBSERVED", upstream=tag)
    except Exception as exc:
        result["error"] = str(exc)
    with file_lock(lock_path(root, path)):
        atomic_bytes(path, json.dumps(result).encode("utf-8"))


def notice(root):
    # This optional observation must not discard the session's recovery context.
    try:
        return _notice(Path(root))
    except (OSError, ValueError, StateError, subprocess.SubprocessError) as exc:
        return f"Upstream update check NOT ASSESSED: {exc}"


def _notice(root):
    if os.environ.get("CI") or os.environ.get("CCGS_OFFLINE"):
        return "Upstream update check not run in CI/offline mode."
    resolved = helper(root, ".agents/studio/hooks/yaml-helper.sh", "resolve_setting", "updates.check")
    if resolved.returncode:
        return "Upstream update check NOT ASSESSED: configuration could not be resolved."
    value = resolved.stdout.split("\t", 1)[0].strip()
    if value in {"false", "off"}:
        return ""
    path = root / ".scratch/runtime/update-status.json"
    with file_lock(lock_path(root, path), timeout=0.2):
        try:
            cached = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cached = {}
        checked = cached.get("checked", 0) if isinstance(cached, dict) else None
        if not isinstance(checked, (int, float)) or isinstance(checked, bool):
            return "Upstream update check NOT ASSESSED: invalid project cache timestamp."
        age = time.time() - checked
        if age < 0 or age >= 86400:
            atomic_bytes(path, json.dumps({"checked": time.time(), "status": "CHECKING"}).encode())
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            try:
                subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--root", str(root)],
                                 cwd=root, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, creationflags=flags, close_fds=True)
            except OSError as exc:
                atomic_bytes(path, json.dumps({"checked": time.time(), "status": "NOT ASSESSED",
                                               "error": str(exc)}).encode())
            return "Upstream release refresh scheduled; no compatibility or upgrade was asserted."
    latest = cached.get("upstream")
    if cached.get("status") == "OBSERVED" and latest:
        if not isinstance(latest, str) or not re.fullmatch(r"\d+\.\d+\.\d+", latest):
            return "Upstream update check NOT ASSESSED: invalid cached release version."
        local = (FRAMEWORK_ROOT / ".agents/studio/VERSION").read_text().strip().split("-", 1)[0]
        if tuple(map(int, latest.split("."))) > tuple(map(int, local.split("."))):
            return f"Upstream release {latest} is available. This Codex fork needs manual compatibility review; no automatic upgrade."
        return f"Cached upstream release: {latest}; this is not a Codex compatibility assessment."
    return "Upstream version NOT ASSESSED: " + cached.get("error", "refresh pending")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    refresh(Path(args.root).resolve())
