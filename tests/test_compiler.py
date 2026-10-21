"""Source-independent, synthetic compilation and fail-closed regressions."""

from __future__ import annotations

from copy import deepcopy
import unittest

from bcast import BcastPackage, PackageValidationError, compile_package


ROOT = {"kind": "document", "locator": "root", "label": "Synthetic code", "status": "resolved"}
SECTION = {
    "kind": "section", "locator": "1.1", "status": "resolved",
    "parent": {"kind": "document", "locator": "root"},
    "content": {"media_type": "text/plain", "text": "Project-authored synthetic requirement."},
    "provenance": {"citation": "Synthetic section 1.1"},
}
PARAMETERS = {
    "namespace": "codes.example", "family": "example-code", "edition": "2026",
    "package_version": "2026.synthetic.1", "title": "Synthetic code", "issuing_body": "Fixture author",
}


class CompilerTests(unittest.TestCase):
    def build(self, *items, **overrides):
        return compile_package(**(PARAMETERS | overrides), objects=items)

    def test_builds_a_valid_navigable_package_from_unidentified_coordinates(self):
        original = [deepcopy(SECTION), deepcopy(ROOT)]
        package = self.build(*original)
        self.assertEqual([SECTION, ROOT], original)
        client = BcastPackage(package)
        root = client.find("document", "root")
        self.assertEqual("1.1", client.children(root["object_id"])[0]["locator"])
        self.assertNotIn("assurance", package["objects"][0])
        self.assertEqual("bcast.package/0.2.0", client.schema_version)

    def test_enumeration_order_does_not_change_materialization_or_ids(self):
        forward = self.build(ROOT, SECTION)
        reverse = self.build(SECTION, ROOT)
        self.assertEqual(forward, reverse)
        self.assertEqual(forward["package_id"], reverse["package_id"])

    def test_content_and_provenance_change_package_identity_not_object_identity(self):
        before = self.build(ROOT, SECTION)
        edited = deepcopy(SECTION)
        edited["content"]["text"] += " Updated."
        after = self.build(ROOT, edited)
        self.assertNotEqual(before["package_id"], after["package_id"])
        before_by_coordinate = {(x["kind"], x["locator"]): x["object_id"] for x in before["objects"]}
        after_by_coordinate = {(x["kind"], x["locator"]): x["object_id"] for x in after["objects"]}
        self.assertEqual(before_by_coordinate, after_by_coordinate)
        edited["provenance"]["citation"] = "Changed source"
        self.assertNotEqual(after["package_id"], self.build(ROOT, edited)["package_id"])

    def test_revision_changes_publication_identity(self):
        old = self.build(ROOT)
        new = self.build(ROOT, revision="a")
        self.assertNotEqual(old["publication"]["publication_id"], new["publication"]["publication_id"])

    def test_unresolved_and_unsupported_status_preserved_without_fabricating_text(self):
        for status in ("unresolved", "unsupported"):
            with self.subTest(status=status):
                record = SECTION | {"status": status}
                record.pop("content")
                package = self.build(ROOT, record)
                self.assertEqual(status, BcastPackage(package).find("section", "1.1")["status"])

    def test_duplicate_coordinates_and_parent_cycles_fail_closed(self):
        bad = [
            (ROOT, deepcopy(ROOT)),
            (SECTION,),
            (ROOT | {"parent": {"kind": "section", "locator": "1.1"}}, SECTION),
        ]
        for objects in bad:
            with self.subTest(objects=objects), self.assertRaises(PackageValidationError):
                self.build(*objects)

    def test_untrusted_identity_and_extra_metadata_cannot_be_injected(self):
        for key in ("object_id", "parent_id", "assurance", "provider_id"):
            with self.subTest(key=key), self.assertRaises(PackageValidationError):
                self.build(ROOT | {key: "untrusted"})
        with self.assertRaises(PackageValidationError):
            self.build(ROOT, SECTION | {"parent": {"kind": "document", "locator": "root", "id": "nope"}})

    def test_invalid_source_neutral_inputs_fail_closed(self):
        cases = [
            (ROOT | {"kind": "injected"},),
            (ROOT | {"locator": ""},),
            (ROOT | {"status": "verified"},),
            (ROOT | {"content": {"media_type": "text/html", "text": "X"}},),
            (ROOT | {"parent": {"kind": "section", "locator": "missing"}},),
            (ROOT | {"parent": {"kind": "document", "locator": "root"}},),
            (ROOT | {"parent": "root"},),
            ({"kind": "document", "locator": "root"},),
        ]
        for records in cases:
            with self.subTest(records=records), self.assertRaises(PackageValidationError):
                self.build(*records)
        with self.assertRaises(PackageValidationError):
            self.build(ROOT, namespace="Provider-ID")


if __name__ == "__main__":
    unittest.main()
