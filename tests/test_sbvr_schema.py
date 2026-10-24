"""Structural JSON Schema conformance for SBVR-style proposal batches.

Rust semantic admission additionally verifies content digests, IDs, and accounting.
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads(
    (ROOT / "spec/schemas/sbvr-proposal-batch-0.1.0.schema.json").read_text(encoding="utf-8")
)


class SbvrBatchSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Draft202012Validator.check_schema(SCHEMA)
        cls.validator = Draft202012Validator(SCHEMA)

    def minimal(self):
        sha = "a" * 64
        return {
            "schema_version": "bcast.sbvr_proposal_batch/0.1.0",
            "baseline": {"schema_version": "bcast.rule_ir/0.1.0", "editions": [{}]},
            "source": {
                "namespace": "study.example",
                "family": "fictional-code",
                "edition": "2017",
                "publication_id": "bcastpub:sha256:" + sha,
                "package_id": "bcastpkg:sha256:" + sha,
                "artifact_sha256": sha,
                "media_type": "application/pdf",
            },
            "source_package": {
                "schema_version": "bcast.package/0.2.0",
                "package_version": "source-witness/1",
                "publication": {
                    "publication_id": "bcastpub:sha256:" + sha,
                    "namespace": "study.example",
                    "family": "fictional-code",
                    "edition": "2017",
                },
                "objects": [
                    {
                        "object_id": "bcastobj:sha256:" + sha,
                        "kind": "section",
                        "locator": "210.19(A)(3)",
                        "status": "unresolved",
                        "provenance": {
                            "citation": "Synthetic test",
                            "source_artifact_sha256": sha,
                        },
                    }
                ],
                "package_id": "bcastpkg:sha256:" + sha,
            },
            "passages": [
                {
                    "passage_id": "bcastpassage:sha256:" + sha,
                    "kind": "section",
                    "locator": "210.19(A)(3)",
                    "source_object_id": "bcastobj:sha256:" + sha,
                    "pdf_page": 65,
                    "bbox_millipoints": [1000, 2000, 3000, 4000],
                    "text": "synthetic text",
                    "text_sha256": sha,
                }
            ],
            "proposals": [
                {
                    "proposal_id": "synthetic-permission",
                    "passage_id": "bcastpassage:sha256:" + sha,
                    "modality": "permission",
                    "disposition": "unresolved",
                    "dependencies": [{"locator": "Article 100", "resolved": False}],
                    "reason": "requires vocabulary review",
                }
            ],
            "accounting": {
                "extracted_passages": 1,
                "classified_passages": 1,
                "proposals": 1,
                "admitted": 0,
                "unresolved": 1,
                "rejected": 0,
            },
        }

    def test_schema_accepts_bounded_unresolved_batch(self):
        self.assertEqual([], list(self.validator.iter_errors(self.minimal())))

    def test_schema_rejects_shape_and_modality_errors(self):
        invalids = []
        x = self.minimal()
        x["proposals"][0]["modality"] = "recommendation"
        invalids.append(x)
        x = self.minimal()
        x["passages"][0]["text"] = "a" * 8193
        invalids.append(x)
        x = self.minimal()
        x["proposals"][0]["predicate"] = {"fact": "x", "op": "eq", "value": {"bool": True}}
        invalids.append(x)
        x = self.minimal()
        x["proposals"][0]["disposition"] = "admitted"
        invalids.append(x)
        x = self.minimal()
        x["source"]["publication_id"] = "not-a-hash"
        invalids.append(x)
        x = self.minimal()
        x["source_package"]["objects"][0]["kind"] = "made-up"
        invalids.append(x)
        x = self.minimal()
        del x["source_package"]
        invalids.append(x)
        for value in invalids:
            with self.subTest(value=value):
                self.assertTrue(list(self.validator.iter_errors(value)))


if __name__ == "__main__":
    unittest.main()
