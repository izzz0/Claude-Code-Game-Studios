import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INSPECT = ROOT / ".agents" / "studio" / "scripts" / "studio-inspect.py"

class InspectionTests(unittest.TestCase):
    def test_json_separates_configured_discovered_observed_and_unconfirmed(self):
        result = subprocess.run([sys.executable, str(INSPECT), str(ROOT), "--json"], text=True,
                                capture_output=True, check=True)
        report = json.loads(result.stdout)
        self.assertEqual(set(report), {"configured", "discovered", "observed", "trust_unconfirmed"})
        self.assertEqual(report["discovered"]["skills"], 74)
        self.assertEqual(report["discovered"]["roles"], 49)
        self.assertEqual(report["discovered"]["teams"], 9)
        self.assertIn("role_execution", report["trust_unconfirmed"])
        self.assertFalse(report["observed"]["hook_observed"])

    def test_manifest_or_role_files_do_not_claim_execution(self):
        result = subprocess.run([sys.executable, str(INSPECT), str(ROOT)], text=True,
                                capture_output=True, check=True)
        self.assertIn("TRUST_UNCONFIRMED:", result.stdout)

if __name__ == "__main__":
    unittest.main()
