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
