"""Focused semantic contracts for the migrated Codex skills.

These tests exercise relationships between instructions and the installed
routes/configuration; they deliberately avoid asserting a copied sentence.
"""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".agents" / "skills"


class SkillContractTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_non_team_routes_resolve_to_installed_skills(self):
        """A migrated route must point at a real skill, not a legacy path."""
        for path in SKILLS.glob("ccgs-*/**/*.md"):
            if path.parts[-2].startswith("ccgs-team-"):
                continue
            text = path.read_text(encoding="utf-8")
            for route in set(re.findall(r"\$(ccgs-[a-z0-9-]+)", text)):
                self.assertTrue((SKILLS / route).is_dir(), f"{path}: missing route {route}")

    def test_all_non_team_skill_metadata_is_exactly_name_and_description(self):
        """Parse every first-party skill header, including skills with no focused test."""
        paths = sorted(p for p in SKILLS.glob("ccgs-*/SKILL.md")
                       if not p.parent.name.startswith("ccgs-team-"))
        self.assertEqual(len(paths), 65)
        for path in paths:
            text = path.read_text(encoding="utf-8-sig")
            self.assertTrue(text.startswith("---\n"), path)
            match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
            self.assertIsNotNone(match, path)
            fields = {}
            for line in match.group(1).splitlines():
                self.assertRegex(line, r"^(name|description):\s+", path)
                key, value = line.split(":", 1)
                self.assertNotIn(key, fields, path)
                fields[key] = value.strip()
            self.assertEqual(set(fields), {"name", "description"}, path)
            self.assertEqual(fields["name"], path.parent.name, path)
            description = fields["description"]
            self.assertGreater(len(description), 2, path)
            if description[0] in "\"'":
                self.assertEqual(description[-1], description[0], path)
            else:
                # Plain scalars are valid only when they contain no mapping
                # delimiter or comment marker that would change YAML meaning.
                self.assertNotIn(": ", description, path)
                self.assertNotIn(" #", description, path)

    def test_start_keeps_workflow_axes_and_minimal_path_independent(self):
        text = self.read(".agents/skills/ccgs-start/SKILL.md")
        self.assertIn("standard and full follow their configured artifact paths", text)
        self.assertNotIn("unsupported tier", text.lower())
        self.assertIn("independent of the phase ladder", text)

    def test_minimal_non_gate_is_explicitly_not_applicable(self):
        text = self.read(".agents/skills/ccgs-gate-check/references/gate-technical-setup.md")
        self.assertRegex(text, r"NOT APPLICABLE.*no design gate at minimal")
        self.assertNotRegex(text, r"minimal.{0,120}auto-PASS")
        self.assertIn("no stage write", text)

    def test_smoke_failure_and_missing_runner_have_distinct_outcomes(self):
        smoke = self.read(".agents/skills/ccgs-smoke-check/SKILL.md")
        detect = self.read(".agents/skills/ccgs-smoke-check/references/1-detect-setup.md")
        gate = self.read(".agents/skills/ccgs-smoke-check/references/6-write-gate.md")
        self.assertIn("suite is configured and runs, `FAIL` remains `FAIL`", smoke)
        self.assertIn("genuinely unconfigured", detect)
        self.assertIn("A configured suite that runs and fails remains `FAIL`", gate)
        self.assertNotIn("hand-off is not blocked", gate)

    def test_review_is_read_only_and_does_not_mutate_qa_or_story_state(self):
        text = self.read(".agents/skills/ccgs-code-review/SKILL.md")
        detail = self.read(".agents/skills/ccgs-code-review/references/full-workflow.md")
        self.assertIn("Make no file writes", text)
        self.assertIn("do not write QA reports", detail)
        self.assertIn("story status/content", detail)

    def test_skill_test_uses_codex_role_inventory(self):
        text = self.read(".agents/skills/ccgs-skill-test/references/source-contract.md")
        self.assertIn(".codex/agents/ccgs-*.toml", text)
        self.assertNotIn(".agents/studio/agents/", text)

    def test_all_owned_resources_are_free_of_host_specific_active_calls(self):
        """Scan every owned resource, not just the seven focused contracts."""
        markers = (
            r"\bsubagent_type\s*:", r"\bTask(?:Create|Get|List|Update)\b",
            r"\bAskUserQuestion\b", r"\bCLAUDE_(?:PROJECT|SKILL)_DIR\b",
            r"(?m)^\s*(?:model|allowed-tools):",
            r"\b(?:opus|sonnet|haiku)-tier\b", r"\b(?:opus|sonnet|haiku)\b",
            r"\bvia\s+`?Agent`?\b", r"\b(?:new|a)\s+`Agent`\s+call\b",
            r"n`native", r"Normal in-scope edits are authorized; ask only for consequential product decisions\.",
        )
        compiled = [re.compile(pattern, re.I) for pattern in markers]
        owned = [p for d in SKILLS.iterdir() if d.is_dir() and not d.name.startswith("ccgs-team-")
                 for p in d.rglob("*") if p.is_file() and p.suffix in {".md", ".sh"}]
        for path in owned:
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern in compiled:
                self.assertIsNone(pattern.search(text), f"{path}: active host marker {pattern.pattern}")

        # Negative fixtures prove the scan is behavioral rather than a list of
        # expected files or a search for only the currently failing examples.
        fixtures = {
            "role": "route subagent_type: ccgs-qa-tester",
            "tasks": "TaskCreate a QA task",
            "question": "AskUserQuestion before writing",
            "env": "${CLAUDE_SKILL_DIR}/hooks",
            "model": "model: opus",
            "agent": "spawn via Agent",
            "broken_native": "2. n`native delegation fixes errors",
            "lost_step": "Normal in-scope edits are authorized; ask only for consequential product decisions.",
        }
        for label, fixture in fixtures.items():
            self.assertTrue(any(pattern.search(fixture) for pattern in compiled), label)

    def test_story_generation_contract_is_idempotent(self):
        text = self.read(".agents/skills/ccgs-create-stories/CONTRACT.md")
        self.assertIn("idempotent", text.lower())
        self.assertIn("never duplicates", text.lower())

    def test_help_uses_stage_key_and_treats_presence_as_nonproof(self):
        text = self.read(".agents/skills/ccgs-help/SKILL.md")
        self.assertIn("resolve_config --keys rigor,automation,workflow,project.stage", text)
        self.assertIn("evidence/marker", text)
        self.assertNotIn("permission grant", text.lower())
        self.assertNotIn("\\note=", text)

    def test_setup_engine_discovery_uses_runtime_bash_resolution(self):
        text = self.read(".agents/skills/ccgs-setup-engine/SKILL.md")
        self.assertIn("context.bash_executable()", text)
        self.assertIn("do not edit global PATH", text)


if __name__ == "__main__":
    unittest.main()
