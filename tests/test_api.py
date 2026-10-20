from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from bcast import BcastApiClient, BcastApiProblem, BcastApiProtocolError, BcastPackage, PackageValidationError, package_id, publication_id, regulatory_object_id
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

    def run_hostile_server(self, initial_payload):
        response = {"payload": initial_payload}

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                return

            def do_GET(self):
                body = json.dumps(response["payload"]).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return f"http://127.0.0.1:{server.server_port}", lambda value: response.update(payload=value)

    def test_adversarial_metadata_responses_fail_closed(self):
        package = self.make_package()
        valid = package.metadata()
        base_url, change_response = self.run_hostile_server(valid)
        client = BcastApiClient(base_url)
        self.assertEqual(package.package_id, client.get_package_metadata(package.package_id)["package_id"])
        variants = [
            {**valid, "package_id": f"bcastpkg:sha256:{'f' * 64}"},
            {**valid, "private_compiler_state": "not public"},
            {**valid, "publication": {**valid["publication"], "provider_key": "private"}},
            {**valid, "publication": {**valid["publication"], "edition": "2030"}},
            {**valid, "package_version": "2030.other"},
            {**valid, "schema_version": "bcast.package/unknown"},
            ["not", "metadata"],
        ]
        for payload in variants:
            with self.subTest(payload=payload):
                change_response(payload)
                with self.assertRaises(BcastApiProtocolError):
                    client.get_package_metadata(package.package_id)

    def test_adversarial_full_package_response_cannot_substitute_identity(self):
        package = self.make_package()
        valid = package.as_dict()
        base_url, change_response = self.run_hostile_server(valid)
        client = BcastApiClient(base_url)
        self.assertEqual(valid, client.get_package(package.package_id))
        with self.assertRaisesRegex(BcastApiProtocolError, "identity"):
            client.get_package(f"bcastpkg:sha256:{'f' * 64}")

        invalid = {**valid, "objects": [{**valid["objects"][0], "private_key": "not public"}, *valid["objects"][1:]]}
        change_response(invalid)
        with self.assertRaises(BcastApiProtocolError):
            client.get_package(package.package_id)

    def test_adversarial_object_response_checks_shape_and_requested_identity(self):
        package = self.make_package()
        valid = package.as_dict()["objects"][0]
        base_url, change_response = self.run_hostile_server(valid)
        client = BcastApiClient(base_url)
        self.assertEqual(valid, client.get_object(package.package_id, valid["object_id"]))
        for payload in [
            valid,
            {**valid, "private_source_locator": "secret"},
            {**valid, "status": "unknown"},
            {"object_id": valid["object_id"]},
        ]:
            with self.subTest(payload=payload):
                change_response(payload)
                requested = f"bcastobj:sha256:{'f' * 64}" if payload is valid else valid["object_id"]
                with self.assertRaises(BcastApiProtocolError):
                    client.get_object(package.package_id, requested)

    def test_adversarial_children_require_direct_unique_sorted_public_records(self):
        package = self.make_package()
        root = package.as_dict()["objects"][0]["object_id"]
        valid = package.children(root)
        self.assertEqual(2, len(valid))
        base_url, change_response = self.run_hostile_server(valid)
        client = BcastApiClient(base_url)
        self.assertEqual(valid, client.get_children(package.package_id, root))
        for payload in [
            list(reversed(valid)),
            [valid[0], valid[0]],
            [{**valid[0], "parent_id": f"bcastobj:sha256:{'f' * 64}"}],
            [{**valid[0], "private_review": True}],
            [{**valid[0], "assurance": "approved"}],
            [valid[0], "not an object"],
        ]:
            with self.subTest(payload=payload):
                change_response(payload)
                with self.assertRaises(BcastApiProtocolError):
                    client.get_children(package.package_id, root)

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

    def test_reference_server_cannot_accept_unvalidated_package(self):
        valid = self.make_package().as_dict()
        valid["objects"][0]["status"] = "not-a-public-state"
        with self.assertRaises(PackageValidationError):
            # Construction must fail before the package can enter make_server.
            make_server([BcastPackage(valid)], host="127.0.0.1", port=0)

        valid = self.make_package().as_dict()
        valid["objects"][1]["parent_id"] = f"bcastobj:sha256:{'f' * 64}"
        with self.assertRaisesRegex(PackageValidationError, "missing parent object"):
            make_server([BcastPackage(valid)], host="127.0.0.1", port=0)

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
