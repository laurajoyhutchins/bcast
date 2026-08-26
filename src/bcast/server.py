from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlsplit

from .package import BcastPackage, ObjectNotFoundError


class BcastPackageStore:
    def __init__(self, packages: Iterable[BcastPackage]):
        self._packages: dict[str, BcastPackage] = {}
        for package in packages:
            if package.package_id in self._packages:
                raise ValueError(f"duplicate package_id: {package.package_id}")
            self._packages[package.package_id] = package

    @classmethod
    def from_paths(cls, paths: Iterable[str | Path]) -> "BcastPackageStore":
        return cls(BcastPackage.load(path) for path in paths)

    def get(self, package_id: str) -> BcastPackage:
        try:
            return self._packages[package_id]
        except KeyError as exc:
            raise KeyError(package_id) from exc


def _handler_for(store: BcastPackageStore):
    class Handler(BaseHTTPRequestHandler):
        server_version = "BCASTReference/0.1"

        def log_message(self, format: str, *args) -> None:
            return

        def _json(self, status: int, payload) -> None:
            body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _problem(self, status: int, code: str, message: str, resource_id: str | None = None) -> None:
            payload = {"code": code, "message": message}
            if resource_id is not None:
                payload["resource_id"] = resource_id
            self._json(status, payload)

        def do_GET(self) -> None:
            segments = [unquote(part) for part in urlsplit(self.path).path.split("/") if part]
            if not segments or segments[0] != "packages":
                self._problem(404, "not_found", "BCAST resource not found")
                return
            if len(segments) < 2:
                self._problem(404, "not_found", "BCAST resource not found")
                return
            package_id = segments[1]
            try:
                package = store.get(package_id)
            except KeyError:
                self._problem(404, "not_found", "BCAST package not found", package_id)
                return

            if len(segments) == 2:
                self._json(200, package.as_dict())
                return
            if len(segments) == 3 and segments[2] == "metadata":
                self._json(200, package.metadata())
                return
            if len(segments) >= 4 and segments[2] == "objects":
                object_id = segments[3]
                try:
                    if len(segments) == 4:
                        self._json(200, package.get_object(object_id))
                        return
                    if len(segments) == 5 and segments[4] == "children":
                        self._json(200, package.children(object_id))
                        return
                except ObjectNotFoundError:
                    self._problem(404, "not_found", "BCAST object not found", object_id)
                    return
            self._problem(404, "not_found", "BCAST resource not found")

    return Handler


def make_server(
    packages: Iterable[BcastPackage] | BcastPackageStore,
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> ThreadingHTTPServer:
    store = packages if isinstance(packages, BcastPackageStore) else BcastPackageStore(packages)
    return ThreadingHTTPServer((host, port), _handler_for(store))


def serve_paths(paths: Iterable[str | Path], *, host: str = "127.0.0.1", port: int = 8000) -> None:
    store = BcastPackageStore.from_paths(paths)
    server = make_server(store, host=host, port=port)
    try:
        server.serve_forever()
    finally:
        server.server_close()
