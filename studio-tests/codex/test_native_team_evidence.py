import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("native_team_evidence", ROOT / "studio-tests/native/team_evidence.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
verify_team_evidence = MODULE.verify_team_evidence


PARENT = "parent-1"


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


if __name__ == "__main__":
    unittest.main()
