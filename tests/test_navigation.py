from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import unittest

from bcast import BcastPackage, ObjectCoordinateNotFoundError, regulatory_object_id
from bcast.cli import main as cli_main

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "examples" / "synthetic" / "valid" / "package-0.1.0.json"


class NavigationTests(unittest.TestCase):
    def package_with_tree(self):
        candidate = json.loads(VALID.read_text(encoding="utf-8"))
        publication_id = candidate["publication"]["publication_id"]
        root = candidate["objects"][0]
        section = candidate["objects"][1]
        sibling = {
            "object_id": regulatory_object_id(publication_id, "section", "1.0"),
            "kind": "section",
            "locator": "1.0",
            "parent_id": root["object_id"],
            "label": "Scope",
            "status": "resolved",
            "assurance": "verified",
            "provenance": {"citation": "Project-authored synthetic fixture, Section 1.0"},
        }
        grandchild = {
            "object_id": regulatory_object_id(publication_id, "section", "1.1.1"),
            "kind": "section",
            "locator": "1.1.1",
            "parent_id": section["object_id"],
            "label": "Synthetic Detail",
            "status": "resolved",
            "assurance": "verified",
            "provenance": {"citation": "Project-authored synthetic fixture, Section 1.1.1"},
        }
        candidate["objects"].extend([sibling, grandchild])
        return BcastPackage.from_mapping(candidate), root, section, sibling, grandchild

    def test_structural_navigation_uses_only_parent_id(self):
        package, root, section, sibling, grandchild = self.package_with_tree()
        self.assertEqual([root["object_id"]], [item["object_id"] for item in package.roots()])
        self.assertIsNone(package.parent(root["object_id"]))
        self.assertEqual(root["object_id"], package.parent(section["object_id"])["object_id"])
        self.assertEqual(
            [root["object_id"], section["object_id"]],
            [item["object_id"] for item in package.ancestors(grandchild["object_id"])],
        )
        expected = sorted([section["object_id"], sibling["object_id"], grandchild["object_id"]])
        self.assertEqual(expected, [item["object_id"] for item in package.descendants(root["object_id"])])

    def test_exact_coordinate_lookup_is_public_and_explicit(self):
        package, _, section, _, _ = self.package_with_tree()
        self.assertEqual(section["object_id"], package.find("section", "1.1")["object_id"])
        with self.assertRaises(ObjectCoordinateNotFoundError) as captured:
            package.find("section", "404")
        self.assertEqual(("section", "404"), (captured.exception.kind, captured.exception.locator))

    def test_tree_cli_prints_public_structure_deterministically(self):
        out = io.StringIO()
        with redirect_stdout(out):
            rc = cli_main(["tree", str(VALID)])
        self.assertEqual(0, rc)
        self.assertEqual(
            [
                "document root Example Safety Code",
                "  section 1.1 Clearances",
            ],
            out.getvalue().splitlines(),
        )


if __name__ == "__main__":
    unittest.main()
