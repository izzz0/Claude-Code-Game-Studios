"""Static input-completeness regression for native architecture case 006."""

import copy
import json
from pathlib import Path
import re
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "studio-tests/native/fixtures/architecture-decision"
LAYERS = {"Foundation", "Core", "Feature", "Presentation"}


def delivery_service_layer(architecture_file):
    if not architecture_file.is_file():
        return None
    layer = None
    for line in architecture_file.read_text(encoding="utf-8").splitlines():
        heading = re.fullmatch(r"### (Foundation|Core|Feature|Presentation) Layer", line.strip())
        if heading:
            layer = heading.group(1)
        elif layer and "**DeliveryService**" in line:
            return layer
    return None


class NativeArchitectureCaseTests(unittest.TestCase):
    def test_missing_layer_map_needs_input_and_supplied_map_resolves_feature(self):
        contract = (ROOT / ".agents/skills/ccgs-architecture-decision/references/5-generate.md").read_text(
            encoding="utf-8"
        )
        self.assertRegex(contract, r"With no layer map, or no system in it, ask the\s+user")
        with tempfile.TemporaryDirectory() as temp:
            legacy_architecture = Path(temp) / "architecture.md"
            self.assertIsNone(delivery_service_layer(legacy_architecture))

        configured_layer = delivery_service_layer(FIXTURE / "docs/architecture/architecture.md")
        self.assertEqual(configured_layer, "Feature")
        self.assertIn(configured_layer, LAYERS)

        catalog = json.loads((ROOT / "studio-tests/native/cases.json").read_text(encoding="utf-8"))
        case = next(item for item in catalog["cases"] if item["id"] == "native-006-ccgs-architecture-decision")
        self.assertIn("Feature layer of the Gameplay Domain", case["prompt"])
        self.assertIn("scene adapters call the service", case["prompt"])
        self.assertIn("neither scenes nor persistence own delivery state", case["prompt"])
        self.assertIn("pending separate approval", case["prompt"])
        self.assertIn("do not modify the registry", case["prompt"])

        project = (FIXTURE / "project.yaml").read_text(encoding="utf-8")
        self.assertIn("rigor: standard", project)
        self.assertIn("automation: guided", project)
        part = json.loads((ROOT / "studio-tests/native/case-parts/design-quality.json").read_text(encoding="utf-8"))
        part_case = next(item for item in part["cases"] if item["id"] == case["id"])
        part_expected = copy.deepcopy(part_case["expected"])
        part_expected["config"] = part_case["config"]
        self.assertEqual(case["expected"], part_expected)
        self.assertEqual(case["expected"]["files"][0]["contains"][5:7], ["**Layer**", "Feature"])
        self.assertEqual(case["expected"]["files"][-1]["path"], "docs/registry/architecture.yaml")
        self.assertFalse(case["expected"]["files"][-1]["changed"])


if __name__ == "__main__":
    unittest.main()
