import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "studio-tests/native"))
SPEC = importlib.util.spec_from_file_location("native_team_evidence", ROOT / "studio-tests/native/team_evidence.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
verify_team_evidence = MODULE.verify_team_evidence


PARENT = "parent-1"
NATIVE_CHILD = "01a17d9e-a3b0-77c3-955a-35487d6efb92"
NATIVE_PATH = "/root/godot_adr_validation"


def _thread(thread_id="child-1", role="ccgs-qa-tester", parent=PARENT, text="Review result: PASS - completed evidence", cwd=None):
    return {
        "id": thread_id,
        "parentThreadId": parent,
        "agentRole": role,
        "cwd": cwd,
        "status": {"type": "idle"},
        "turns": [{"id": "turn-1", "status": "completed", "startedAt": 1, "completedAt": 2, "items": [
            {"type": "agentMessage", "phase": "final_answer", "text": text}
        ]}],
    }


def _item(tool, ids, status="completed", states=None, prompt=None):
    return {
        "type": "collabAgentToolCall", "tool": tool, "status": status,
        "receiverThreadIds": ids, "senderThreadId": PARENT,
        "agentsStates": states or {}, "prompt": prompt,
    }


def _manifest(root, agent_id="child-1", role="ccgs-qa-tester", status="completed", depends=None, summary="QA completed", artifact_path="evidence.txt"):
    artifact = root / "evidence.txt"
    artifact.write_text("retained evidence\n", encoding="utf-8")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    data = {"schema": 1, "tasks": {"qa": {
        "role": role, "files": [], "read_only": True,
        "depends_on": depends or [], "status": status, "agent_id": agent_id,
        "summary": summary, "artifacts": [{"path": artifact_path, "sha256": digest}],
    }}}
    target = root / "production" / "team-runs" / "run.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data), encoding="utf-8")


def _review_manifest(root, agent_id="child-1", read_only=True, role="ccgs-qa-tester", artifacts=True):
    coordination = root / ".scratch" / "team-observations"
    artifact = coordination / "review-evidence.txt"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text("Review result: PASS - completed evidence\n", encoding="utf-8")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    data = {"schema": 1, "tasks": {"review": {
        "role": role, "files": [], "read_only": read_only,
        "depends_on": [], "status": "completed", "agent_id": agent_id,
        "summary": "Independent review completed", "artifacts": ([
            {"path": "review-evidence.txt", "sha256": digest}
        ] if artifacts else []),
    }}}
    target = coordination / "production" / "team-runs" / "review.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data), encoding="utf-8")


def _multi_writer_manifest(root):
    target = root / "production" / "team-runs" / "run.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"schema": 1, "tasks": {
        "one": {"role": "ccgs-qa-tester", "files": ["src/shared.gd"], "read_only": False,
                "depends_on": [], "status": "completed", "agent_id": "child-1", "summary": "one done", "artifacts": []},
        "two": {"role": "ccgs-qa-tester", "files": ["src/shared.gd"], "read_only": False,
                "depends_on": [], "status": "completed", "agent_id": "child-2", "summary": "two done", "artifacts": []},
    }}), encoding="utf-8")


def _native_thread(root, child_id=NATIVE_CHILD, parent=PARENT, role="ccgs-qa-tester", path=NATIVE_PATH,
                   final=True, interrupted=False):
    thread = _thread(thread_id=child_id, role=role, parent=parent,
                     cwd=str(root / "project"), text="Review result: PASS - completed evidence")
    thread["source"] = {"subAgent": {"thread_spawn": {
        "parent_thread_id": parent, "agent_path": path, "agent_role": role,
    }}}
    thread["turns"] = []
    if interrupted:
        thread["turns"].append({"id": "turn-interrupted", "status": "interrupted",
                                "startedAt": 1, "completedAt": 2, "items": [], "itemsView": "full"})
    if final:
        thread["turns"].append({"id": "turn-completed", "status": "completed",
                                "startedAt": 3, "completedAt": 4, "items": [
                                    {"type": "agentMessage", "phase": "final_answer",
                                     "text": "Review result: PASS - completed evidence"}
                                ], "itemsView": "full"})
    return thread


def _activity(kind, child_id=NATIVE_CHILD, path=NATIVE_PATH, receipt_id=None):
    return {"type": "subAgentActivity", "kind": kind, "agentThreadId": child_id,
            "agentPath": path, "id": receipt_id or f"activity-{kind}"}


class NativeTeamEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        role_dir = self.root / ".codex" / "agents"
        role_dir.mkdir(parents=True)
        (role_dir / "ccgs-qa-tester.toml").write_text('name = "ccgs-qa-tester"\n', encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def valid_inputs(self):
        _manifest(self.root)
        items = [
            _item("spawnAgent", ["child-1"]),
            _item("interruptAgent", ["child-1"], states={"child-1": {"status": "interrupted"}}),
            _item("resumeAgent", ["child-1"]),
            _item("wait", ["child-1"], states={"child-1": {"status": "completed"}}),
        ]
        child = _thread(cwd=str(self.root))
        child["turns"] = [
            {"id": "turn-1", "status": "interrupted", "startedAt": 1, "completedAt": 2, "items": []},
            {"id": "turn-2", "status": "completed", "startedAt": 3, "completedAt": 4, "items": child["turns"][0]["items"]},
        ]
        items.insert(0, _item("wait", ["child-1"], states={"child-1": {"status": "running"}}))
        return items, {"child-1": child}

    def test_valid_chain_verifies_both_evidence_classes(self):
        items, children = self.valid_inputs()
        result = verify_team_evidence(self.root, items, children, PARENT)
        self.assertEqual(result["verified"], ["native_agents", "team_recovery"])
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["findings"], [])

    def test_absence_stays_missing_without_findings(self):
        result = verify_team_evidence(self.root, [], {}, PARENT)
        self.assertEqual(set(result["missing"]), {"native_agents", "team_recovery"})
        self.assertEqual(result["findings"], [])

    def test_missing_one_spawn_child_blocks_entire_spawn_set(self):
        _manifest(self.root)
        children = {"child-1": _thread(cwd=str(self.root))}
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["child-1", "child-2"])], children, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertIn("native_agents", result["missing"])

    def test_overlapping_completed_writers_are_a_confirmed_finding(self):
        _multi_writer_manifest(self.root)
        child1, child2 = _thread(thread_id="child-1", cwd=str(self.root)), _thread(thread_id="child-2", cwd=str(self.root))
        child1["turns"][0].update(startedAt=1, completedAt=5)
        child2["turns"][0].update(startedAt=4, completedAt=6)
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["child-1", "child-2"])],
                                      {"child-1": child1, "child-2": child2}, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertTrue(any("overlaps completed writer" in x for x in result["findings"]))

    def test_sequential_completed_writers_are_allowed(self):
        _multi_writer_manifest(self.root)
        child1, child2 = _thread(thread_id="child-1", cwd=str(self.root)), _thread(thread_id="child-2", cwd=str(self.root))
        child1["turns"][0].update(startedAt=1, completedAt=2)
        child2["turns"][0].update(startedAt=3, completedAt=4)
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["child-1", "child-2"])],
                                      {"child-1": child1, "child-2": child2}, PARENT)
        self.assertIn("native_agents", result["verified"])

    def test_followup_turns_do_not_hide_earlier_writer_overlap(self):
        _multi_writer_manifest(self.root)
        children = {name: _thread(thread_id=name, cwd=str(self.root)) for name in ("child-1", "child-2")}
        for name, first, last in (("child-1", (1, 5), (7, 8)), ("child-2", (4, 6), (9, 10))):
            child = children[name]
            child["turns"][0].update(startedAt=first[0], completedAt=first[1])
            child["turns"].append({**child["turns"][0], "id": "followup", "startedAt": last[0], "completedAt": last[1]})
        result = verify_team_evidence(self.root, [_item("spawnAgent", list(children))], children, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertTrue(any("overlaps completed writer" in x for x in result["findings"]))

    def test_missing_writer_turn_times_stays_na(self):
        _multi_writer_manifest(self.root)
        child1, child2 = _thread(thread_id="child-1", cwd=str(self.root)), _thread(thread_id="child-2", cwd=str(self.root))
        child1["turns"][0].update(startedAt=1, completedAt=2)
        child2["turns"][0].pop("startedAt")
        child2["turns"][0].pop("completedAt")
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["child-1", "child-2"])],
                                      {"child-1": child1, "child-2": child2}, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertFalse(any("overlaps completed writer" in x for x in result["findings"]))

    def test_fake_ids_and_wrong_parent_or_role_do_not_pass(self):
        _manifest(self.root, agent_id="fake")
        child = _thread(parent="other-parent", role="ccgs-not-a-role", cwd=str(self.root))
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["fake-id"])], {"fake-id": child}, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertTrue(any("wrong parent" in x or "unknown" in x or "ID does not match" in x for x in result["findings"]))

    def test_incomplete_child_does_not_pass(self):
        _manifest(self.root)
        child = _thread(cwd=str(self.root))
        child["turns"][0]["status"] = "inProgress"
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["child-1"])], {"child-1": child}, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertTrue(any("completed substantive" in x for x in result["findings"]))

    def test_stale_hash_and_unresolved_dependency_are_findings(self):
        _manifest(self.root, depends=["missing-task"])
        (self.root / "evidence.txt").write_text("changed\n", encoding="utf-8")
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["child-1"])], {"child-1": _thread(cwd=str(self.root))}, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertTrue(any("unresolved dependency" in x for x in result["findings"]))
        self.assertTrue(any("stale artifact hash" in x for x in result["findings"]))

    def test_recovery_wrong_id_does_not_pass(self):
        _manifest(self.root)
        items = [_item("spawnAgent", ["child-1"]),
                 _item("interruptAgent", ["child-1"], states={"child-1": {"status": "errored"}}),
                 _item("resumeAgent", ["other-child"])]
        result = verify_team_evidence(self.root, items, {"child-1": _thread(cwd=str(self.root))}, PARENT)
        self.assertNotIn("team_recovery", result["verified"])
        self.assertTrue(any("post-resume completed" in x for x in result["findings"]))

    def test_failure_only_manifest_cannot_attest_native_work(self):
        _manifest(self.root, agent_id="claimed", status="failed", summary="")
        result = verify_team_evidence(self.root, [], {}, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertTrue(any("is failed" in x for x in result["findings"]))

    def test_path_escape_and_profile_elsewhere_do_not_pass(self):
        _manifest(self.root, artifact_path="../outside.txt")
        child = _thread(cwd=str(self.root))
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["child-1"])], {"child-1": child}, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertTrue(any("stale artifact hash" in x for x in result["findings"]))

    def test_profile_only_elsewhere_does_not_pass(self):
        _manifest(self.root)
        child = _thread(cwd=str(self.root))
        (self.root / ".codex" / "agents" / "ccgs-qa-tester.toml").unlink()
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["child-1"])], {"child-1": child}, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertTrue(any("unknown or unconfigured" in x for x in result["findings"]))

    def test_duplicate_role_children_must_all_be_in_manifest(self):
        _manifest(self.root, agent_id="child-1")
        items = [_item("spawnAgent", ["child-1", "child-2"])]
        children = {"child-1": _thread(cwd=str(self.root)), "child-2": _thread(thread_id="child-2", cwd=str(self.root))}
        result = verify_team_evidence(self.root, items, children, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertTrue(any("crossmatches every completed child" in x for x in result["findings"]))

    def test_wrong_sender_is_not_native_evidence(self):
        _manifest(self.root)
        child = _thread(cwd=str(self.root))
        item = _item("spawnAgent", ["child-1"])
        item["senderThreadId"] = "other-parent"
        result = verify_team_evidence(self.root, [item], {"child-1": child}, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertTrue(any("wrong sender" in x for x in result["findings"]))

    def test_last_failed_turn_and_missing_post_resume_completion_do_not_pass(self):
        _manifest(self.root)
        child = _thread(cwd=str(self.root))
        child["turns"].append({"id": "turn-2", "status": "failed", "items": []})
        items = [_item("spawnAgent", ["child-1"]),
                 _item("interruptAgent", ["child-1"], states={"child-1": {"status": "interrupted"}}),
                 _item("resumeAgent", ["child-1"])]
        result = verify_team_evidence(self.root, items, {"child-1": child}, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertNotIn("team_recovery", result["verified"])

    def test_valid_readonly_independent_review_chain(self):
        _review_manifest(self.root)
        child = _thread(cwd=str(self.root))
        result = MODULE.verify_review_evidence(self.root, [_item("spawnAgent", ["child-1"])], {"child-1": child}, PARENT)
        self.assertEqual(result, {"verified": ["independent_review"], "missing": [], "findings": []})

    def test_unrelated_writer_child_does_not_invalidate_claimed_readonly_review(self):
        _review_manifest(self.root, agent_id="review-child")
        reviewer = _thread(thread_id="review-child", cwd=str(self.root))
        writer = _thread(thread_id="writer-child", cwd=str(self.root))
        writer["turns"][0]["items"].append({"type": "fileChange", "id": "write-1", "status": "completed"})
        result = MODULE.verify_review_evidence(
            self.root,
            [_item("spawnAgent", ["review-child", "writer-child"])],
            {"review-child": reviewer, "writer-child": writer},
            PARENT,
        )
        self.assertEqual(result, {"verified": ["independent_review"], "missing": [], "findings": []})

    def test_retained_review_is_one_complete_return_without_coordinator_additions(self):
        _review_manifest(self.root)
        child = _thread(cwd=str(self.root))
        items = [_item("spawnAgent", ["child-1"])]
        coordination = self.root / ".scratch/team-observations"
        artifact = coordination / "review-evidence.txt"
        manifest = coordination / "production/team-runs/review.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        original = artifact.read_text(encoding="utf-8")
        artifact.write_text("Coordinator says approved\n" + original, encoding="utf-8")
        data["tasks"]["review"]["artifacts"][0]["sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        manifest.write_text(json.dumps(data), encoding="utf-8")
        self.assertNotIn("independent_review", MODULE.verify_review_evidence(self.root, items, {"child-1": child}, PARENT)["verified"])
        artifact.write_text(original, encoding="utf-8")
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        (coordination / "duplicate.txt").write_text(original, encoding="utf-8")
        data["tasks"]["review"]["artifacts"] = [{"path": name, "sha256": digest} for name in ("review-evidence.txt", "duplicate.txt")]
        manifest.write_text(json.dumps(data), encoding="utf-8")
        self.assertNotIn("independent_review", MODULE.verify_review_evidence(self.root, items, {"child-1": child}, PARENT)["verified"])

    def test_review_input_hash_prompt_matching_verifies(self):
        _review_manifest(self.root)
        source = self.root / "design" / "brief.md"
        source.parent.mkdir(parents=True)
        source.write_text("brief\n", encoding="utf-8")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        content = source.read_bytes().decode("utf-8")
        child = _thread(cwd=str(self.root))
        bundle = json.dumps({"design/brief.md": {"sha256": digest, "content": content}}, ensure_ascii=False)
        item = _item("spawnAgent", ["child-1"], prompt=f"CCGS_REVIEW_INPUTS\n{bundle}\nCCGS_REVIEW_INPUTS_END")
        result = MODULE.verify_review_evidence(self.root, [item], {"child-1": child}, PARENT,
                                               {"design/brief.md": {"sha256": digest, "content": content}})
        self.assertEqual(result, {"verified": ["independent_review"], "missing": [], "findings": []})

    def test_review_missing_input_hash_prompt_stays_na_without_finding(self):
        _review_manifest(self.root)
        child = _thread(cwd=str(self.root))
        result = MODULE.verify_review_evidence(self.root, [_item("spawnAgent", ["child-1"], prompt="Review the brief")],
                                               {"child-1": child}, PARENT,
                                               {"design/brief.md": {"sha256": "a" * 64, "content": "brief\n"}})
        self.assertEqual(result["verified"], [])
        self.assertEqual(result["missing"], ["independent_review"])
        self.assertEqual(result["findings"], [])

    def test_legacy_review_must_bind_new_deliverable_and_reject_post_review_change(self):
        from run_acceptance import final_review_inputs, tree_hashes
        _review_manifest(self.root)
        source = self.root / "brief.md"
        source.write_text("approved scope", encoding="utf-8")
        before = tree_hashes(self.root)
        initial = {"brief.md": {"sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "content": "approved scope"}}
        output = self.root / "draft.md"
        output.write_text("actual new deliverable", encoding="utf-8")
        case = {"expected": {"files": [{"path": "draft.md", "changed": True}]}}
        expected, missing = final_review_inputs(case, self.root, before, initial)
        self.assertEqual(missing, [])
        child = _thread(cwd=str(self.root))
        def check(bundle, current):
            item = _item("spawnAgent", ["child-1"], prompt="CCGS_REVIEW_INPUTS\n" + json.dumps(bundle) + "\nCCGS_REVIEW_INPUTS_END")
            return MODULE.verify_review_evidence(self.root, [item], {"child-1": child}, PARENT, current)
        self.assertEqual(check(initial, expected)["verified"], [])
        self.assertEqual(check(expected, expected)["verified"], ["independent_review"])
        output.write_text("changed after review", encoding="utf-8")
        current, missing = final_review_inputs(case, self.root, before, initial)
        self.assertEqual(missing, [])
        self.assertEqual(check(expected, current)["verified"], [])

    def test_modern_reviewer_must_read_both_fixture_and_final_output(self):
        from run_acceptance import final_review_inputs, tree_hashes
        _review_manifest(self.root, agent_id=NATIVE_PATH)
        (self.root / "brief.md").write_text("approved scope", encoding="utf-8")
        before = tree_hashes(self.root)
        initial = {"brief.md": {"sha256": hashlib.sha256(b"approved scope").hexdigest(), "content": "approved scope"}}
        (self.root / "draft.md").write_text("new deliverable", encoding="utf-8")
        case = {"expected": {"files": [{"path": "draft.md", "changed": True}]}}
        expected, missing = final_review_inputs(case, self.root, before, initial)
        self.assertEqual(missing, [])
        child = _native_thread(self.root)
        child["cwd"] = str(self.root)
        def add_read(name):
            script = "Microsoft.PowerShell.Management\\Get-Content -LiteralPath '" + name + "' -Raw -Encoding utf8"
            child["turns"][-1]["items"].insert(0, {
                "type": "commandExecution", "command": '\"C:\\runtime\\pwsh.exe\" -Command ' + "'" + script.replace("'", "''") + "'",
                "commandActions": [{"type": "unknown", "command": script}],
                "status": "completed", "exitCode": 0, "aggregatedOutput": expected[name]["content"],
            })
        add_read("brief.md")
        items = [_activity("started")]
        self.assertEqual(MODULE.verify_review_evidence(self.root, items, {NATIVE_CHILD: child}, PARENT, expected)["verified"], [])
        add_read("draft.md")
        self.assertEqual(MODULE.verify_review_evidence(self.root, items, {NATIVE_CHILD: child}, PARENT, expected)["verified"], ["independent_review"])
        (self.root / "draft.md").write_text("changed after read", encoding="utf-8")
        current, _ = final_review_inputs(case, self.root, before, initial)
        self.assertEqual(MODULE.verify_review_evidence(self.root, items, {NATIVE_CHILD: child}, PARENT, current)["verified"], [])

    def test_review_changed_input_hash_stays_na_without_finding(self):
        _review_manifest(self.root)
        source = self.root / "design" / "brief.md"
        source.parent.mkdir(parents=True)
        source.write_text("brief\n", encoding="utf-8")
        old_digest = "0" * 64
        current_digest = hashlib.sha256(source.read_bytes()).hexdigest()
        content = source.read_bytes().decode("utf-8")
        child = _thread(cwd=str(self.root))
        bundle = json.dumps({"design/brief.md": {"sha256": old_digest, "content": content}}, ensure_ascii=False)
        item = _item("spawnAgent", ["child-1"], prompt=f"CCGS_REVIEW_INPUTS\n{bundle}\nCCGS_REVIEW_INPUTS_END")
        result = MODULE.verify_review_evidence(self.root, [item], {"child-1": child}, PARENT,
                                               {"design/brief.md": {"sha256": current_digest, "content": content}})
        self.assertEqual(result["verified"], [])
        self.assertEqual(result["missing"], ["independent_review"])
        self.assertEqual(result["findings"], [])

    def test_review_write_manifest_does_not_pass(self):
        _review_manifest(self.root, read_only=False)
        child = _thread(cwd=str(self.root))
        result = MODULE.verify_review_evidence(self.root, [_item("spawnAgent", ["child-1"])], {"child-1": child}, PARENT)
        self.assertEqual(result["verified"], [])
        self.assertIn("independent_review", result["missing"])
        self.assertTrue(any("not completed read-only" in x for x in result["findings"]))

    def test_review_child_file_change_does_not_pass(self):
        _review_manifest(self.root)
        child = _thread(cwd=str(self.root))
        child["turns"][0]["items"].append({"type": "fileChange", "id": "change-1", "status": "completed", "changes": []})
        result = MODULE.verify_review_evidence(self.root, [_item("spawnAgent", ["child-1"])], {"child-1": child}, PARENT)
        self.assertEqual(result["verified"], [])
        self.assertTrue(any("fileChange" in x for x in result["findings"]))

    def test_review_task_role_must_match_child_role_and_artifact_is_required(self):
        _review_manifest(self.root, role="ccgs-other-role", artifacts=False)
        child = _thread(cwd=str(self.root))
        result = MODULE.verify_review_evidence(self.root, [_item("spawnAgent", ["child-1"])], {"child-1": child}, PARENT)
        self.assertEqual(result["verified"], [])
        self.assertIn("independent_review", result["missing"])
        self.assertTrue(any("role does not match" in x for x in result["findings"]))

    def test_review_unknown_command_stays_missing(self):
        _review_manifest(self.root)
        child = _thread(cwd=str(self.root))
        child["turns"][0]["items"].insert(0, {"type": "commandExecution", "command": "python inspect.py", "status": "completed"})
        result = MODULE.verify_review_evidence(self.root, [_item("spawnAgent", ["child-1"])], {"child-1": child}, PARENT)
        self.assertEqual(result["verified"], [])
        self.assertIn("independent_review", result["missing"])

    def test_review_evidence_absence_stays_na(self):
        result = MODULE.verify_review_evidence(self.root, [], {}, PARENT)
        self.assertEqual(result, {"verified": [], "missing": ["independent_review"], "findings": []})

    def test_modern_activity_and_unambiguous_agent_path_crossmatch_manifest(self):
        _manifest(self.root, agent_id=NATIVE_PATH)
        child = _native_thread(self.root)
        result = verify_team_evidence(self.root, [_activity("started")], {NATIVE_CHILD: child}, PARENT)
        self.assertIn("native_agents", result["verified"])

    def test_mixed_legacy_and_modern_receipts_require_union_of_all_children(self):
        _manifest(self.root, agent_id="child-1")
        legacy = _thread(cwd=str(self.root))
        missing_modern = _native_thread(self.root, child_id="modern-child")
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["child-1"]),
                                                  _activity("started", "modern-child")],
                                      {"child-1": legacy}, PARENT)
        self.assertNotIn("native_agents", result["verified"])

    def test_mixed_same_uuid_legacy_receipt_does_not_require_optional_modern_metadata(self):
        _manifest(self.root, agent_id="child-1")
        legacy = _thread(cwd=str(self.root))
        legacy["source"] = {"subAgent": {"thread_spawn": {
            "parent_thread_id": PARENT, "agent_role": "ccgs-qa-tester",
        }}}
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["child-1"]),
                                                  _activity("started", "child-1")],
                                      {"child-1": legacy}, PARENT)
        self.assertIn("native_agents", result["verified"])

    def test_mixed_same_uuid_rejects_contradictory_modern_metadata(self):
        _manifest(self.root, agent_id="child-1")
        legacy = _thread(cwd=str(self.root))
        legacy["source"] = {"subAgent": {"thread_spawn": {
            "parent_thread_id": PARENT, "agent_path": "/root/wrong", "agent_role": "ccgs-qa-tester",
        }}}
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["child-1"]),
                                                  _activity("started", "child-1")],
                                      {"child-1": legacy}, PARENT)
        self.assertNotIn("native_agents", result["verified"])

    def test_mixed_review_rejects_contradictory_provided_modern_metadata(self):
        _review_manifest(self.root, agent_id=NATIVE_CHILD)
        child = _native_thread(self.root)
        child["source"]["subAgent"]["thread_spawn"]["agent_role"] = "ccgs-wrong"
        items = [_item("spawnAgent", [NATIVE_CHILD]), _activity("started")]
        result = MODULE.verify_review_evidence(self.root, items, {NATIVE_CHILD: child}, PARENT)
        self.assertNotIn("independent_review", result["verified"])

    def test_modern_activity_rejects_wrong_parent_cwd_and_role(self):
        _manifest(self.root, agent_id=NATIVE_PATH)
        for child in (
            _native_thread(self.root, parent="other-parent"),
            _native_thread(self.root, role="ccgs-unconfigured"),
            _native_thread(self.root, path=NATIVE_PATH, final=True),
        ):
            if child["parentThreadId"] == PARENT and child["agentRole"] == "ccgs-qa-tester":
                child["cwd"] = str(self.root.parent)
            result = verify_team_evidence(self.root, [_activity("started")], {NATIVE_CHILD: child}, PARENT)
            self.assertNotIn("native_agents", result["verified"])

    def test_modern_activity_only_or_model_claimed_uuid_does_not_prove_completion(self):
        _manifest(self.root, agent_id=NATIVE_PATH)
        child = _native_thread(self.root, final=False)
        result = verify_team_evidence(self.root, [_activity("started"), {"type": "agentMessage", "text": NATIVE_CHILD}],
                                      {NATIVE_CHILD: child}, PARENT)
        self.assertNotIn("native_agents", result["verified"])

    def test_ambiguous_agent_path_alias_cannot_crossmatch_manifest(self):
        second = "01a17d9e-a3b0-77c3-955a-35487d6efb93"
        _manifest(self.root, agent_id=NATIVE_PATH)
        children = {NATIVE_CHILD: _native_thread(self.root), second: _native_thread(self.root, child_id=second)}
        items = [_activity("started", NATIVE_CHILD), _activity("started", second)]
        result = verify_team_evidence(self.root, items, children, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertTrue(any("ambiguous" in finding for finding in result["findings"]))

    def test_readonly_team_task_rejects_file_changes_and_unproven_commands(self):
        _manifest(self.root)
        child = _thread(cwd=str(self.root))
        child["turns"][0]["items"].append({"type": "fileChange", "id": "write"})
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["child-1"])], {"child-1": child}, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertTrue(any("read-only team task" in finding and "fileChange" in finding for finding in result["findings"]))

        child = _thread(cwd=str(self.root))
        child["turns"][0]["items"].append({
            "type": "commandExecution", "command": "pwsh -Command Get-Content secret.txt",
            "commandActions": [{"type": "unknown", "command": "Get-Content secret.txt"}],
        })
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["child-1"])], {"child-1": child}, PARENT)
        self.assertNotIn("native_agents", result["verified"])
        self.assertNotIn("unproven command", " ".join(result["findings"]))
        self.assertEqual(result["findings"], [])

    def test_authoring_team_task_may_have_write_receipts(self):
        _manifest(self.root)
        manifest = self.root / "production" / "team-runs" / "run.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["tasks"]["qa"]["read_only"] = False
        manifest.write_text(json.dumps(data), encoding="utf-8")
        child = _thread(cwd=str(self.root))
        child["turns"][0]["items"].append({"type": "fileChange", "id": "write"})
        child["turns"][0]["items"].append({"type": "commandExecution", "command": "write command"})
        result = verify_team_evidence(self.root, [_item("spawnAgent", ["child-1"])], {"child-1": child}, PARENT)
        self.assertIn("native_agents", result["verified"])

    def test_modern_recovery_requires_started_interrupted_interacted_and_bound_completion(self):
        _manifest(self.root, agent_id=NATIVE_PATH)
        child = _native_thread(self.root, interrupted=True)
        items = [_activity("started"), _activity("interrupted"), _activity("interacted"),
                 _activity("completed", receipt_id="subagent-completed-turn-completed")]
        result = verify_team_evidence(self.root, items, {NATIVE_CHILD: child}, PARENT)
        self.assertIn("team_recovery", result["verified"])

    def test_modern_recovery_rejects_wrong_order_missing_interruption_and_replayed_completion(self):
        _manifest(self.root, agent_id=NATIVE_PATH)
        child = _native_thread(self.root, interrupted=True)
        good_completion = _activity("completed", receipt_id="subagent-completed-turn-completed")
        bad_chains = (
            [_activity("started"), _activity("interacted"), _activity("interrupted"), good_completion],
            [_activity("started"), _activity("interacted"), good_completion],
            [_activity("started"), _activity("interrupted"), _activity("interacted"),
             _activity("completed", receipt_id="subagent-completed-old-turn")],
            [_activity("started"), _activity("interrupted", child_id="other-child"),
             _activity("interacted"), good_completion],
        )
        for items in bad_chains:
            result = verify_team_evidence(self.root, items, {NATIVE_CHILD: child}, PARENT)
            self.assertNotIn("team_recovery", result["verified"])

    def test_modern_recovery_requires_recovering_child_cwd_and_matching_manifest_task(self):
        _manifest(self.root, agent_id="child-1")
        child = _native_thread(self.root, interrupted=True)
        child["cwd"] = str(self.root.parent)
        unrelated = _thread(cwd=str(self.root))
        items = [_activity("started"), _activity("interrupted"), _activity("interacted"),
                 _activity("completed", receipt_id="subagent-completed-turn-completed")]
        result = verify_team_evidence(self.root, items, {NATIVE_CHILD: child, "child-1": unrelated}, PARENT)
        self.assertNotIn("team_recovery", result["verified"])

        child = _native_thread(self.root, interrupted=True)
        result = verify_team_evidence(self.root, items, {NATIVE_CHILD: child, "child-1": unrelated}, PARENT)
        self.assertNotIn("team_recovery", result["verified"])

    def test_recovery_fallback_crossmatches_unambiguous_manifest_alias(self):
        _manifest(self.root, agent_id=NATIVE_PATH)
        child = _native_thread(self.root, interrupted=True)
        items = [
            _activity("started"),
            _item("wait", [NATIVE_CHILD], states={NATIVE_CHILD: {"status": "running"}}),
            _item("interruptAgent", [NATIVE_CHILD], states={NATIVE_CHILD: {"status": "interrupted"}}),
            _item("resumeAgent", [NATIVE_CHILD]),
            _item("wait", [NATIVE_CHILD], states={NATIVE_CHILD: {"status": "completed"}}),
        ]
        result = verify_team_evidence(self.root, items, {NATIVE_CHILD: child}, PARENT)
        self.assertIn("team_recovery", result["verified"])

    def test_recovery_fallback_rejects_alias_for_unrelated_child(self):
        other_child = "01a17d9e-a3b0-77c3-955a-35487d6efb93"
        other_path = "/root/unrelated_agent"
        _manifest(self.root, agent_id=other_path)
        child = _native_thread(self.root, interrupted=True)
        unrelated = _native_thread(self.root, child_id=other_child, path=other_path)
        items = [
            _activity("started"),
            _activity("started", child_id=other_child, path=other_path),
            _item("wait", [NATIVE_CHILD], states={NATIVE_CHILD: {"status": "running"}}),
            _item("interruptAgent", [NATIVE_CHILD], states={NATIVE_CHILD: {"status": "interrupted"}}),
            _item("resumeAgent", [NATIVE_CHILD]),
            _item("wait", [NATIVE_CHILD], states={NATIVE_CHILD: {"status": "completed"}}),
        ]
        result = verify_team_evidence(self.root, items, {NATIVE_CHILD: child, other_child: unrelated}, PARENT)
        self.assertNotIn("team_recovery", result["verified"])

    def test_modern_recovery_rejects_invalid_interruption_timing(self):
        _manifest(self.root, agent_id=NATIVE_PATH)
        child = _native_thread(self.root, interrupted=True)
        child["turns"][0]["startedAt"] = 999
        items = [_activity("started"), _activity("interrupted"), _activity("interacted"),
                 _activity("completed", receipt_id="subagent-completed-turn-completed")]
        result = verify_team_evidence(self.root, items, {NATIVE_CHILD: child}, PARENT)
        self.assertNotIn("team_recovery", result["verified"])

    def test_readonly_evidence_requires_full_turn_history(self):
        _manifest(self.root, agent_id=NATIVE_PATH)
        items = [_activity("started")]
        _review_manifest(self.root, agent_id=NATIVE_PATH)
        for view in ("notLoaded", "summary"):
            child = _native_thread(self.root)
            child["turns"].insert(0, {"id": "hidden", "status": "completed", "itemsView": view, "items": []})
            result = verify_team_evidence(self.root, items, {NATIVE_CHILD: child}, PARENT)
            self.assertNotIn("native_agents", result["verified"])
            result = MODULE.verify_review_evidence(self.root, items, {NATIVE_CHILD: child}, PARENT)
            self.assertNotIn("independent_review", result["verified"])

    def test_modern_review_requires_and_verifies_canonical_source_reads(self):
        _review_manifest(self.root, agent_id=NATIVE_PATH)
        source = self.root / "design" / "brief.md"
        source.parent.mkdir(parents=True)
        content = "review input\n"
        source.write_bytes(content.encode("utf-8"))
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        expected = {"design/brief.md": {"sha256": digest, "content": content}}
        script = "Microsoft.PowerShell.Management\\Get-Content -LiteralPath 'design/brief.md' -Raw -Encoding utf8"
        command = '"C:\\runtime\\pwsh.exe" -Command ' + "'" + script.replace("'", "''") + "'"
        child = _native_thread(self.root)
        child["turns"][-1]["items"].insert(0, {
            "type": "commandExecution", "command": command,
            "commandActions": [{"type": "unknown", "command": script}],
            "status": "completed", "exitCode": 0, "aggregatedOutput": content,
        })
        items = [_activity("started")]
        result = MODULE.verify_review_evidence(self.root, items, {NATIVE_CHILD: child}, PARENT, expected)
        self.assertEqual(result["verified"], ["independent_review"])

    def test_modern_review_without_bound_reads_stays_na_and_write_receipts_fail(self):
        _review_manifest(self.root, agent_id=NATIVE_PATH)
        source = self.root / "design" / "brief.md"
        source.parent.mkdir(parents=True)
        content = "review input\n"
        source.write_bytes(content.encode("utf-8"))
        expected = {"design/brief.md": {"sha256": hashlib.sha256(content.encode()).hexdigest(), "content": content}}
        child = _native_thread(self.root)
        result = MODULE.verify_review_evidence(self.root, [_activity("started")], {NATIVE_CHILD: child}, PARENT, expected)
        self.assertEqual(result["verified"], [])
        self.assertEqual(result["missing"], ["independent_review"])
        child["turns"][-1]["items"].append({"type": "fileChange", "id": "write"})
        result = MODULE.verify_review_evidence(self.root, [_activity("started")], {NATIVE_CHILD: child}, PARENT, expected)
        self.assertNotIn("independent_review", result["verified"])
        self.assertTrue(any("fileChange" in finding for finding in result["findings"]))


if __name__ == "__main__":
    unittest.main()
