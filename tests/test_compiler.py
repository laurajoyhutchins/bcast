"""Source-independent checks for the public BCAST 0.2 materializer."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from bcast import PackageValidationError, build_package_v2, materialized_package_id


FIXTURE = Path(__file__).resolve().parents[1] / "examples/synthetic/valid/package-0.2.0.json"


def normalized_fixture():
    package = json.loads(FIXTURE.read_text(encoding="utf-8"))
    # The public fixture deliberately uses editorial enumeration order, while
    # the package builder emits canonical sorted records.
    package["objects"].sort(key=lambda record: record["object_id"])
    by_id = {record["object_id"]: record for record in package["objects"]}
    metadata = {
        key: value for key, value in package["publication"].items() if key != "publication_id"
    }
    drafts = []
    for record in package["objects"]:
        draft = {
            key: deepcopy(value)
            for key, value in record.items()
            if key not in {"object_id", "parent_id"}
        }
        if "parent_id" in record:
            parent = by_id[record["parent_id"]]
            draft["parent"] = {"kind": parent["kind"], "locator": parent["locator"]}
        drafts.append(draft)
    return package, metadata, drafts


class PublicPackageBuilderTests(unittest.TestCase):
    def test_fixture_materializes_with_exact_identity_and_structure(self):
        fixture, metadata, drafts = normalized_fixture()
        result = build_package_v2(
            publication=metadata, package_version=fixture["package_version"], objects=drafts
        )
        self.assertEqual(fixture, result)
        self.assertEqual(fixture["package_id"], materialized_package_id(result))

    def test_input_order_and_mutations_do_not_affect_completed_package(self):
        fixture, metadata, drafts = normalized_fixture()
        first = build_package_v2(
            publication=metadata, package_version=fixture["package_version"], objects=drafts
        )
        second = build_package_v2(
            publication=metadata,
            package_version=fixture["package_version"],
            objects=reversed(drafts),
        )
        self.assertEqual(first, second)
        metadata["title"] = "Mutated after compilation"
        next(item for item in drafts if item["kind"] == "section")["content"]["text"] = (
            "Mutated after compilation"
        )
        self.assertEqual(fixture, first)

    def test_changes_in_content_or_source_provenance_change_materialization(self):
        fixture, metadata, drafts = normalized_fixture()
        for changed_field in ("content", "provenance"):
            with self.subTest(changed_field=changed_field):
                modified = deepcopy(drafts)
                if changed_field == "content":
                    next(item for item in modified if item["kind"] == "section")["content"][
                        "text"
                    ] += " Updated"
                else:
                    modified[1]["provenance"]["citation"] += " Updated"
                result = build_package_v2(
                    publication=metadata,
                    package_version=fixture["package_version"],
                    objects=modified,
                )
                self.assertNotEqual(fixture["package_id"], result["package_id"])

    def test_invalid_parent_cycle_duplicate_and_unsupported_claim_fail_closed(self):
        fixture, metadata, drafts = normalized_fixture()
        cases = []
        missing = deepcopy(drafts)
        missing[1]["parent"] = {"kind": "document", "locator": "nonexistent"}
        cases.append(missing)
        cycle = deepcopy(drafts)
        cycle[0]["parent"] = {"kind": "section", "locator": "1.1"}
        cases.append(cycle)
        duplicate = deepcopy(drafts)
        duplicate.append(deepcopy(drafts[1]))
        cases.append(duplicate)
        invalid = deepcopy(drafts)
        invalid[1]["status"] = "imaginary"
        cases.append(invalid)
        for items in cases:
            with self.subTest(items=items), self.assertRaises(PackageValidationError):
                build_package_v2(
                    publication=metadata, package_version=fixture["package_version"], objects=items
                )

    def test_derived_ids_cannot_be_supplied_by_adapter(self):
        fixture, metadata, drafts = normalized_fixture()
        for extra in ("object_id", "parent_id"):
            modified = deepcopy(drafts)
            modified[0][extra] = "bad"
            with self.subTest(extra=extra), self.assertRaisesRegex(ValueError, "derived"):
                build_package_v2(
                    publication=metadata,
                    package_version=fixture["package_version"],
                    objects=modified,
                )
        metadata["publication_id"] = fixture["publication"]["publication_id"]
        with self.assertRaisesRegex(ValueError, "derived"):
            build_package_v2(
                publication=metadata, package_version=fixture["package_version"], objects=drafts
            )

    def test_malformed_parent_is_rejected_before_hashing(self):
        fixture, metadata, drafts = normalized_fixture()
        modified = deepcopy(drafts)
        modified[1]["parent"] = {
            "kind": "document",
            "locator": "root",
            "source_provider_id": "private",
        }
        with self.assertRaisesRegex(ValueError, "parent must identify"):
            build_package_v2(
                publication=metadata, package_version=fixture["package_version"], objects=modified
            )


if __name__ == "__main__":
    unittest.main()
