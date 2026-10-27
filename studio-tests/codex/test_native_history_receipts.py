"""Protocol regressions for retained and paginated native receipts; no model runs."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("native_history_receipts", ROOT / "studio-tests/native/run_acceptance.py")
driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(driver)


class NativeHistoryReceiptTests(unittest.TestCase):
    def test_child_ids_use_authoritative_host_items_only(self):
        items = [
            {"type": "collabAgentToolCall", "receiverThreadIds": ["legacy", "shared"]},
            {"type": "subAgentActivity", "kind": "started", "agentThreadId": "activity"},
            {"type": "subAgentActivity", "kind": "interrupted", "agentThreadId": "shared"},
            {"type": "agentMessage", "text": "agentThreadId: forged"},
            {"type": "subAgentActivity", "agentPath": "fake-child", "kind": "started"},
            {"type": "subAgentActivity", "agentThreadId": None},
            {"type": "subAgentActivity", "agentThreadId": " "},
            {"type": "collabAgentToolCall", "receiverThreadIds": "not-a-list"},
        ]
        self.assertEqual(driver.collect_child_thread_ids(items), ["activity", "legacy", "shared"])

    def test_child_history_hydrates_all_pages_including_omitted_writes(self):
        class Client:
            def request(self, method, params):
                if method == "thread/read":
                    return {"thread": {"id": "child", "historyMode": "paginated"}}
                if method == "thread/turns/list":
                    return {"data": [{"id": "turn", "itemsView": "summary", "items": []}], "nextCursor": None}
                item = {"type": "fileChange", "id": "write"} if params["cursor"] else {
                    "type": "agentMessage", "text": "reviewed"}
                return {"data": [{"turnId": "turn", "item": item}],
                        "nextCursor": None if params["cursor"] else "second"}
        thread, pages = driver.read_child_history(Client(), "child")
        self.assertEqual(thread["turns"][0]["itemsView"], "full")
        self.assertEqual(thread["turns"][0]["items"][-1]["type"], "fileChange")
        self.assertEqual(len(pages), 3)

    def test_repeating_history_cursor_and_wrong_turn_cannot_be_verified(self):
        class Client:
            def request(self, method, params):
                if method == "thread/read":
                    return {"thread": {"turns": [{"id": "turn", "itemsView": "notLoaded"}]}}
                return {"data": [], "nextCursor": "same"}
        with self.assertRaises(driver.Attention):
            driver.read_child_history(Client(), "child")
        class WrongTurn(Client):
            def request(self, method, params):
                if method == "thread/read":
                    return super().request(method, params)
                return {"data": [{"turnId": "other", "item": {}}], "nextCursor": None}
        with self.assertRaises(driver.Attention):
            driver.read_child_history(WrongTurn(), "child")

    def test_timeout_retains_attempt_and_interrupts_without_starting_another_case(self):
        class Client:
            def __init__(self):
                self.events, self.requests = [], []
            def request(self, method, params):
                self.requests.append(method)
                if method == "thread/start":
                    self.ephemeral = params["ephemeral"]
                    return {"thread": {"id": "timed-child"}, "model": "synthetic"}
                if method == "turn/start":
                    return {"turn": {"id": "turn-1"}}
                if method == "turn/interrupt":
                    raise driver.Attention("synthetic interruption RPC unavailable")
                return {}
        case = json.loads((ROOT / "studio-tests/native/cases.json").read_text(encoding="utf-8"))["cases"][0]
        with tempfile.TemporaryDirectory() as temp:
            client = Client()
            result = driver.run_case(client, ROOT, Path(temp), case, 0)
            self.assertEqual(result["status"], "NOT ASSESSED")
            self.assertEqual(result["transport_status"], "timeout")
            self.assertEqual(client.requests.count("turn/start"), 1)
            self.assertFalse(client.ephemeral, "Native child forks require a retained parent rollout")
            self.assertIn("turn/interrupt", client.requests)
            self.assertTrue(any("interruption was not confirmed" in x for x in result["missing"]))
            attempt = Path(result["attempt"])
            for name in ("before.json", "events.json", "result.json", "response.txt", "child-threads.json"):
                self.assertTrue((attempt / name).is_file(), name)

    def test_human_interaction_retains_case_receipts_without_approving(self):
        class Client:
            def __init__(self):
                self.events, self.requests = [], []
            def request(self, method, params):
                self.requests.append(method)
                return {"thread": {"id": "approval-case"}} if method == "thread/start" else {}
            def receive(self, timeout):
                raise driver.Attention("Human interaction required: item/fileChange/requestApproval")
        case = json.loads((ROOT / "studio-tests/native/cases.json").read_text(encoding="utf-8"))["cases"][0]
        with tempfile.TemporaryDirectory() as temp:
            client = Client()
            result = driver.run_case(client, ROOT, Path(temp), case, 10)
            self.assertEqual(result["status"], "NOT ASSESSED")
            self.assertIn("requestApproval", result["native_error"]["message"])
            self.assertEqual(client.requests, ["thread/start", "turn/start"])
            self.assertTrue((Path(result["attempt"]) / "result.json").is_file())

    def test_interrupted_parent_hydrates_activity_child_history_without_resuming(self):
        class Client:
            def __init__(self):
                self.events, self.requests = [], []
            def request(self, method, params):
                self.requests.append((method, params))
                if method == "thread/start":
                    return {"thread": {"id": "parent", "model": "fixture"}}
                if method == "turn/start":
                    return {"turn": {"id": "turn-1"}}
                if method == "thread/read":
                    self.read_child = params["threadId"]
                    return {"thread": {"id": "activity-child", "status": "interrupted", "turns": []}}
                raise AssertionError("Unexpected RPC: " + method)
            def receive(self, timeout):
                self.events.append({
                    "method": "item/completed",
                    "params": {"threadId": "parent", "item": {
                        "type": "subAgentActivity", "kind": "interrupted",
                        "agentThreadId": "activity-child", "agentPath": "ccgs-godot-gdscript-specialist",
                    }},
                })
                raise driver.Attention("Human interaction required: item/fileChange/requestApproval")

        case = json.loads((ROOT / "studio-tests/native/cases.json").read_text(encoding="utf-8"))["cases"][0]
        with tempfile.TemporaryDirectory() as temp:
            client = Client()
            result = driver.run_case(client, ROOT, Path(temp), case, 10)
            self.assertEqual(result["status"], "NOT ASSESSED")
            self.assertEqual(result["native_agent_ids"], ["activity-child"])
            self.assertEqual(client.read_child, "activity-child")
            self.assertEqual([method for method, _ in client.requests],
                             ["thread/start", "turn/start", "thread/read"])
            child_receipt = json.loads((Path(result["attempt"]) / "child-threads.json").read_text(encoding="utf-8"))
            self.assertEqual(child_receipt["threads"]["activity-child"]["status"], "interrupted")
            self.assertEqual(client.requests[-1][0], "thread/read")

            review = driver.verify_review_evidence(
                Path(result["sandbox"]),
                [{"type": "subAgentActivity", "kind": "interrupted", "agentThreadId": "activity-child"}],
                child_receipt["threads"], "parent",
            )
            self.assertEqual(review["verified"], [])
            self.assertIn("independent_review", review["missing"])
