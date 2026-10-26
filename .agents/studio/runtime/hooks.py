#!/usr/bin/env python3
"""Native Codex hook adapter: observations/checks, never model or project writes."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

from context import code_roots, helper, project_root
from state import atomic_bytes, file_lock, lock_path, StateError
from checks.business import check as business_check
from updates import notice as update_notice


def emit(event: str, message: str, deny: bool = False) -> None:
    specific = {"hookEventName": event}
    if event == "PreToolUse":
        specific["additionalContext"] = message
        if deny:
            specific.update(permissionDecision="deny", permissionDecisionReason=message)
    elif event in {"SessionStart", "PostToolUse", "SubagentStart"}:
        specific["additionalContext"] = message
    # Stop/SubagentStop require a JSON object on successful exit.
    output = {"systemMessage": message}
    if event in {"PreToolUse", "SessionStart", "PostToolUse", "SubagentStart"}:
        output["hookSpecificOutput"] = specific
    print(json.dumps(output, ensure_ascii=True))


def read_input() -> dict:
    data = json.load(sys.stdin)
    if not isinstance(data, dict):
        raise ValueError("hook input must be a JSON object")
    return data


def record(root: Path, kind: str, payload: dict) -> None:
    canonical = json.dumps(payload, ensure_ascii=True, sort_keys=True).encode("utf-8")
    key = hashlib.sha256(canonical + kind.encode()).hexdigest()
    target = root / ".scratch/runtime/receipts" / f"{key}.json"
    with file_lock(lock_path(root, target), timeout=0.4):
        if not target.exists():
            identity = {key: payload[key] for key in
                        ("session_id", "turn_id", "event_id", "agent_id", "tool_use_id",
                         "tool_call_id", "hook_event_name", "tool_name") if key in payload}
            atomic_bytes(target, json.dumps({"kind": kind, "time": time.time(),
                                             "identity": identity,
                                             "payload_sha256": hashlib.sha256(canonical).hexdigest()},
                                            ensure_ascii=True).encode("utf-8"))


def bounded_stop(root: Path, payload: dict) -> bool:
    target = root / ".scratch/runtime/stop-count.json"
    with file_lock(lock_path(root, target), timeout=0.4):
        counts = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
        key = hashlib.sha256((str(payload.get("session_id", "unknown")) + ":" +
                              str(payload.get("turn_id", "unknown"))).encode()).hexdigest()
        count = counts.get(key, 0)
        if count >= 2:
            return False
        counts[key] = count + 1
        atomic_bytes(target, json.dumps(counts).encode())
    return True


def tool_input(data):
    inp = data.get("tool_input", {})
    if not isinstance(inp, dict):
        return {"command": str(inp)}
    # Native payloads use command; accept compatible executor spellings when
    # present so the guard remains fail-closed without claiming they are the
    # canonical host payload.
    if "command" not in inp:
        for key in ("cmd", "freeform_input", "input"):
            if key in inp:
                return {**inp, "command": inp[key]}
    return inp


def tool_name(data):
    return str(data.get("tool_name", "")).rsplit(".", 1)[-1]


def write_paths(data: dict, root: Path) -> list[tuple[Path, str]]:
    tool = tool_name(data)
    inp = tool_input(data)
    paths = []
    if tool in {"apply_patch", "ApplyPatch"}:
        patch = str(inp.get("command", inp.get("patch", "")))
        for line in patch.splitlines():
            if line.startswith(("*** Add File: ", "*** Update File: ",
                                "*** Delete File: ", "*** Move to: ")):
                paths.append(line.split(": ", 1)[1].strip())
    elif tool in {"Write", "Edit"}:
        paths.append(str(inp.get("file_path", inp.get("path", ""))))
    cwd = Path(data.get("cwd") or os.getcwd()).resolve()
    result = []
    for name in paths:
        if not name:
            continue
        target = (cwd / name.replace("\\", "/")).resolve()
        try:
            relative = target.relative_to(root).as_posix()
        except ValueError:
            raise ValueError("Write target is outside the active project root")
        result.append((target, relative))
    return result


def tool_guard(data: dict, root: Path) -> tuple[str, bool] | None:
    inp = tool_input(data)
    command = str(inp.get("command", ""))
    if tool_name(data) == "Read" and inp.get("file_path"):
        target = (Path(data.get("cwd") or root) / inp["file_path"]).resolve()
        try:
            relative = target.relative_to(root).as_posix()
        except ValueError:
            # External references are legitimate read inputs.  The read-size
            # helper only understands project-relative paths; containment is
            # still strict for writes below.
            relative = None
        if relative is not None:
            bounded = "yes" if inp.get("offset") is not None or inp.get("limit") is not None else "no"
            result = helper(root, ".agents/studio/scripts/read-guard.sh", "--root", str(root),
                            "check", relative, "--bounded", bounded)
            if result.returncode:
                return "Read-size check NOT ASSESSED: " + result.stderr.strip(), True
            if any(line.startswith("LARGE\t") for line in result.stdout.splitlines()):
                return f"Read {relative} by heading/section with a bounded range; it exceeds the configured whole-document limit.", True
    if re.search(r"\bgit(?:\.exe)?\s+(?:-[Cc]\s+\S+\s+)*push\b", command, re.I):
        if re.search(r"(?:^|\s)(?:--force(?:-with-lease)?|-f)(?:\s|=|$)", command):
            return "Destructive force-push is outside the studio's ordinary authorized workflow.", True
    try:
        paths = write_paths(data, root)
    except ValueError as exc:
        return str(exc), True
    if paths and data.get("permission_mode") == "plan":
        return "Plan activity is read-only; no file write was authorized.", True
    configured = None
    for target, relative in paths:
        if relative.startswith("production/session-state/"):
            return "Developmental checkpoints are updated by the coordinator CLI, not file tools.", True
        if target.suffix.lower() in {".gd", ".cs", ".cpp", ".h", ".hpp", ".gdshader", ".shader",
                                     ".ts", ".tsx", ".js", ".jsx"}:
            if relative.startswith((".agents/", ".codex/", "studio-tests/", "tests/", "addons/")):
                continue
            configured = code_roots(root)
            if not configured:
                return "Engine is not configured; run ccgs-setup-engine before writing engine code.", True
            valid = tuple(prefix + "/" for prefix in configured)
            if "Assets" in configured:
                valid += ("Packages/",)
            # Cocos may expose packages/server roots; generated/shared trees
            # are intentionally absent from the resolver's authoritative rows.
            if not relative.startswith(valid):
                return f"Engine code must use a configured code root ({', '.join(configured)}/).", True
    return None


def observations(root: Path, data: dict, after=False) -> list[str]:
    messages = []
    paths = write_paths(data, root)
    for target, relative in paths:
        if after and relative.startswith(("assets/", "Assets/", "Content/")):
            if re.search(r"(?:^|/)[Dd]ata/.*\.json$", relative, re.I) and target.is_file():
                try:
                    json.loads(target.read_text(encoding="utf-8-sig"))
                except (ValueError, UnicodeError) as exc:
                    messages.append(f"FAIL: asset data JSON {relative}: {exc}")
            if relative.startswith("assets/") and re.search(r"[A-Z\s-]", target.name):
                messages.append(f"Asset naming concern: {relative}; use the project's Godot naming convention.")
        if after and relative.startswith(".agents/skills/"):
            messages.append("Studio skill changed; run ccgs-skill-test static and the framework checks.")
    if paths:
        messages.extend(business_check(root, data, paths, after=after))
    return messages


def main() -> int:
    event = "Unknown"
    try:
        data = read_input()
        event = str(data.get("hook_event_name", "Unknown"))
        try:
            root = project_root(str(data.get("cwd") or os.getcwd()))
        except (ValueError, OSError) as exc:
            emit(event, f"NOT ASSESSED: studio runtime is not bound to this project: {exc}")
            return 0
        if event == "PreToolUse":
            decision = tool_guard(data, root)
            if decision:
                emit(event, *decision)
                return 0
            notes = []
            command = str(tool_input(data).get("command", ""))
            if tool_name(data) in {"Bash", "PowerShell", "Shell", "exec_command"} and "git" in command.lower() and "commit" in command.lower():
                canonical = dict(data)
                canonical["tool_input"] = tool_input(data)
                result = helper(root, ".agents/studio/runtime/checks/validate-commit.sh",
                                stdin=json.dumps(canonical), timeout=20)
                if result.returncode:
                    emit(event, result.stderr.strip() or "Commit validation could not complete.", True)
                    return 0
                if result.stdout.strip():
                    try:
                        message = json.loads(result.stdout).get("hookSpecificOutput", {}).get("additionalContext", "")
                    except ValueError:
                        message = result.stdout.strip()
                    if message:
                        notes.append(message)
            notes.extend(observations(root, data))
            if notes:
                emit(event, "\n".join(notes))
        elif event == "SessionStart":
            notes = [f"Studio project: {root}; native hook event observed.",
                     "Read the current checkpoint and resolve configuration before resuming.",
                     "Role files/configured hooks do not prove native role execution or trust of other definitions."]
            checkpoint = root / "production/session-state/active.md"
            if checkpoint.exists():
                notes.append("Recovery checkpoint available: production/session-state/active.md")
            if not (root / "design").exists():
                notes.append("Design is absent; use ccgs-start to select the next supported step.")
            if data.get("source") in {"startup", "resume", "clear", "fork"}:
                notes.append(update_notice(root))
            emit(event, "\n".join(notes))
            record(root, event, data)
        elif event in {"PreCompact", "PostCompact"}:
            emit(event, f"Resume {root} from its current branch/stories/checkpoint; this hook does not update the checkpoint.")
            record(root, event, data)
        elif event in {"Stop", "SubagentStop", "SubagentStart", "SessionEnd", "Interrupt"}:
            if event in {"Stop", "Interrupt"} and not bounded_stop(root, data):
                emit(event, "Stop re-entry bound reached. No continuation was started.")
                return 0
            record(root, event, data)
            emit(event, f"{event} observed; coordinator validates artifacts and owns checkpoint updates. No continuation was started.")
        elif event == "PostToolUse":
            record(root, event, data)
            notes = observations(root, data, after=True)
            if notes:
                emit(event, "\n".join(notes))
        return 0
    except (ValueError, OSError, StateError, subprocess.SubprocessError) as exc:
        if event in {"Stop", "SubagentStop", "Interrupt", "SessionEnd", "PreCompact", "PostCompact"}:
            emit(event, f"NOT ASSESSED: runtime observation failed: {exc}; no continuation requested.")
            return 0
        if event == "PreToolUse":
            emit(event, f"NOT ASSESSED: the required pre-tool check could not complete: {exc}", True)
            return 0
        print(json.dumps({"error": str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
