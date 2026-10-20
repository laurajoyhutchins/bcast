"""Executable 0.1/0.2 interoperability facts, using actual maintained fixtures.

No invented 1.0 contract, provider adapter, private source material or hidden
best-effort schema upgrades belong in this test.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import threading
import unittest

from bcast import BcastApiClient, BcastApiProblem, BcastApiProtocolError, BcastPackage
from bcast.validation import PackageValidationError, validate_package
from bcast.server import make_server


FIXTURES = Path(__file__).resolve().parents[1] / "examples/synthetic/valid"


@contextmanager
def serve(package_contract: str, packages: list[BcastPackage]):
    server = make_server(packages, host="127.0.0.1", port=0, package_contract=package_contract)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


class MaintainedCompatibilityEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.legacy = BcastPackage.load(FIXTURES / "package-0.1.0.json")
        self.current = BcastPackage.load(FIXTURES / "package-0.2.0.json")

    def test_real_version_pair_has_distinct_publication_object_and_package_identity(self):
        old, new = self.legacy.as_dict(), self.current.as_dict()
        self.assertEqual(old["publication"]["family"], new["publication"]["family"])
        self.assertEqual(old["publication"]["edition"], new["publication"]["edition"])
        self.assertNotEqual(old["publication"]["publication_id"], new["publication"]["publication_id"])
        self.assertNotEqual(old["package_id"], new["package_id"])
        old_objects = {(x["kind"], x["locator"]): x for x in old["objects"]}
        new_objects = {(x["kind"], x["locator"]): x for x in new["objects"]}
        self.assertEqual(old_objects.keys(), new_objects.keys())
        for key in old_objects:
            self.assertNotEqual(old_objects[key]["object_id"], new_objects[key]["object_id"])
            self.assertIn("assurance", old_objects[key])
            self.assertNotIn("assurance", new_objects[key])
        self.assertNotIn("namespace", old["publication"])
        self.assertEqual("codes.example", new["publication"]["namespace"])

    def test_each_api_accepts_exact_pair_and_rejects_undeclared_package_contract(self):
        for contract, accepted, refused in [
            ("bcast.package/0.1.0", self.legacy, self.current),
            ("bcast.package/0.2.0", self.current, self.legacy),
        ]:
            with self.subTest(contract=contract), serve(contract, [accepted, refused]) as origin:
                client = BcastApiClient(origin, package_contract=contract)
                self.assertEqual(accepted.as_dict(), client.get_package(accepted.package_id))
                self.assertEqual(accepted.metadata(), client.get_package_metadata(accepted.package_id))
                root = accepted.roots()[0]["object_id"]
                self.assertEqual(accepted.children(root), client.get_children(accepted.package_id, root))
                with self.assertRaises(BcastApiProblem) as problem:
                    client.get_package(refused.package_id)
                self.assertEqual("incompatible_version", problem.exception.code)
                self.assertEqual(409, problem.exception.http_status)
                with self.assertRaises(BcastApiProblem) as metadata_problem:
                    client.get_package_metadata(refused.package_id)
                self.assertEqual("incompatible_version", metadata_problem.exception.code)

    def test_wrong_version_client_cannot_reinterpret_an_http_success(self):
        for server_contract, server_package, client_contract in [
            ("bcast.package/0.1.0", self.legacy, "bcast.package/0.2.0"),
            ("bcast.package/0.2.0", self.current, "bcast.package/0.1.0"),
        ]:
            with self.subTest(server_contract=server_contract), serve(server_contract, [server_package]) as origin:
                wrong = BcastApiClient(origin, package_contract=client_contract)
                with self.assertRaises(BcastApiProtocolError):
                    wrong.get_package(server_package.package_id)

    def test_fabricated_upgrade_or_downgrade_is_not_a_compatibility_path(self):
        old = self.legacy.as_dict()
        new = self.current.as_dict()

        invented_v02 = {
            **old,
            "schema_version": "bcast.package/0.2.0",
            "publication": {**old["publication"], "namespace": "codes.example"},
        }
        with self.assertRaises(PackageValidationError):
            validate_package(invented_v02)

        invented_v01 = {
            **new,
            "schema_version": "bcast.package/0.1.0",
            "publication": {k: v for k, v in new["publication"].items() if k != "namespace"},
        }
        with self.assertRaises(PackageValidationError):
            validate_package(invented_v01)


if __name__ == "__main__":
    unittest.main()
