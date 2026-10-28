"""Bounded, data-only verification of native PowerShell file-read receipts."""
from __future__ import annotations

import hashlib
import json
import ntpath
from pathlib import Path, PureWindowsPath
import re
from typing import Any


_READ = re.compile(
    r"\s*Microsoft\.PowerShell\.Management\\Get-Content\s+"
    r"-LiteralPath\s+'((?:[^']|'')*)'\s+-Raw\s+-Encoding\s+utf8\s*\Z",
    re.IGNORECASE,
)
_WRAPPER = re.compile(
    r'\s*"([^"\r\n]+)"\s+-Command\s+'
    r"(?:'((?:[^']|'')*)'|\"((?:\\.|[^\"\\])*)\")\s*\Z",
    re.IGNORECASE,
)
_HEX = re.compile(r"[0-9a-f]{64}\Z", re.IGNORECASE)


def _windows_path_under(path: PureWindowsPath, root: PureWindowsPath) -> bool:
    if (not path.drive or path.drive.casefold() != root.drive.casefold()
            or not path.is_absolute() or not root.is_absolute()):
        return False
    path_parts = tuple(part.casefold() for part in path.parts)
    root_parts = tuple(part.casefold() for part in root.parts)
    return len(path_parts) >= len(root_parts) and path_parts[:len(root_parts)] == root_parts


def _script(item: dict[str, Any], sandbox: Path) -> str | None:
    actions = item.get("commandActions")
    if (not isinstance(actions, list) or len(actions) != 1
            or not isinstance(actions[0], dict)
            or actions[0].get("type") != "unknown"):
        return None
    action = actions[0].get("command")
    raw = actions[0].get("rawCommand")
    if action is None:
        action = raw
    elif raw is not None and raw != action:
        return None
    if not isinstance(action, str):
        return None
    command = item.get("command")
    if not isinstance(command, str):
        return None
    wrapper = _WRAPPER.fullmatch(command)
    if wrapper:
        executable = PureWindowsPath(wrapper.group(1))
        if (not re.fullmatch(r"[a-z]:", executable.drive, re.IGNORECASE)
                or not executable.is_absolute()
                or any(part in {".", ".."} for part in executable.parts)):
            return None
        roots = (PureWindowsPath(str(Path(sandbox).absolute())),
                 PureWindowsPath(str(Path(sandbox).resolve())))
        if any(root.drive and _windows_path_under(executable, root) for root in roots):
            return None
        if not re.fullmatch(r"pwsh(?:\.exe)?", executable.name, re.IGNORECASE):
            return None
        if wrapper.group(2) is not None:
            wrapped = wrapper.group(2).replace("''", "'")
        else:
            try:
                wrapped = json.loads('"' + wrapper.group(3) + '"')
            except json.JSONDecodeError:
                return None
        return action if wrapped == action else None
    # Small protocol fixtures may provide the literal script without a process wrapper.
    return action if command == action else None


def _safe_relative_path(value: str, sandbox: Path) -> str | None:
    normalized = _literal_path(value)
    if normalized is None:
        return None
    root = Path(sandbox).resolve()
    try:
        candidate = root.joinpath(*normalized.split("/")).resolve()
    except (OSError, RuntimeError):
        return None
    try:
        candidate.relative_to(root)
    except (OSError, ValueError):
        return None
    return normalized if candidate.is_file() else None


def _literal_path(value: str) -> str | None:
    if not value or "\x00" in value:
        return None
    normalized = value.replace("\\", "/")
    windows = PureWindowsPath(value)
    if (windows.is_absolute() or windows.drive or ntpath.splitdrive(value)[0]
            or normalized.startswith("/") or any(part in {"", ".", ".."} for part in normalized.split("/"))):
        return None
    return normalized


def _read_cwd(item: dict[str, Any], sandbox: Path) -> Path | None:
    root = Path(sandbox).resolve()
    if "cwd" not in item:
        return root
    value = item.get("cwd")
    if not isinstance(value, str) or not value:
        return None
    cwd = Path(value)
    if not cwd.is_absolute():
        return None
    try:
        resolved = cwd.resolve()
        resolved.relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return None
    return resolved


def _read_path(value: str, sandbox: Path, cwd: Path) -> str | None:
    literal = _literal_path(value)
    if literal is None:
        return None
    root = Path(sandbox).resolve()
    try:
        candidate = cwd.joinpath(*literal.split("/")).resolve()
        relative = candidate.relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return None
    return relative.as_posix() if candidate.is_file() else None


def powershell_read_path(item: dict[str, Any], sandbox: Path) -> str | None:
    """Return the safe relative path for one exact, canonical literal read receipt."""
    if not isinstance(item, dict):
        return None
    script = _script(item, Path(sandbox))
    if script is None:
        return None
    match = _READ.fullmatch(script)
    if not match:
        return None
    literal = match.group(1).replace("''", "'")
    cwd = _read_cwd(item, Path(sandbox))
    return None if cwd is None else _read_path(literal, Path(sandbox), cwd)


def _display_text(value: str) -> str:
    value = value.replace("\r\n", "\n")
    return value[1:] if value.startswith("\ufeff") else value


def _output_matches(output: Any, content: str) -> bool:
    if not isinstance(output, str):
        return False
    actual, expected = _display_text(output), _display_text(content)
    return actual == expected or actual == expected + "\n"


def verified_read_inputs(thread: dict[str, Any], expected: dict[str, Any], sandbox: Path) -> bool:
    """Verify all expected inputs against completed child read receipts and current bytes."""
    if not isinstance(thread, dict) or not isinstance(expected, dict) or not expected:
        return False
    root = Path(sandbox).resolve()
    receipts: dict[str, list[dict[str, Any]]] = {}
    for turn in thread.get("turns", []):
        if not isinstance(turn, dict):
            continue
        for item in turn.get("items", []):
            if not isinstance(item, dict) or item.get("type") != "commandExecution":
                continue
            path = powershell_read_path(item, root)
            if path is not None:
                receipts.setdefault(path, []).append(item)
    for raw_path, value in expected.items():
        if not isinstance(raw_path, str) or not isinstance(value, dict):
            return False
        safe_path = _safe_relative_path(raw_path, root)
        if safe_path is None or safe_path != raw_path.replace("\\", "/"):
            return False
        digest, content = value.get("sha256"), value.get("content")
        if not isinstance(digest, str) or not _HEX.fullmatch(digest) or not isinstance(content, str):
            return False
        try:
            encoded = content.encode("utf-8")
            current = (root / safe_path).read_bytes()
        except (OSError, UnicodeEncodeError):
            return False
        if hashlib.sha256(encoded).hexdigest().casefold() != digest.casefold():
            return False
        if hashlib.sha256(current).hexdigest().casefold() != digest.casefold():
            return False
        if not any(item.get("status") == "completed" and item.get("exitCode") == 0
                   and _output_matches(item.get("aggregatedOutput"), content)
                   for item in receipts.get(safe_path, [])):
            return False
    return True
