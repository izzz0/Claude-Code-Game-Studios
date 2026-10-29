import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / ".agents/studio/scripts/team-run.py"


class TeamRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ccgs team 测试 ")
        self.root = Path(self.tmp.name) / "project"
        self.root.mkdir(); (self.root / "project.yaml").write_text("schema_version: 1\n")

    def tearDown(self): self.tmp.cleanup()

    def invoke(self, *args):
        return subprocess.run([sys.executable, str(RUNNER), "--root", str(self.root), *map(str, args)],
                              text=True, capture_output=True)

    def test_init_assign_run_complete_and_resume_revalidates_artifacts(self):
        init = self.invoke("init", "--id", "run-1", "--team", "ccgs-team-combat", "--size", "small", "--host-limit", "1")
        self.assertEqual(init.returncode, 0, init.stderr)
        self.assertEqual(self.invoke("assign", "--id", "run-1", "--task", "design", "--role", "ccgs-qa-tester", "--files", "design/a.md").returncode, 0)
        self.assertEqual(self.invoke("event", "--id", "run-1", "--task", "design", "--status", "running", "--agent-id", "synthetic-agent-1").returncode, 0)
        artifact = self.root / "design/a.md"; artifact.parent.mkdir(); artifact.write_text("artifact", encoding="utf-8")
        completed = self.invoke("event", "--id", "run-1", "--task", "design", "--status", "completed", "--agent-id", "synthetic-agent-1", "--summary", "synthetic protocol fixture", "--artifact", "design/a.md")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        artifact.write_text("changed", encoding="utf-8")
        resume = json.loads(self.invoke("resume", "--id", "run-1").stdout)
        self.assertEqual(resume["revalidate"][0]["path"], "design/a.md")

    def test_dependencies_host_cap_ownership_and_missing_artifact_fail(self):
        self.assertEqual(self.invoke("init", "--id", "run-2", "--team", "team-combat", "--size", "studio", "--host-limit", "1").returncode, 0)
        self.assertEqual(self.invoke("assign", "--id", "run-2", "--task", "a", "--role", "ccgs-qa-tester", "--files", "src/a.gd").returncode, 0)
        self.assertEqual(self.invoke("assign", "--id", "run-2", "--task", "b", "--role", "ccgs-qa-tester", "--files", "src/b.gd").returncode, 0)
        self.assertEqual(self.invoke("event", "--id", "run-2", "--task", "a", "--status", "running", "--agent-id", "synthetic-a").returncode, 0)
        blocked = self.invoke("event", "--id", "run-2", "--task", "b", "--status", "running", "--agent-id", "synthetic-b")
        self.assertEqual(blocked.returncode, 3); self.assertIn("concurrency", blocked.stderr)
        conflict = self.invoke("assign", "--id", "run-2", "--task", "c", "--role", "ccgs-qa-tester", "--files", "src/a.gd")
        self.assertEqual(conflict.returncode, 0)
        missing = self.invoke("event", "--id", "run-2", "--task", "c", "--status", "completed", "--agent-id", "synthetic-a", "--summary", "missing artifact", "--artifact", "absent.txt")
        self.assertEqual(missing.returncode, 2)

        self.assertEqual(self.invoke("init", "--id", "run-overlap", "--team", "ccgs-team-combat", "--size", "small", "--host-limit", "2").returncode, 0)
        for task in ("left", "right"):
            self.assertEqual(self.invoke("assign", "--id", "run-overlap", "--task", task, "--role", "ccgs-qa-tester", "--files", "src/shared.gd").returncode, 0)
        self.assertEqual(self.invoke("event", "--id", "run-overlap", "--task", "left", "--status", "running", "--agent-id", "synthetic-left").returncode, 0)
        overlap = self.invoke("event", "--id", "run-overlap", "--task", "right", "--status", "running", "--agent-id", "synthetic-right")
        self.assertEqual(overlap.returncode, 3); self.assertIn("owns", overlap.stderr)

    def test_record_slug_is_separate_from_verbatim_native_agent_path(self):
        # Protocol fixture only: actual identity requires separate host receipts.
        invalid = self.invoke("init", "--id", "/root/designer", "--team", "team-combat", "--size", "small", "--host-limit", "1")
        self.assertNotEqual(invalid.returncode, 0)
        self.assertEqual(self.invoke("init", "--id", "chase-01", "--team", "team-combat", "--size", "small", "--host-limit", "1").returncode, 0)
        self.assertEqual(self.invoke("assign", "--id", "chase-01", "--task", "design", "--role", "ccgs-game-designer").returncode, 0)
        identity = "/root/synthetic_designer"
        running = self.invoke("event", "--id", "chase-01", "--task", "design", "--status", "running", "--agent-id", identity)
        self.assertEqual(running.returncode, 0, running.stderr)
        completed = self.invoke("event", "--id", "chase-01", "--task", "design", "--status", "completed", "--agent-id", identity,
                                "--summary", "Synthetic protocol return, no real child execution asserted")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertFalse(json.loads(completed.stdout)["execution_attested"])
        record = json.loads(self.invoke("show", "--id", "chase-01").stdout)
        self.assertEqual(record["id"], "chase-01")
        self.assertEqual(record["tasks"]["design"]["agent_id"], identity)

    def test_read_only_assign_requires_flag_and_duplicate_events_are_idempotent(self):
        self.assertEqual(self.invoke("init", "--id", "run-3", "--team", "ccgs-team-combat", "--size", "individual", "--host-limit", "2").returncode, 0)
        normal = self.invoke("assign", "--id", "run-3", "--task", "review", "--role", "ccgs-qa-tester", "--files", "docs/a.md", "--read-only")
        self.assertEqual(normal.returncode, 0)
        duplicate = self.invoke("assign", "--id", "run-3", "--task", "review", "--role", "ccgs-qa-tester", "--files", "docs/a.md", "--read-only")
        self.assertEqual(duplicate.returncode, 0); self.assertTrue(json.loads(duplicate.stdout)["unchanged"])
        record = json.loads(self.invoke("show", "--id", "run-3").stdout)
        self.assertTrue(record["tasks"]["review"]["read_only"])
        self.assertEqual(self.invoke("event", "--id", "run-3", "--task", "review", "--status", "running", "--agent-id", "synthetic-review").returncode, 0)
        self.assertEqual(self.invoke("assign", "--id", "run-3", "--task", "writer", "--role", "ccgs-qa-tester", "--files", "docs/a.md").returncode, 0)
        self.assertEqual(self.invoke("event", "--id", "run-3", "--task", "writer", "--status", "running", "--agent-id", "synthetic-writer").returncode, 0)
        done = self.invoke("event", "--id", "run-3", "--task", "review", "--status", "failed", "--agent-id", "synthetic-review", "--summary", "synthetic retry")
        self.assertEqual(done.returncode, 0)
        retry = self.invoke("event", "--id", "run-3", "--task", "review", "--status", "running", "--agent-id", "synthetic-review-2")
        self.assertEqual(retry.returncode, 0)
        interrupted = self.invoke("event", "--id", "run-3", "--task", "review", "--status", "interrupted", "--agent-id", "synthetic-review-2", "--summary", "synthetic interruption")
        self.assertEqual(interrupted.returncode, 0)
        resumed = self.invoke("event", "--id", "run-3", "--task", "review", "--status", "running", "--agent-id", "synthetic-review-2")
        self.assertEqual(resumed.returncode, 0)
        revision = json.loads(self.invoke("show", "--id", "run-3").stdout)["revision"]
        duplicate_event = self.invoke("event", "--id", "run-3", "--task", "review", "--status", "running", "--agent-id", "synthetic-review-2")
        self.assertEqual(duplicate_event.returncode, 0)
        self.assertEqual(json.loads(self.invoke("show", "--id", "run-3").stdout)["revision"], revision)
        self.assertEqual(self.invoke("event", "--id", "run-3", "--task", "review", "--status", "completed", "--agent-id", "wrong", "--summary", "wrong owner").returncode, 3)


if __name__ == "__main__": unittest.main()
