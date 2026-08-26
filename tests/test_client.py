from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from bcast import BcastPackage, ObjectNotFoundError, PackageValidationError, validate_package
from bcast.cli import main as cli_main

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "examples" / "synthetic" / "valid" / "package-0.1.0.json"
SPEC_SCHEMA = ROOT / "spec" / "schemas" / "package-0.1.0.schema.json"


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_id(prefix, payload):
    return f"{prefix}:sha256:{hashlib.sha256(canonical_json(payload).encode('utf-8')).hexdigest()}"


class ClientTests(unittest.TestCase):
    def load_fixture(self):
        return json.loads(VALID.read_text(encoding="utf-8"))

    def test_valid_package_loads_and_projects_metadata(self):
        package = BcastPackage.load(VALID)
        self.assertEqual("bcast.package/0.1.0", package.schema_version)
        self.assertEqual("2026.08.synthetic.1", package.package_version)
        self.assertEqual(package.package_id, package.metadata()["package_id"])
        self.assertNotIn("objects", package.metadata())

    def test_embedded_schema_matches_maintained_companion_schema(self):
        package_schema = BcastPackage.schema()
        maintained_schema = json.loads(SPEC_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(maintained_schema, package_schema)

    def test_wrong_identity_is_rejected(self):
        candidate = self.load_fixture()
        candidate["package_id"] = f"bcastpkg:sha256:{'0' * 64}"
        with self.assertRaisesRegex(PackageValidationError, "package_id does not match canonical package identity"):
            validate_package(candidate)

    def test_missing_parent_is_rejected(self):
        candidate = self.load_fixture()
        candidate["objects"][1]["parent_id"] = f"bcastobj:sha256:{'0' * 64}"
        with self.assertRaisesRegex(PackageValidationError, "missing parent object"):
            validate_package(candidate)

    def test_object_lookup_returns_unresolved_record_instead_of_error(self):
        candidate = self.load_fixture()
        candidate["objects"][1]["status"] = "unresolved"
        package = BcastPackage.from_mapping(candidate)
        record = package.get_object(candidate["objects"][1]["object_id"])
        self.assertEqual("unresolved", record["status"])

    def test_unknown_object_is_not_found(self):
        package = BcastPackage.load(VALID)
        missing = f"bcastobj:sha256:{'f' * 64}"
        with self.assertRaises(ObjectNotFoundError) as captured:
            package.get_object(missing)
        self.assertEqual(missing, captured.exception.object_id)

    def test_children_are_direct_only_and_sorted_by_object_id(self):
        candidate = self.load_fixture()
        publication_id = candidate["publication"]["publication_id"]
        root_id = candidate["objects"][0]["object_id"]
        section_id = candidate["objects"][1]["object_id"]
        second = {
            "object_id": stable_id("bcastobj", {"kind": "section", "locator": "1.0", "publication_id": publication_id}),
            "kind": "section",
            "locator": "1.0",
            "parent_id": root_id,
            "status": "resolved",
            "assurance": "reviewed",
        }
        grandchild = {
            "object_id": stable_id("bcastobj", {"kind": "paragraph", "locator": "1.1.a", "publication_id": publication_id}),
            "kind": "paragraph",
            "locator": "1.1.a",
            "parent_id": section_id,
            "status": "resolved",
            "assurance": "reviewed",
        }
        candidate["objects"].extend([second, grandchild])
        package = BcastPackage.from_mapping(candidate)
        children = package.children(root_id)
        self.assertEqual(sorted([section_id, second["object_id"]]), [item["object_id"] for item in children])
        self.assertNotIn(grandchild["object_id"], [item["object_id"] for item in children])

    def test_cli_validate_and_get_use_only_local_package(self):
        out = io.StringIO()
        with redirect_stdout(out):
            rc = cli_main(["validate", str(VALID)])
        self.assertEqual(0, rc)
        self.assertIn("OK", out.getvalue())

        object_id = self.load_fixture()["objects"][1]["object_id"]
        out = io.StringIO()
        with redirect_stdout(out):
            rc = cli_main(["get", str(VALID), object_id])
        self.assertEqual(0, rc)
        self.assertEqual(object_id, json.loads(out.getvalue())["object_id"])

        root_id = self.load_fixture()["objects"][0]["object_id"]
        out = io.StringIO()
        with redirect_stdout(out):
            rc = cli_main(["children", str(VALID), root_id])
        self.assertEqual(0, rc)
        self.assertEqual([object_id], [item["object_id"] for item in json.loads(out.getvalue())])

    def test_cli_validation_failure_is_nonzero_and_source_safe(self):
        candidate = self.load_fixture()
        candidate["schema_version"] = "private.compiler/99"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate.json"
            path.write_text(json.dumps(candidate), encoding="utf-8")
            err = io.StringIO()
            with redirect_stderr(err):
                rc = cli_main(["validate", str(path)])
        self.assertEqual(1, rc)
        self.assertIn("schema_version", err.getvalue())
        self.assertNotIn("provider", err.getvalue().lower())


if __name__ == "__main__":
    unittest.main()
