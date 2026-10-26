#!/usr/bin/env python3
"""Run selected native skill cases through Codex app-server, preserving host policy.

Launch from a normal user terminal. No hook trust, model, permission, provider,
global configuration, or CODEX_HOME override is made by this driver.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid

HERE = Path(__file__).resolve().parent
FRAMEWORK = HERE.parents[1]
sys.path.insert(0, str(FRAMEWORK / ".agents/studio/runtime"))
from state import atomic_bytes, file_lock, lock_path
from context import helper


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    atomic_bytes(Path(path), (json.dumps(value, ensure_ascii=True, indent=2) + "\n").encode())


def tree_hashes(root):
    ignored = {".scratch", ".git", ".godot", "__pycache__"}
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(Path(root).rglob("*"))
            if p.is_file() and not ignored.intersection(p.relative_to(root).parts)}


def instruction_hashes(project):
    """Hash applicable project/ancestor instructions, including absent files."""
    result = {}
    directory = Path(project).resolve()
    while True:
        for name in ("AGENTS.md", "AGENTS.local.md"):
            path = directory / name
            result[str(path)] = sha(path) if path.is_file() else None
        parent = directory.parent
        if parent == directory:
            break
        directory = parent
    return result


def safe_path(root, relative):
    target = (Path(root) / relative).resolve()
    target.relative_to(Path(root).resolve())
    return target


def check_hooks(listing, project):
    source = (Path(project) / ".codex/hooks.json").resolve()
    config = json.loads(source.read_text(encoding="utf-8"))
    normalize = lambda value: "".join(c for c in value.lower() if c.isalnum())
    expected = {normalize(name) for name in config["hooks"]}
    hooks = [hook for row in listing.get("data", []) for hook in row.get("hooks", [])
             if hook.get("sourcePath") and Path(hook["sourcePath"]).resolve() == source]
    reasons = []
    if {normalize(h["eventName"]) for h in hooks} != expected:
        reasons.append("The exact project's hook source was not fully discovered; check worktree discovery and project trust.")
    if any(not h.get("enabled") or h.get("trustStatus") != "trusted" for h in hooks):
        reasons.append("Project hooks require human review of their current definitions in /hooks.")
    return reasons


def copy_case_resources(project, sandbox):
    """Copy framework resources and role profiles, never project hook/config files."""
    shutil.copytree(project / ".agents/studio", sandbox / ".agents/studio")
    skills = project / ".agents/skills"
    if skills.is_dir():
        shutil.copytree(skills, sandbox / ".agents/skills")
    roles = project / ".codex/agents"
    if roles.is_dir():
        shutil.copytree(roles, sandbox / ".codex/agents")
    reference = sandbox / "docs/engine-reference"
    if not reference.exists() and (project / "docs/engine-reference").is_dir():
        shutil.copytree(project / "docs/engine-reference", reference)


def assess(case, sandbox, before, response, items, hooks, transport_status):
    """Transport completion, fixture checks, and missing evidence stay separate."""
    fail, missing = [], []
    if transport_status != "completed":
        missing.append("Native turn did not complete: " + transport_status)
    if any(h.get("status") != "completed" for h in hooks):
        fail.append("A native project hook failed or was interrupted.")
    if not hooks:
        missing.append("No native project hook completion was observed.")
    commands = [i for i in items if i.get("type") == "commandExecution"]
    if any(i.get("exitCode") == -1 or "sandbox provisioning failed" in i.get("aggregatedOutput", "")
           for i in commands):
        missing.append("The host could not provision the tool sandbox.")
    if case["expected"].get("required_tools") and not any(
            i.get("status") == "completed" and i.get("exitCode") == 0 for i in commands):
        missing.append("No successful native shell inspection was observed.")
    after = tree_hashes(sandbox)
    if case.get("readonly") and before != after:
        fail.append("Read-only case changed protected sandbox files.")
    if transport_status != "completed":
        return {"status": "FAIL" if fail else "NOT ASSESSED", "findings": fail,
                "missing": missing, "artifacts": {}, "protected_hashes": after}
    expected = case["expected"]
    for text in expected.get("response_contains", []):
        if text.casefold() not in response.casefold():
            fail.append("Missing expected finding: " + text)
    for text in expected.get("response_not_contains", []):
        if text.casefold() in response.casefold():
            fail.append("Forbidden response claim: " + text)
    if "response_commands" in expected:
        navigation, inventory = [], False
        for line in response.splitlines():
            heading = re.match(r"\s*#{1,6}\s+(.+)", line)
            if heading:
                inventory = heading.group(1).casefold().startswith("also installed")
            # Exclude only the documented non-action inventory bullet shape.
            # Instructions appended below that footer remain navigation text.
            if inventory and re.match(r"\s*[-*]\s+`?\$ccgs-[a-z0-9-]+`?\s*[—–:-]", line, re.I):
                continue
            navigation.append(line)
        commands = set(re.findall(r"\$(ccgs-[a-z0-9-]+)", "\n".join(navigation), re.I))
        if {name.casefold() for name in commands} != set(expected["response_commands"]):
            fail.append("Workflow command set differs from the required single handoff: " + ", ".join(sorted(commands)))
    artifacts = {}
    for spec in expected.get("files", []):
        path = safe_path(sandbox, spec["path"])
        if not path.is_file():
            fail.append("Missing artifact: " + spec["path"])
            continue
        text = path.read_text(encoding="utf-8-sig")
        artifacts[spec["path"]] = sha(path)
        for token in spec.get("contains", []):
            if token not in text:
                fail.append(f"{spec['path']}: missing {token}")
        for token in spec.get("not_contains", []):
            if token in text:
                fail.append(f"{spec['path']}: forbidden {token}")
        if spec.get("changed") is True and before.get(spec["path"]) == artifacts[spec["path"]]:
            fail.append("Expected artifact was not changed: " + spec["path"])
        if spec.get("changed") is False and before.get(spec["path"]) != artifacts[spec["path"]]:
            fail.append("Preserved artifact changed: " + spec["path"])
    for spec in expected.get("counts", []):
        safe_path(sandbox, spec["glob"])
        actual_count = sum(path.is_file() for path in Path(sandbox).glob(spec["glob"]))
        if actual_count != spec["count"]:
            fail.append(f"{spec['glob']}: expected {spec['count']} files, found {actual_count}")
    for key, expected_value in expected.get("config", {}).items():
        result = helper(Path(sandbox), ".agents/studio/hooks/yaml-helper.sh", "get_yaml_key",
                        str(Path(sandbox) / "project.yaml"), key)
        if result.returncode:
            missing.append("Original configuration parser could not verify " + key)
        elif result.stdout.strip() != expected_value:
            fail.append(f"Configuration mismatch for {key}: {result.stdout.strip()!r}")
    # These evidence classes need their own actual execution/reviewer records.
    # A keyword in the model's response never satisfies them.
    required = case.get("required_evidence", expected.get("required_evidence", []))
    missing.extend("Separate evidence required: " + name for name in required)
    if not case.get("readonly") and before == after:
        fail.append("Authoring case produced no file changes.")
    # Host failure prevents assessing skill semantics, even if its response lacks
    # the expected domain finding. A failed hook remains a confirmed failure.
    status = "FAIL" if any("hook" in x or "Read-only" in x for x in fail) else (
        "NOT ASSESSED" if missing else "FAIL" if fail else "PASS")
    return {"status": status, "findings": fail, "missing": missing,
            "artifacts": artifacts, "protected_hashes": after}


class Attention(Exception):
    pass


class Client:
    def __init__(self, executable, project, output):
        self.events, self.serial, self.queue = [], 0, queue.Queue()
        self.log = (output / "host-events.jsonl").open("a", encoding="utf-8")
        self.stderr = (output / "host-stderr.log").open("a", encoding="utf-8")
        options = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
        self.process = subprocess.Popen([executable, "app-server"], cwd=project,
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=self.stderr, text=True, encoding="utf-8",
                                        bufsize=1, **options)
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def _read(self):
        for line in self.process.stdout:
            try:
                value = json.loads(line)
            except ValueError:
                continue
            self.log.write(json.dumps(value, ensure_ascii=True) + "\n")
            self.log.flush()
            self.events.append(value)
            self.queue.put(value)
        self.queue.put({"_closed": True})

    def receive(self, timeout):
        value = self.queue.get(timeout=timeout)
        if value.get("_closed"):
            raise Attention("Native host exited; inspect host-stderr.log.")
        if "id" in value and "method" in value:
            raise Attention("Human interaction required: " + value["method"])
        return value

    def request(self, method, params):
        self.serial += 1
        request_id = self.serial
        self.process.stdin.write(json.dumps({"id": request_id, "method": method, "params": params}) + "\n")
        self.process.stdin.flush()
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            value = self.receive(max(.01, deadline - time.monotonic()))
            if value.get("id") == request_id:
                if "error" in value:
                    raise Attention(method + ": " + json.dumps(value["error"]))
                return value["result"]
        raise Attention("Native request timed out: " + method)

    def notify(self, method):
        self.process.stdin.write(json.dumps({"method": method}) + "\n")
        self.process.stdin.flush()

    def close(self):
        self.process.stdin.close()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        self.reader.join(timeout=3)
        self.log.close()
        self.stderr.close()


def run_case(client, project, output, case, timeout):
    attempt = output / "cases" / case["id"] / uuid.uuid4().hex[:12]
    sandbox = attempt / "project"
    fixture = safe_path(HERE / "fixtures", case["fixture"])
    shutil.copytree(fixture, sandbox)
    # Skill commands retain their repository-relative resource layout. Case
    # projects have no foreign Git marker; the trusted host layer is the parent.
    copy_case_resources(project, sandbox)
    before = tree_hashes(sandbox)
    start_index = len(client.events)
    thread = client.request("thread/start", {"cwd": str(sandbox), "ephemeral": True})
    tid = thread["thread"]["id"]
    write_json(attempt / "thread.json", thread)
    skill = project / ".agents/skills" / case["skill"] / "SKILL.md"
    instruction = ("This is an isolated native acceptance case. Execute the named skill with actual tools. "
                   "Respond in English. Preserve inherited model/provider/permissions; never approve hook trust "
                   "or alter global settings. Work only in this case project. Review and plan operations "
                   "are read-only. Do not assert evidence you have not observed.\n" + case["prompt"])
    client.request("turn/start", {"threadId": tid, "input": [
        {"type": "skill", "name": case["skill"], "path": str(skill)},
        {"type": "text", "text": instruction}]})
    deadline = time.monotonic() + timeout
    transport_status = "timeout"
    native_error = None
    while time.monotonic() < deadline:
        try:
            value = client.receive(min(10, max(.01, deadline - time.monotonic())))
        except queue.Empty:
            continue
        if value.get("method") == "turn/completed" and value.get("params", {}).get("threadId") == tid:
            transport_status = value["params"]["turn"]["status"]
            native_error = value["params"]["turn"].get("error")
            break
    if transport_status == "timeout":
        # Stop the batch; do not start more work while a timed-out turn is live.
        raise Attention(f"Case {case['id']} timed out; thread {tid}; evidence retained at {attempt}")
    events = [e for e in client.events[start_index:] if e.get("params", {}).get("threadId") == tid]
    items = [e["params"]["item"] for e in events if e.get("method") == "item/completed"]
    hooks = [e["params"]["run"] for e in events if e.get("method") == "hook/completed"
             and e["params"]["run"].get("source") == "project"]
    response = "\n".join(i.get("text", "") for i in items if i.get("type") == "agentMessage"
                         and i.get("phase") in {None, "final_answer"})
    (attempt / "response.txt").write_text(response, encoding="utf-8")
    write_json(attempt / "events.json", events)
    result = assess(case, sandbox, before, response, items, hooks, transport_status)
    if native_error:
        result["native_error"] = native_error
        result["missing"].append("Native host: " + native_error.get("message", "unspecified error"))
    result.update(id=case["id"], skill=case["skill"], thread_id=tid,
                  transport_status=transport_status, sandbox=str(sandbox),
                  attempt=str(attempt), response_sha256=sha(attempt / "response.txt"),
                  model=thread.get("model"), reasoning_effort=thread.get("reasoningEffort"),
                  events_sha256=sha(attempt / "events.json"),
                  thread_sha256=sha(attempt / "thread.json"),
                  native_agent_ids=sorted({child for i in items if i.get("type") == "collabAgentToolCall"
                                           for child in i.get("receiverThreadIds", [])}))
    write_json(attempt / "result.json", result)
    return result


def can_resume(record, fingerprint):
    if record.get("status") != "PASS" or record.get("source_fingerprint") != fingerprint:
        return False
    try:
        if sha(Path(record["attempt"]) / "response.txt") != record["response_sha256"]:
            return False
        if sha(Path(record["attempt"]) / "events.json") != record["events_sha256"]:
            return False
        if sha(Path(record["attempt"]) / "thread.json") != record["thread_sha256"]:
            return False
        if tree_hashes(Path(record["sandbox"])) != record["protected_hashes"]:
            return False
        return all(sha(safe_path(record["sandbox"], path)) == digest
                   for path, digest in record["artifacts"].items())
    except (OSError, ValueError, KeyError):
        return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--codex", default=shutil.which("codex"))
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args(argv)
    project = args.project.resolve()
    catalog = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))
    cases = catalog["cases"]
    if args.list:
        print(json.dumps({"authored": [c["skill"] for c in cases], "coverage": catalog.get("coverage")}, ensure_ascii=True))
        return 0
    if not args.codex:
        parser.error("Supply the installed Codex executable with --codex.")
    if not (project / ".git").is_dir():
        parser.error("Native acceptance requires an ordinary Git clone (.git directory), not a linked worktree.")
    selected = cases if args.all else [c for c in cases if c["id"] in args.case or c["skill"] in (args.case or ["ccgs-help"])]
    if not selected:
        parser.error("No authored case matches; use --list.")
    output = (args.output or project / ".scratch/native-acceptance").resolve()
    output.relative_to(project)
    output.mkdir(parents=True, exist_ok=True)
    codex_version = subprocess.check_output([args.codex, "--version"], text=True).strip()
    codex_executable = Path(shutil.which(args.codex) or args.codex).resolve()
    inputs = {"agents": tree_hashes(project / ".agents"),
              "instructions": instruction_hashes(project),
              "codex": tree_hashes(project / ".codex"), "fixtures": tree_hashes(HERE / "fixtures"),
              "engine_references": tree_hashes(project / "docs/engine-reference"),
              "catalog": sha(HERE / "cases.json"), "driver": sha(__file__),
              "host_version": codex_version, "host_executable": str(codex_executable),
              "host_binary": sha(codex_executable)}
    fingerprint = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    state_path = output / "state.json"
    # One batch per output directory; OS locks release after crashes.
    with file_lock(lock_path(project, state_path), timeout=.2):
        state = json.loads(state_path.read_text()) if args.resume and state_path.exists() else {"cases": {}}
        state["source_revision"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=project, text=True).strip()
        state["source_branch"] = subprocess.check_output(["git", "branch", "--show-current"], cwd=project, text=True).strip()
        state["source_dirty"] = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=project, text=True).strip())
        state["codex_version"] = codex_version
        if not args.inspect:
            write_json(state_path, state)
        pending_summary = {"selected_result": "NOT ASSESSED", "selected": len(selected),
                           "authored_cases": len(cases), "full_port_acceptance": "NOT ASSESSED",
                           "note": "Current invocation has not completed its preflight and selected cases."}
        summary_path = output / ("inspection.json" if args.inspect else "summary.json")
        write_json(summary_path, pending_summary)
        client = Client(args.codex, project, output)
        try:
            client.request("initialize", {"clientInfo": {"name": "ccgs-native-acceptance", "version": "1"},
                                          "capabilities": {"experimentalApi": True}})
            client.notify("initialized")
            listing = client.request("hooks/list", {"cwds": [str(project)]})
            write_json(output / "hooks.json", listing)
            reasons = check_hooks(listing, project)
            if reasons:
                write_json(summary_path, {**pending_summary, "reasons": reasons})
                print(json.dumps({"status": "NOT ASSESSED", "reasons": reasons}, ensure_ascii=True))
                return 2
            if args.inspect:
                inspection = {"hooks": "trusted", "project": str(project),
                              "full_port_acceptance": "NOT ASSESSED"}
                write_json(summary_path, inspection)
                print(json.dumps(inspection, ensure_ascii=True))
                return 0
            for case in selected:
                old = state["cases"].get(case["id"], {})
                if args.resume and can_resume(old, fingerprint):
                    print(json.dumps({"id": case["id"], "status": "PASS", "reused": True}), flush=True)
                    continue
                result = run_case(client, project, output, case, args.timeout)
                result["source_fingerprint"] = fingerprint
                state["cases"][case["id"]] = result
                write_json(state_path, state)
                print(json.dumps({key: value for key, value in result.items()
                                  if key not in {"protected_hashes", "artifacts"}},
                                 ensure_ascii=True), flush=True)
                if result["status"] != "PASS":
                    break
            statuses = [state["cases"].get(c["id"], {}).get("status", "NOT ASSESSED") for c in selected]
            overall = "FAIL" if "FAIL" in statuses else "NOT ASSESSED" if "NOT ASSESSED" in statuses else "PASS"
            summary = {"selected_result": overall, "selected": len(selected),
                       "authored_cases": len(cases), "full_port_acceptance": "NOT ASSESSED",
                       "note": "Selected native cases do not establish full engine/team/workflow acceptance."}
            write_json(summary_path, summary)
            print(json.dumps(summary, ensure_ascii=True))
            return 0 if overall == "PASS" else 1 if overall == "FAIL" else 2
        except (Attention, queue.Empty) as exc:
            reason = str(exc) or "Native host response timed out."
            write_json(summary_path, {**pending_summary, "reason": reason})
            write_json(output / ("inspection-attention.json" if args.inspect else "attention.json"),
                       {"status": "NOT ASSESSED", "reason": reason})
            print(json.dumps({"status": "NOT ASSESSED", "reason": reason}, ensure_ascii=True))
            return 2
        finally:
            client.close()


if __name__ == "__main__":
    raise SystemExit(main())
