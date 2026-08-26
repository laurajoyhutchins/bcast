from copy import deepcopy
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from conformance.validate import load_json, validate_semantics


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "spec" / "schemas" / "package-0.1.schema.json"
PACKAGE_PATH = ROOT / "examples" / "synthetic" / "package-0.1.json"


class PackageConformanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.package = load_json(PACKAGE_PATH)

    def test_synthetic_fixture_conforms(self) -> None:
        schema = load_json(SCHEMA_PATH)
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        errors = sorted(
            validator.iter_errors(self.package),
            key=lambda item: list(item.absolute_path),
        )
        self.assertEqual([], [error.message for error in errors])
        self.assertEqual([], validate_semantics(PACKAGE_PATH, self.package))

    def test_wrong_package_identity_is_rejected(self) -> None:
        candidate = deepcopy(self.package)
        candidate["package_id"] = f"bcastpkg:sha256:{'0' * 64}"
        failures = validate_semantics(Path("wrong-package-id.json"), candidate)
        self.assertTrue(
            any("package_id does not match canonical package identity" in failure for failure in failures)
        )

    def test_missing_parent_is_rejected(self) -> None:
        candidate = deepcopy(self.package)
        candidate["objects"][1]["parent_id"] = f"bcastobj:sha256:{'0' * 64}"
        failures = validate_semantics(Path("missing-parent.json"), candidate)
        self.assertTrue(any("missing parent object" in failure for failure in failures))

    def test_structural_parent_cycle_is_rejected(self) -> None:
        candidate = deepcopy(self.package)
        document = candidate["objects"][0]
        section = candidate["objects"][1]
        document["parent_id"] = section["object_id"]
        failures = validate_semantics(Path("parent-cycle.json"), candidate)
        self.assertTrue(any("structural parent cycle" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()