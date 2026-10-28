"""Evidence checks for native team acceptance.

This module only consumes host receipts and coordinator manifests.  It never
spawns agents, reads model claims, or treats a coordinator event as a completed
child turn by itself.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import tomllib
from typing import Any

from native_reads import powershell_read_path, verified_read_inputs


_CONTINUATIONS = {"resumeAgent", "followupTask", "sendInput"}


def _thread(value: Any) -> dict[str, Any]:
    if isinstance(value, dict) and isinstance(value.get("thread"), dict):
        return value["thread"]
    return value if isinstance(value, dict) else {}


def _status(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return str(value.get("type", value.get("status", "")))
    return ""


def _ids(item: dict[str, Any]) -> list[str]:
    return [str(x) for x in item.get("receiverThreadIds", []) if isinstance(x, str)]


def _role_is_configured(role: str, sandbox: Path) -> bool:
    if not isinstance(role, str) or not re.fullmatch(r"ccgs-[A-Za-z0-9-]+", role):
        return False
    path = sandbox / ".codex" / "agents" / f"{role}.toml"
    try:
        return path.is_file() and tomllib.loads(path.read_text(encoding="utf-8")).get("name") == role
    except (OSError, tomllib.TOMLDecodeError):
        return False


def _final_substantive(thread: dict[str, Any]) -> bool:
    if _status(thread.get("status")) not in {"idle", "notLoaded"}:
        return False
    turns = thread.get("turns", [])
    if not turns or not isinstance(turns[-1], dict) or turns[-1].get("status") != "completed":
        return False
    if turns[-1].get("itemsView", "full") != "full":
        return False
    return any(
        item.get("type") == "agentMessage"
        and item.get("phase") in (None, "final_answer")
        and isinstance(item.get("text"), str)
        and item["text"].strip()
        for item in turns[-1].get("items", [])
    )


def _final_response_text(thread: dict[str, Any]) -> str:
    turns = thread.get("turns", [])
    if not turns or not isinstance(turns[-1], dict) or turns[-1].get("status") != "completed":
        return ""
    return "\n".join(
        item.get("text", "") for item in turns[-1].get("items", [])
        if item.get("type") == "agentMessage"
        and item.get("phase") in (None, "final_answer")
        and isinstance(item.get("text"), str)
    ).strip()


def _writer_turn_intervals(thread: dict[str, Any]) -> list[tuple[float, float]] | None:
    turns = thread.get("turns", [])
    if not turns or not isinstance(turns[-1], dict) or turns[-1].get("status") != "completed":
        return None
    intervals = []
    for turn in turns:
        started, completed = turn.get("startedAt"), turn.get("completedAt")
        if not isinstance(started, (int, float)) or not isinstance(completed, (int, float)) or completed < started:
            return None
        intervals.append((float(started), float(completed)))
    return intervals


def _intervals_overlap(left: tuple[float, float], right: tuple[float, float]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def _spawn_receipts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item for item in items
        if item.get("type") == "collabAgentToolCall"
        and item.get("tool") == "spawnAgent"
        and item.get("status") == "completed"
    ]


def _activity_receipts(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Collect native lifecycle evidence keyed by authoritative child UUID."""
    activities: dict[str, list[dict[str, Any]]] = {}
    for index, item in enumerate(items):
        if (item.get("type") != "subAgentActivity"
                or item.get("kind") not in {"started", "interrupted", "interacted", "completed"}):
            continue
        child_id = item.get("agentThreadId")
        if not isinstance(child_id, str) or not child_id or child_id != child_id.strip():
            continue
        activities.setdefault(child_id, []).append({**item, "_order": index})
    return activities


def _native_aliases(child_threads: dict[str, Any], activities: dict[str, list[dict[str, Any]]], parent_thread_id: str, sandbox: Path) -> dict[str, str | None]:
    """Return exact host agent paths that unambiguously identify a child."""
    candidates: dict[str, set[str]] = {}
    for child_id, raw in child_threads.items():
        thread = _thread(raw)
        source = thread.get("source")
        source = source.get("subAgent") if isinstance(source, dict) else None
        source = source.get("thread_spawn") if isinstance(source, dict) else None
        path = source.get("agent_path") if isinstance(source, dict) else None
        role = thread.get("agentRole")
        if (not isinstance(source, dict) or thread.get("id") != child_id or thread.get("parentThreadId") != parent_thread_id
                or source.get("parent_thread_id") != parent_thread_id
                or source.get("agent_role") != role
                or not isinstance(path, str) or not path.strip()
                or not isinstance(role, str) or not _role_is_configured(role, sandbox)):
            continue
        if not any(event.get("kind") == "started" and event.get("agentPath") == path
                   for event in activities.get(child_id, [])):
            continue
        candidates.setdefault(path, set()).add(child_id)
    return {path: next(iter(ids)) if len(ids) == 1 else None for path, ids in candidates.items()}


def _activity_matches_thread(child_id: str, thread: dict[str, Any], events: list[dict[str, Any]],
                             parent_thread_id: str) -> bool:
    source = thread.get("source")
    source = source.get("subAgent") if isinstance(source, dict) else None
    source = source.get("thread_spawn") if isinstance(source, dict) else None
    if not isinstance(source, dict):
        return False
    path, role = source.get("agent_path"), thread.get("agentRole")
    return bool(
        thread.get("id") == child_id
        and thread.get("parentThreadId") == parent_thread_id
        and source.get("parent_thread_id") == parent_thread_id
        and source.get("agent_role") == role
        and isinstance(path, str) and path.strip()
        and any(event.get("kind") == "started" and event.get("agentPath") == path for event in events)
    )


def _activity_metadata_contradicts_thread(thread: dict[str, Any], events: list[dict[str, Any]],
                                         parent_thread_id: str) -> bool:
    source = thread.get("source")
    source = source.get("subAgent") if isinstance(source, dict) else None
    source = source.get("thread_spawn") if isinstance(source, dict) else None
    if not isinstance(source, dict):
        return False
    path, role, parent = source.get("agent_path"), source.get("agent_role"), source.get("parent_thread_id")
    if parent is not None and parent != parent_thread_id:
        return True
    if role is not None and role != thread.get("agentRole"):
        return True
    if path is not None and (not isinstance(path, str) or not any(
            event.get("kind") == "started" and event.get("agentPath") == path for event in events)):
        return True
    return False


def _manifest_child_id(value: Any, child_ids: set[str], aliases: dict[str, str | None]) -> str | None:
    if isinstance(value, str) and value in child_ids:
        return value
    return aliases.get(value) if isinstance(value, str) else None


def _manifest_paths(sandbox: Path) -> list[tuple[Path, Path]]:
    paths = [
        (sandbox / "production" / "team-runs", sandbox),
        (sandbox / ".scratch" / "team-observations" / "production" / "team-runs",
         sandbox / ".scratch" / "team-observations"),
    ]
    found: list[tuple[Path, Path]] = []
    for directory, root in paths:
        if directory.is_dir():
            found.extend((path, root) for path in sorted(directory.glob("*.json")))
    return list(dict.fromkeys(found))


def _review_manifest_paths(sandbox: Path) -> list[tuple[Path, Path]]:
    """Return review manifests and the coordination root they were authored under."""
    coordination_root = sandbox / ".scratch" / "team-observations"
    directory = coordination_root / "production" / "team-runs"
    if not directory.is_dir():
        return []
    return [(path, coordination_root) for path in sorted(directory.glob("*.json"))]


def _digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_path(sandbox: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        return None
    root = sandbox.resolve()
    candidate = (sandbox / value).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _cwd_within_sandbox(thread: dict[str, Any], sandbox: Path) -> bool:
    cwd = thread.get("cwd")
    if not isinstance(cwd, str):
        return False
    try:
        Path(cwd).resolve().relative_to(sandbox.resolve())
        return True
    except (OSError, ValueError):
        return False


def _has_file_change(thread: dict[str, Any]) -> bool:
    return any(
        isinstance(item, dict) and item.get("type") == "fileChange"
        for turn in thread.get("turns", []) if isinstance(turn, dict)
        for item in turn.get("items", [])
    )


def _full_history(thread: dict[str, Any]) -> bool:
    turns = thread.get("turns")
    return isinstance(turns, list) and all(
        isinstance(turn, dict) and turn.get("itemsView", "full") == "full" for turn in turns
    )


def _has_unproven_command(thread: dict[str, Any], sandbox: Path) -> bool:
    safe_actions = {"read", "listFiles", "search"}
    for turn in thread.get("turns", []):
        for item in turn.get("items", []) if isinstance(turn, dict) else []:
            if item.get("type") != "commandExecution":
                continue
            actions = item.get("commandActions")
            if powershell_read_path(item, sandbox) is not None:
                continue
            if not isinstance(actions, list) or not actions:
                return True
            if any(not isinstance(action, dict) or action.get("type") not in safe_actions for action in actions):
                return True
    return False


def _review_inputs_match(prompt: Any, expected: dict[str, Any]) -> bool:
    if not isinstance(prompt, str) or not expected:
        return False
    start_marker, end_marker = "CCGS_REVIEW_INPUTS", "CCGS_REVIEW_INPUTS_END"
    start, end = prompt.find(start_marker), prompt.find(end_marker)
    if start < 0 or end < start + len(start_marker):
        return False
    payload = prompt[start + len(start_marker):end].strip()
    try:
        bundle = json.loads(payload)
    except (TypeError, json.JSONDecodeError):
        return False
    if not isinstance(bundle, dict) or set(bundle) != set(expected):
        return False
    for path, value in expected.items():
        if not isinstance(value, dict) or not isinstance(value.get("sha256"), str) or not isinstance(value.get("content"), str):
            return False
        entry = bundle.get(path)
        if not isinstance(entry, dict) or entry.get("sha256") != value["sha256"] or not isinstance(entry.get("content"), str):
            return False
        if hashlib.sha256(entry["content"].encode("utf-8")).hexdigest() != value["sha256"]:
            return False
    return True


def _manifest_evidence(sandbox: Path, child_roles: dict[str, str], child_threads: dict[str, Any] | None = None,
                       aliases: dict[str, str | None] | None = None,
                       required_child_ids: set[str] | None = None) -> tuple[bool, list[str]]:
    manifests = _manifest_paths(sandbox)
    if not manifests:
        return False, []
    findings: list[str] = []
    valid_manifest = False
    missing_readonly_proof = False
    child_ids = set(child_roles)
    aliases = aliases or {}
    child_threads = child_threads or {}
    missing_intervals = False
    for path, manifest_root in manifests:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(f"team manifest unreadable: {path.name} ({exc})")
            continue
        tasks = data.get("tasks")
        if not isinstance(tasks, dict) or not tasks:
            findings.append(f"team manifest has no tasks: {path.name}")
            continue
        manifest_ok = True
        matched_ids: list[str] = []
        owned_files: dict[str, tuple[str, str, bool]] = {}
        writer_intervals: dict[str, list[tuple[str, tuple[float, float]]]] = {}
        for name, task in tasks.items():
            if not isinstance(task, dict):
                findings.append(f"team manifest task is not an object: {name}")
                manifest_ok = False
                continue
            agent_id = _manifest_child_id(task.get("agent_id"), child_ids, aliases)
            if (agent_id is None and isinstance(task.get("agent_id"), str)
                    and task.get("agent_id") in aliases and aliases[task["agent_id"]] is None):
                findings.append(f"team task {name} native agent path alias is ambiguous")
            role = task.get("role")
            if agent_id not in child_ids:
                manifest_ok = False
            elif child_roles[agent_id] != role:
                findings.append(f"team task {name} role does not match child receipt")
                manifest_ok = False
            else:
                matched_ids.append(agent_id)
            if not isinstance(task.get("read_only"), bool):
                findings.append(f"team task {name} has invalid read_only semantics")
                manifest_ok = False
            elif task["read_only"]:
                child = _thread(child_threads.get(agent_id))
                if _has_file_change(child):
                    findings.append(f"read-only team task {name} has a fileChange receipt")
                    manifest_ok = False
                if not _full_history(child) or _has_unproven_command(child, sandbox):
                    missing_readonly_proof = True
            files = task.get("files", [])
            if not isinstance(files, list):
                findings.append(f"team task {name} has malformed ownership files")
                manifest_ok = False
                files = []
            for file_value in files:
                safe_file = _safe_path(manifest_root, file_value)
                if safe_file is None:
                    findings.append(f"team task {name} has an unsafe ownership path")
                    manifest_ok = False
                    continue
                key = safe_file.as_posix()
                current_status = task.get("status")
                if (key in owned_files and current_status == "running"
                        and owned_files[key][1] == "running"
                        and not task.get("read_only", False)
                        and not owned_files[key][2]):
                    findings.append(f"team task {name} overlaps ownership with {owned_files[key][0]}")
                    manifest_ok = False
                else:
                    owned_files[key] = (name, current_status, task.get("read_only", False))
                if current_status == "completed" and not task.get("read_only", False):
                    intervals = _writer_turn_intervals(_thread(child_threads.get(agent_id)))
                    if intervals is None:
                        missing_intervals = True
                    else:
                        for previous_path, previous_writers in writer_intervals.items():
                            previous = Path(previous_path)
                            if previous != safe_file and previous not in safe_file.parents and safe_file not in previous.parents:
                                continue
                            for previous_id, previous_interval in previous_writers:
                                if previous_id != agent_id and any(_intervals_overlap(previous_interval, interval) for interval in intervals):
                                    findings.append(f"team task {name} overlaps completed writer {previous_id}")
                                    manifest_ok = False
                        writer_intervals.setdefault(key, []).extend((agent_id, interval) for interval in intervals)
            if task.get("status") != "completed":
                findings.append(f"team task {name} is {task.get('status', 'missing')}")
                manifest_ok = False
            if not isinstance(task.get("summary"), str) or not task["summary"].strip():
                findings.append(f"team task {name} has no substantive summary")
                manifest_ok = False
            for dependency in task.get("depends_on", []):
                if dependency not in tasks or tasks[dependency].get("status") != "completed":
                    findings.append(f"team task {name} has unresolved dependency {dependency}")
                    manifest_ok = False
            for artifact in task.get("artifacts", []):
                if not isinstance(artifact, dict) or not isinstance(artifact.get("path"), str) or not isinstance(artifact.get("sha256"), str):
                    findings.append(f"team task {name} has malformed artifact receipt")
                    manifest_ok = False
                    continue
                artifact_path = _safe_path(manifest_root, artifact["path"])
                if artifact_path is None or not artifact_path.is_file() or _digest(artifact_path) != artifact["sha256"]:
                    findings.append(f"team task {name} has missing or stale artifact hash")
                    manifest_ok = False
        if (set(matched_ids) == set(child_roles) and len(set(matched_ids)) == len(child_roles)
                and (not required_child_ids or required_child_ids.issubset(matched_ids)) and manifest_ok):
            valid_manifest = True
    if not valid_manifest and child_roles:
        findings.append("no team manifest crossmatches every completed child role")
    if missing_intervals or missing_readonly_proof:
        valid_manifest = False
    return valid_manifest, findings


def _recovery_evidence(sandbox: Path, items: list[dict[str, Any]], child_threads: dict[str, Any],
                       parent_thread_id: str, aliases: dict[str, str | None] | None = None) -> tuple[bool, list[str]]:
    aliases = aliases or {}
    activities = _activity_receipts(items)
    for child_id, events in activities.items():
        started = [event for event in events if event.get("kind") == "started"]
        interrupted_events = [event for event in events if event.get("kind") == "interrupted"]
        interacted = [event for event in events if event.get("kind") == "interacted"]
        completed = [event for event in events if event.get("kind") == "completed"]
        thread = _thread(child_threads.get(child_id))
        if thread.get("id") != child_id or thread.get("parentThreadId") != parent_thread_id:
            continue
        if not _cwd_within_sandbox(thread, sandbox):
            continue
        if not _activity_matches_thread(child_id, thread, events, parent_thread_id):
            continue
        interrupted_turns = [
            (pos, turn) for pos, turn in enumerate(thread.get("turns", []))
            if isinstance(turn, dict) and turn.get("status") in {"interrupted", "failed"}
        ]
        turns = thread.get("turns", [])
        if not turns or not isinstance(turns[-1], dict):
            continue
        final_turn = turns[-1]
        start_time, finish_time = final_turn.get("startedAt"), final_turn.get("completedAt")
        if (not started or not interrupted_events or not interacted or not completed
                or final_turn.get("status") != "completed"
                or not isinstance(start_time, (int, float)) or not isinstance(finish_time, (int, float))
                or finish_time < start_time):
            continue
        turn_id = final_turn.get("id")
        completed_events = [event for event in completed
                            if event.get("id") == f"subagent-completed-{turn_id}"]
        if not completed_events:
            continue
        ordered = any(
            launch["_order"] < interruption["_order"] < interaction["_order"] < receipt["_order"]
            for launch in started for interruption in interrupted_events
            for interaction in interacted for receipt in completed_events
        )
        earlier_interruption = any(
            pos < len(turns) - 1
            and isinstance(turn.get("startedAt"), (int, float))
            and isinstance(turn.get("completedAt"), (int, float))
            and turn["startedAt"] <= turn["completedAt"] <= start_time
            for pos, turn in interrupted_turns
        )
        if not ordered or not earlier_interruption or not _final_substantive(thread):
            continue
        role = thread.get("agentRole")
        if not isinstance(role, str) or not _role_is_configured(role, sandbox):
            continue
        manifest_roles = {
            candidate_id: _thread(raw).get("agentRole")
            for candidate_id, raw in child_threads.items()
            if _thread(raw).get("id") == candidate_id
            and _thread(raw).get("parentThreadId") == parent_thread_id
            and _cwd_within_sandbox(_thread(raw), sandbox)
            and isinstance(_thread(raw).get("agentRole"), str)
            and _role_is_configured(_thread(raw).get("agentRole"), sandbox)
            and _final_substantive(_thread(raw))
        }
        if child_id not in manifest_roles:
            continue
        manifest_ok, _ = _manifest_evidence(sandbox, manifest_roles, child_threads, aliases,
                                            required_child_ids={child_id})
        if manifest_ok:
            return True, []

    interrupted: dict[str, int] = {}
    running_before: dict[str, int] = {}
    continuations: list[tuple[int, set[str]]] = []
    completed_after_resume: dict[str, set[int]] = {}
    for index, item in enumerate(items):
        if item.get("type") != "collabAgentToolCall" or item.get("status") != "completed":
            continue
        if item.get("senderThreadId") != parent_thread_id:
            continue
        ids = set(_ids(item))
        states = item.get("agentsStates", {})
        for child_id in ids:
            if _status(states.get(child_id)) == "running":
                running_before.setdefault(child_id, index)
        if item.get("tool") == "interruptAgent" or any(_status(states.get(i)) in {"interrupted", "errored"} for i in ids):
            for child_id in ids:
                interrupted.setdefault(child_id, index)
        if item.get("tool") in _CONTINUATIONS:
            continuations.append((index, ids))
        if item.get("tool") in _CONTINUATIONS | {"wait"}:
            for child_id in ids:
                if _status(states.get(child_id)) == "completed":
                    completed_after_resume.setdefault(child_id, set()).add(index)
    for index, ids in continuations:
        for child_id in ids:
            if child_id not in interrupted or index <= interrupted[child_id]:
                continue
            thread = _thread(child_threads.get(child_id))
            turns = thread.get("turns", [])
            interrupted_turns = [
                (pos, turn.get("id")) for pos, turn in enumerate(turns)
                if isinstance(turn, dict) and turn.get("status") in {"interrupted", "failed"}
            ]
            later_completed = any(
                isinstance(turn, dict) and turn.get("status") == "completed"
                and turn.get("id") != failed_id and pos > failed_pos
                for failed_pos, failed_id in interrupted_turns
                for pos, turn in enumerate(turns)
            )
            has_manifest_task = False
            for manifest, _manifest_root in _manifest_paths(sandbox):
                try:
                    data = json.loads(manifest.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                has_manifest_task = any(
                    isinstance(task, dict)
                    and _manifest_child_id(task.get("agent_id"), {child_id}, aliases) == child_id
                    and task.get("status") == "completed"
                    for task in (data.get("tasks") or {}).values()
                )
                if has_manifest_task:
                    break
            if (thread.get("id") == child_id and thread.get("parentThreadId") == parent_thread_id
                    and child_id in running_before and running_before[child_id] < interrupted[child_id]
                    and interrupted_turns and later_completed
                    and _final_substantive(thread) and has_manifest_task
                    and any(done > index for done in completed_after_resume.get(child_id, set()))):
                return True, []
    if not interrupted:
        return False, []
    return False, ["recovery receipt lacks a post-resume completed host state for the same child and matching manifest task"]


def verify_team_evidence(
    sandbox: str | Path,
    items: list[dict[str, Any]],
    child_threads: dict[str, Any],
    parent_thread_id: str,
) -> dict[str, list[str]]:
    """Verify host-backed native-agent and recovery evidence.

    Missing evidence is reported in ``missing`` (the caller keeps it NA). A
    ``findings`` entry means receipts were present but contradicted each other.
    """
    root = Path(sandbox)
    verified: list[str] = []
    missing: list[str] = []
    findings: list[str] = []
    spawns = _spawn_receipts(items)
    activities = _activity_receipts(items)
    aliases = _native_aliases(child_threads, activities, parent_thread_id, root)
    legacy_ids = {child_id for spawn in spawns for child_id in _ids(spawn)}
    modern_ids = {child_id for child_id, events in activities.items()
                  if any(event.get("kind") == "started" for event in events)}
    required_ids = legacy_ids | modern_ids
    child_roles: dict[str, str] = {}
    if not required_ids:
        missing.append("native_agents")
        _, manifest_findings = _manifest_evidence(root, child_roles)
        findings.extend(manifest_findings)
    else:
        if not required_ids.issubset(child_threads):
            missing.append("native_agents")
        for spawn in spawns:
            if spawn.get("senderThreadId") != parent_thread_id:
                findings.append("spawn receipt has wrong sender thread")
        for child_id in required_ids:
            thread = _thread(child_threads.get(child_id))
            if not thread:
                continue
            if thread.get("id") != child_id:
                findings.append(f"child receipt ID does not match spawn or activity ID {child_id}")
                continue
            if thread.get("parentThreadId") != parent_thread_id:
                findings.append(f"child {child_id} has wrong parent thread")
                continue
            if not _cwd_within_sandbox(thread, root):
                findings.append(f"child {child_id} cwd is outside the acceptance sandbox")
                continue
            role = thread.get("agentRole")
            if not isinstance(role, str) or not _role_is_configured(role, root):
                findings.append(f"child {child_id} has unknown or unconfigured native role")
                continue
            has_legacy_proof = child_id in legacy_ids and any(
                spawn.get("senderThreadId") == parent_thread_id and child_id in _ids(spawn) for spawn in spawns
            )
            source_present = thread.get("source") is not None
            if child_id in modern_ids and not has_legacy_proof:
                if not _activity_matches_thread(child_id, thread, activities[child_id], parent_thread_id):
                    findings.append(f"child {child_id} activity path or role does not match host thread metadata")
                    continue
            elif child_id in modern_ids and source_present and _activity_metadata_contradicts_thread(
                    thread, activities[child_id], parent_thread_id):
                findings.append(f"child {child_id} activity metadata contradicts host thread metadata")
                continue
            if not _final_substantive(thread):
                findings.append(f"child {child_id} has no completed substantive final turn")
                continue
            child_roles[child_id] = role
        if len(child_roles) == len(required_ids) and not findings:
            manifests_ok, manifest_findings = _manifest_evidence(root, child_roles, child_threads, aliases)
            findings.extend(manifest_findings)
            if manifests_ok and not findings:
                verified.append("native_agents")
            else:
                missing.append("native_agents")
        else:
            missing.append("native_agents")
    recovery_ok, recovery_findings = _recovery_evidence(root, items, child_threads, parent_thread_id, aliases)
    if recovery_ok:
        verified.append("team_recovery")
    else:
        missing.append("team_recovery")
        findings.extend(recovery_findings)
    return {"verified": verified, "missing": missing, "findings": findings}


def verify_review_evidence(
    sandbox: str | Path,
    items: list[dict[str, Any]],
    child_threads: dict[str, Any],
    parent_thread_id: str,
    input_hashes: dict[str, dict[str, str]] | None = None,
) -> dict[str, list[str]]:
    """Verify an independent, read-only native review receipt.

    Review manifests are authored with ``team-run.py --root
    .scratch/team-observations``; therefore their paths and hashes are resolved
    against that coordination root, while child identity/cwd is checked against
    the acceptance sandbox.
    """
    root = Path(sandbox)
    verified: list[str] = []
    missing: list[str] = []
    findings: list[str] = []
    spawns = _spawn_receipts(items)
    activities = _activity_receipts(items)
    aliases = _native_aliases(child_threads, activities, parent_thread_id, root)
    candidates: list[tuple[str, dict[str, Any] | None]] = []
    seen_candidates: set[str] = set()
    for spawn in spawns:
        for child_id in _ids(spawn):
            if child_id not in seen_candidates:
                candidates.append((child_id, spawn))
                seen_candidates.add(child_id)
    for child_id, events in activities.items():
        if child_id not in seen_candidates and any(event.get("kind") == "started" for event in events):
            candidates.append((child_id, None))
            seen_candidates.add(child_id)
    if not candidates:
        return {"verified": [], "missing": ["independent_review"], "findings": []}
    manifests = _review_manifest_paths(root)
    if not manifests:
        return {"verified": [], "missing": ["independent_review"], "findings": []}
    for child_id, spawn in candidates:
            if spawn is not None and spawn.get("senderThreadId") != parent_thread_id:
                findings.append("review spawn receipt has wrong sender thread")
                continue
            raw = child_threads.get(child_id)
            if raw is None:
                continue
            thread = _thread(raw)
            if _has_file_change(thread):
                findings.append(f"review child {child_id} has a fileChange receipt")
                continue
            if not _full_history(thread):
                continue
            if input_hashes:
                prompt_bound = spawn is not None and _review_inputs_match(spawn.get("prompt"), input_hashes)
                read_bound = spawn is None and verified_read_inputs(thread, input_hashes, root)
                if not (prompt_bound or read_bound):
                    continue
            if thread.get("id") != child_id or thread.get("parentThreadId") != parent_thread_id:
                findings.append(f"review child {child_id} has mismatched identity")
                continue
            if not _cwd_within_sandbox(thread, root):
                findings.append(f"review child {child_id} cwd is outside the acceptance sandbox")
                continue
            role = thread.get("agentRole")
            if not isinstance(role, str) or not _role_is_configured(role, root):
                findings.append(f"review child {child_id} has unknown or unconfigured native role")
                continue
            if spawn is None and not _activity_matches_thread(child_id, thread, activities[child_id], parent_thread_id):
                findings.append(f"review child {child_id} activity path or role does not match host thread metadata")
                continue
            if (spawn is not None and child_id in activities
                    and any(event.get("kind") == "started" for event in activities[child_id])
                    and thread.get("source") is not None
                    and _activity_metadata_contradicts_thread(thread, activities[child_id], parent_thread_id)):
                findings.append(f"review child {child_id} activity metadata contradicts host thread metadata")
                continue
            if _has_unproven_command(thread, root):
                continue
            if not _final_substantive(thread):
                findings.append(f"review child {child_id} has no completed substantive final turn")
                continue
            final_text = _final_response_text(thread)
            if not re.search(r"\b(?:PASS|CONCERNS|FAIL|APPROVED|CHANGES REQUIRED|NEEDS REVISION)\b", final_text, re.IGNORECASE):
                findings.append(f"review child {child_id} has no explicit meaningful verdict")
                continue
            for manifest_path, coordination_root in manifests:
                try:
                    data = json.loads(manifest_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    findings.append(f"review manifest unreadable: {manifest_path.name}")
                    continue
                tasks = data.get("tasks")
                if not isinstance(tasks, dict):
                    continue
                for task in tasks.values():
                    if not isinstance(task, dict) or _manifest_child_id(task.get("agent_id"), {child_id}, aliases) != child_id:
                        continue
                    if task.get("role") != role:
                        findings.append(f"review task for {child_id} role does not match host agent role")
                        continue
                    if task.get("status") != "completed" or task.get("read_only") is not True:
                        findings.append(f"review task for {child_id} is not completed read-only")
                        continue
                    if not isinstance(task.get("summary"), str) or not task["summary"].strip():
                        findings.append(f"review task for {child_id} has no substantive summary")
                        continue
                    artifacts = task.get("artifacts", [])
                    if not isinstance(artifacts, list) or not artifacts:
                        findings.append(f"review task for {child_id} has no retained artifact")
                        continue
                    artifacts_ok = True
                    for artifact in artifacts:
                        if not isinstance(artifact, dict):
                            artifacts_ok = False
                            break
                        artifact_path = _safe_path(coordination_root, artifact.get("path"))
                        if (artifact_path is None or not artifact_path.is_file()
                                or _digest(artifact_path) != artifact.get("sha256")):
                            artifacts_ok = False
                            break
                        try:
                            if final_text not in artifact_path.read_text(encoding="utf-8"):
                                artifacts_ok = False
                                break
                        except (OSError, UnicodeDecodeError):
                            artifacts_ok = False
                            break
                    if artifacts_ok:
                        verified.append("independent_review")
                        return {"verified": verified, "missing": [], "findings": findings}
    missing.append("independent_review")
    return {"verified": verified, "missing": missing, "findings": findings}
