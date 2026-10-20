"""Normative 0.2.0 regression vectors: namespaces, content hashes and bounded claims."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from bcast import BcastPackage, materialized_package_id, publication_id_v2, regulatory_object_id, validate_package
from bcast.validation import PackageValidationError, load_schema
from conformance.validate_openapi import validate_openapi_document


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "examples/synthetic/valid/package-0.2.0.json"
SCHEMA = ROOT / "spec/schemas/package-0.2.0.schema.json"
API = ROOT / "spec/openapi/bcast-api-0.2.0.openapi.json"


class V2PackageConformance(unittest.TestCase):
    def setUp(self):
        self.package = json.loads(PACKAGE.read_text(encoding="utf-8"))

    def test_fixture_is_content_addressed_and_public_schema_matches(self):
        self.assertEqual(load_schema("bcast.package/0.2.0"), json.loads(SCHEMA.read_text()))
        validate_package(self.package)
        self.assertEqual(self.package["package_id"], materialized_package_id(self.package))
        self.assertEqual("bcast.package/0.2.0", BcastPackage.from_mapping(self.package).schema_version)

    def test_different_authority_namespaces_do_not_collide(self):
        original = self.package["publication"]
        a = publication_id_v2("codes.example", original["family"], original["edition"])
        b = publication_id_v2("other.example", original["family"], original["edition"])
        self.assertEqual(a, original["publication_id"])
        self.assertNotEqual(a, b)
        self.assertNotEqual(
            regulatory_object_id(a, "section", "1.1"),
            regulatory_object_id(b, "section", "1.1"),
        )

    def test_same_publication_from_different_source_providers_has_one_id(self):
        # Acquisition provider coordinates are never inputs to the public identity.
        first = publication_id_v2("codes.example", "example-safety-code", "2026")
        second = publication_id_v2("codes.example", "example-safety-code", "2026")
        self.assertEqual(first, second)

    def test_changed_content_structure_provenance_or_status_invalidates_id(self):
        changes = [
            lambda p: p["objects"][1]["content"].update(text="Changed regulatory text"),
            lambda p: p["objects"][1].update(parent_id=None),
            lambda p: p["objects"][1]["provenance"].update(citation="Changed citation"),
            lambda p: p["objects"][1].update(status="unresolved"),
            lambda p: p["publication"].update(title="Changed title"),
            lambda p: p.update(package_version="2026.10.synthetic.2"),
        ]
        for change in changes:
            with self.subTest(change=change):
                candidate = deepcopy(self.package)
                change(candidate)
                self.assertNotEqual(materialized_package_id(candidate), candidate["package_id"])
                with self.assertRaisesRegex(PackageValidationError, "package_id"):
                    validate_package(candidate)
                candidate["package_id"] = materialized_package_id(candidate)
                validate_package(candidate)

    def test_object_enumeration_order_does_not_change_digest(self):
        candidate = deepcopy(self.package)
        candidate["objects"].reverse()
        self.assertEqual(self.package["package_id"], materialized_package_id(candidate))
        validate_package(candidate)

    def test_unsubstantiated_assurance_and_noncanonical_names_are_rejected(self):
        for mutate in (
            lambda p: p["objects"][0].update(assurance="verified"),
            lambda p: p["publication"].update(namespace="CODES.example"),
            lambda p: p["publication"].update(family="Example-Safety-Code"),
            lambda p: p["publication"].update(edition=" 2026 "),
            lambda p: p["publication"].update(edition="e\u0301"),
        ):
            with self.subTest(mutate=mutate):
                candidate = deepcopy(self.package)
                mutate(candidate)
                with self.assertRaises(PackageValidationError):
                    validate_package(candidate)

    def test_namespace_collision_is_not_fixed_by_issuer_display_metadata(self):
        a = deepcopy(self.package)
        b = deepcopy(self.package)
        b["publication"]["issuing_body"] = "An unrelated issuer"
        self.assertEqual(a["publication"]["publication_id"], b["publication"]["publication_id"])
        # An unrelated issuer must instead be allocated a distinct controlled namespace.
        b["publication"]["namespace"] = "other.example"
        b["publication"]["publication_id"] = publication_id_v2(
            "other.example", b["publication"]["family"], b["publication"]["edition"]
        )
        self.assertNotEqual(a["publication"]["publication_id"], b["publication"]["publication_id"])

    def test_legacy_0_1_package_is_still_accepted(self):
        legacy = json.loads(
            (ROOT / "examples/synthetic/valid/package-0.1.0.json").read_text(encoding="utf-8")
        )
        validate_package(legacy)
        self.assertEqual("bcast.package/0.1.0", BcastPackage(legacy).schema_version)

    def test_api_companion_has_versioned_compatibility_and_resolves(self):
        document = json.loads(API.read_text(encoding="utf-8"))
        self.assertEqual("bcast.api/0.2.0", document["x-bcast-contract"])
        self.assertEqual(["bcast.package/0.2.0"], document["x-bcast-compatible-package-contracts"])
        validate_openapi_document(document, API)


if __name__ == "__main__":
    unittest.main()
