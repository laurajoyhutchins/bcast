from __future__ import annotations

from contextlib import redirect_stdout
import io
import threading
import unittest

from bcast import BcastApiClient, BcastApiProblem, BcastPackage, package_id, publication_id, regulatory_object_id
from bcast.cli import main as cli_main
from bcast.server import make_server


class ApiClientServerTests(unittest.TestCase):
    def make_package(self) -> BcastPackage:
        publication = publication_id("example-safety-code", "2026")
        root = regulatory_object_id(publication, "document", "root")
        section_a = regulatory_object_id(publication, "section", "1.0")
        section_b = regulatory_object_id(publication, "section", "1.1")
        return BcastPackage({
            "schema_version": "bcast.package/0.1.0",
            "package_id": package_id(publication, "2026.08.synthetic.1"),
            "package_version": "2026.08.synthetic.1",
            "publication": {
                "publication_id": publication,
                "family": "example-safety-code",
                "edition": "2026",
            },
            "objects": [
                {
                    "object_id": root,
                    "kind": "document",
                    "locator": "root",
                    "status": "resolved",
                    "assurance": "verified",
                },
                {
                    "object_id": section_b,
                    "kind": "section",
                    "locator": "1.1",
                    "parent_id": root,
                    "status": "unresolved",
                    "assurance": "reviewed",
                },
                {
                    "object_id": section_a,
                    "kind": "section",
                    "locator": "1.0",
                    "parent_id": root,
                    "status": "resolved",
                    "assurance": "reviewed",
                },
            ],
        })

    def run_server(self):
        package = self.make_package()
        server = make_server([package], host="127.0.0.1", port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return package, f"http://127.0.0.1:{server.server_port}"

    def test_normative_identity_helpers_match_maintained_fixture_coordinates(self):
        publication = publication_id("example-safety-code", "2026")
        self.assertEqual(
            "bcastpub:sha256:cdc0d4941affb103cc10a87b6a206094ff02f0790795b79a909a5ea0ac3be0e8",
            publication,
        )
        self.assertEqual(
            "bcastpkg:sha256:51b6229012ad1f71303d9018e0e7e9fdfc68fb66724e258dbd767979ccf2cea1",
            package_id(publication, "2026.08.synthetic.1"),
        )

    def test_reference_server_round_trips_only_public_contract_shapes(self):
        package, base_url = self.run_server()
        client = BcastApiClient(base_url)
        metadata = client.get_package_metadata(package.package_id)
        self.assertEqual(package.package_id, metadata["package_id"])
        self.assertNotIn("objects", metadata)

        root = package.as_dict()["objects"][0]["object_id"]
        children = client.get_children(package.package_id, root)
        self.assertEqual(
            sorted(item["object_id"] for item in children),
            [item["object_id"] for item in children],
        )
        self.assertEqual({"object_id", "kind", "locator", "parent_id", "status", "assurance"}, set(children[0]))

        unresolved = package.as_dict()["objects"][1]["object_id"]
        self.assertEqual("unresolved", client.get_object(package.package_id, unresolved)["status"])

    def test_not_found_is_structured_problem(self):
        package, base_url = self.run_server()
        client = BcastApiClient(base_url)
        missing = f"bcastobj:sha256:{'f' * 64}"
        with self.assertRaises(BcastApiProblem) as captured:
            client.get_object(package.package_id, missing)
        self.assertEqual("not_found", captured.exception.code)
        self.assertEqual(404, captured.exception.http_status)
        self.assertEqual(missing, captured.exception.resource_id)

    def test_remote_cli_exercises_api_contract(self):
        package, base_url = self.run_server()
        out = io.StringIO()
        with redirect_stdout(out):
            rc = cli_main(["api", base_url, "metadata", package.package_id])
        self.assertEqual(0, rc)
        self.assertIn(package.package_id, out.getvalue())


if __name__ == "__main__":
    unittest.main()
