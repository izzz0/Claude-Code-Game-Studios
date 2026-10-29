"""Inventory contracts for the source-host to native Codex migration."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "studio-tests" / "migration-manifest.json"
SOURCE_INVENTORY = ROOT / "studio-tests" / "source-inventory.json"


class MigrationInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.inventory = json.loads(SOURCE_INVENTORY.read_text(encoding="utf-8"))

    def test_inventory_counts_and_unique_source_names(self):
        self.assertEqual(len(self.manifest["skills"]), 74)
        self.assertEqual(len(self.manifest["roles"]), 49)
        self.assertEqual(len(self.manifest["hooks"]), 18)
        for kind in ("skills", "roles", "hooks"):
            rows = self.manifest[kind]
            self.assertEqual(len({row["source"] for row in rows}), len(rows), kind)
            self.assertEqual(self.inventory["counts"][kind], len(rows), kind)
            allowed = {"NOT ASSESSED", "PASS", "CONCERNS", "FAIL"}
            self.assertTrue(all(row.get("validation") in allowed for row in rows), kind)

    def test_source_inventory_is_pinned_to_fixed_revision_and_entrypoints_exist(self):
        self.assertEqual(self.inventory["source_revision"], self.manifest["source_revision"])
        inventory = {(row["kind"], row["source"]): row["blob"] for row in self.inventory["entries"]}
        for kind in ("skills", "roles"):
            for row in self.manifest[kind]:
                with self.subTest(kind=kind, name=row.get("name")):
                    self.assertRegex(inventory[(kind, row["source"])], r"^[0-9a-f]{40}$")
                    self.assertTrue((ROOT / row["entrypoint"]).is_file(), row["entrypoint"])
        expected = {(kind, row["source"]) for kind in ("skills", "roles", "hooks") for row in self.manifest[kind]}
        self.assertEqual(set(inventory), expected)
        for row in self.manifest["hooks"]:
            with self.subTest(source=row["source"]):
                self.assertRegex(inventory[("hooks", row["source"])], r"^[0-9a-f]{40}$")
                for replacement in row["replacement"].split(";"):
                    self.assertTrue((ROOT / replacement.strip()).is_file(), replacement)

    def test_hook_rows_have_concrete_native_mapping_and_provenance(self):
        allowed = {"static", "protocol", "native", "game", "unsupported"}
        self.assertEqual(set(self.manifest["provenance_contract"]), allowed)
        for row in self.manifest["hooks"]:
            with self.subTest(source=row["source"]):
                for field in ("event", "responsibility", "adaptation", "provenance"):
                    self.assertTrue(str(row.get(field, "")).strip(), field)
                self.assertIn(row["provenance"], allowed)
                self.assertNotEqual(row["replacement"], "pending runtime mapping")

    def test_validation_status_is_not_execution_evidence(self):
        rows = self.manifest["skills"] + self.manifest["roles"] + self.manifest["hooks"]
        self.assertTrue(all(row["validation"] != "PASS" or row.get("evidence") for row in rows))
        self.assertTrue(any(row["provenance"] == "unsupported" for row in self.manifest["hooks"]))


if __name__ == "__main__":
    unittest.main()
