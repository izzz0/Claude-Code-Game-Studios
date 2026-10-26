#!/usr/bin/env python3
"""Coordinator-owned team records. This CLI does not spawn or attest agents."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tomllib

STUDIO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDIO / "runtime"))
from state import StateError, atomic_bytes, digest, file_lock, lock_path, root_path, safe_target


def slug(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", value):
        raise StateError("run/task id must be a simple slug, without path separators")
    return value


def snapshot(root, name):
    target = safe_target(root, name)
    if not target.is_file():
        raise StateError(f"returned artifact is missing: {name}")
    return {"path": target.relative_to(root).as_posix(), "sha256": digest(target)}


def overlaps(left, right):
    a, b = Path(left), Path(right)
    return a == b or a in b.parents or b in a.parents


def resume(data, root):
    ready, blocked, revalidate = [], [], []
    for name, task in data["tasks"].items():
        missing = [d for d in task["depends_on"] if data["tasks"][d]["status"] != "completed"]
        if task["status"] in {"pending", "failed", "interrupted"}:
            (blocked if missing else ready).append({"task": name, "dependencies": missing})
        for artifact in task.get("artifacts", []):
            if digest(safe_target(root, artifact["path"])) != artifact["sha256"]:
                revalidate.append({"task": name, "path": artifact["path"]})
    return {"ready": ready, "blocked": blocked, "revalidate": revalidate,
            "running": [n for n, t in data["tasks"].items() if t["status"] == "running"],
            "note": "Reconcile running IDs with the host; records are not proof of native execution."}


def change(args, data, root):
    if args.command == "assign":
        slug(args.task)
        profile = STUDIO.parents[1] / ".codex/agents" / f"{args.role}.toml"
        if not profile.is_file() or tomllib.loads(profile.read_text(encoding="utf-8"))["name"] != args.role:
            raise StateError(f"unknown native role: {args.role}")
        files = sorted({safe_target(root, f).relative_to(root).as_posix() for f in args.files})
        deps = sorted(set(args.depends_on))
        if args.task in deps or any(d not in data["tasks"] for d in deps):
            raise StateError("dependencies must name existing, different tasks")
        task = {"role": args.role, "files": files, "read_only": args.read_only,
                "depends_on": deps, "status": "pending", "agent_id": None,
                "summary": "", "artifacts": [], "events": []}
        if args.task in data["tasks"]:
            old = data["tasks"][args.task]
            keys = ("role", "files", "read_only", "depends_on")
            if any(old[k] != task[k] for k in keys):
                raise StateError("task already exists with a different assignment", 3)
            return False
        data["tasks"][args.task] = task
        return True
    task = data["tasks"].get(args.task)
    if task is None:
        raise StateError("unknown task")
    artifacts = [snapshot(root, name) for name in args.artifact]
    identity = json.dumps([args.status, args.agent_id, args.summary, artifacts], sort_keys=True)
    event = hashlib.sha256(identity.encode()).hexdigest()
    if task["events"] and task["events"][-1] == event:
        return False
    if args.status == "running":
        if task["status"] not in {"pending", "failed", "interrupted"}:
            raise StateError("task must be pending, failed or interrupted before starting", 3)
        if not args.agent_id:
            raise StateError("running requires the actual native agent id")
        if any(data["tasks"][d]["status"] != "completed" for d in task["depends_on"]):
            raise StateError("task dependencies are incomplete", 3)
        active = [t for t in data["tasks"].values() if t["status"] == "running"]
        if len(active) >= data["host_limit"]:
            raise StateError("host concurrency limit reached", 3)
        if not task["read_only"]:
            for other in active:
                if not other["read_only"] and any(overlaps(a, b) for a in task["files"] for b in other["files"]):
                    raise StateError("another running task owns these files", 3)
        task["agent_id"] = args.agent_id
    else:
        if args.status == "completed":
            if task["status"] != "running" or args.agent_id != task["agent_id"]:
                raise StateError("completion must match a running native agent id", 3)
        elif task["status"] not in {"pending", "running"}:
            raise StateError("failure/interruption must refer to pending or running work", 3)
        if task["status"] == "running" and args.agent_id != task["agent_id"]:
            raise StateError("event agent id does not match the running assignment", 3)
        if not args.summary.strip():
            raise StateError("completion/failure/interruption requires a substantive returned summary")
    task.update(status=args.status, summary=args.summary, artifacts=artifacts)
    task["events"].append(event)
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--id", required=True)
    init.add_argument("--team", required=True)
    init.add_argument("--size", choices=("individual", "small", "studio"), required=True)
    init.add_argument("--host-limit", type=int, required=True)
    assign = sub.add_parser("assign")
    assign.add_argument("--id", required=True)
    assign.add_argument("--task", required=True)
    assign.add_argument("--role", required=True)
    assign.add_argument("--files", nargs="*", default=[])
    assign.add_argument("--read-only", action="store_true")
    assign.add_argument("--depends-on", nargs="*", default=[])
    event = sub.add_parser("event")
    event.add_argument("--id", required=True)
    event.add_argument("--task", required=True)
    event.add_argument("--status", choices=("running", "completed", "failed", "interrupted"), required=True)
    event.add_argument("--agent-id")
    event.add_argument("--summary", default="")
    event.add_argument("--artifact", action="append", default=[])
    for command in ("show", "resume"):
        p = sub.add_parser(command)
        p.add_argument("--id", required=True)
    args = parser.parse_args(argv)
    try:
        root = root_path(args.root)
        target = safe_target(root, f"production/team-runs/{slug(args.id)}.json")
        if args.command in {"show", "resume"}:
            data = json.loads(target.read_text(encoding="utf-8"))
            print(json.dumps(data if args.command == "show" else resume(data, root), ensure_ascii=True))
            return 0
        with file_lock(lock_path(root, target)):
            data = json.loads(target.read_text(encoding="utf-8")) if target.exists() else None
            if args.command == "init":
                if args.host_limit < 1:
                    raise StateError("host limit must be positive")
                route = args.team.removeprefix("ccgs-")
                if not (STUDIO.parent / "skills" / f"ccgs-{route}" / "SKILL.md").is_file() or not route.startswith("team-"):
                    raise StateError("unknown team")
                proposed = {"schema": 1, "id": args.id, "team": route, "size": args.size,
                            "host_limit": args.host_limit, "revision": 0, "tasks": {}}
                if data and any(data[k] != proposed[k] for k in ("team", "size", "host_limit")):
                    raise StateError("run already exists with different configuration", 3)
                changed = data is None
                data = data or proposed
            else:
                if data is None:
                    raise StateError("initialize the run first")
                changed = change(args, data, root)
            if changed:
                data["revision"] += 1
                atomic_bytes(target, (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        print(json.dumps({"ok": True, "unchanged": not changed, "revision": data["revision"],
                          "path": str(target), "execution_attested": False}))
        return 0
    except (OSError, ValueError, StateError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return exc.code if isinstance(exc, StateError) else 2


if __name__ == "__main__":
    raise SystemExit(main())
