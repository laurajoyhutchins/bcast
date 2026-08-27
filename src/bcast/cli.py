from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .api import BcastApiClient, BcastApiError
from .package import BcastPackage, ObjectCoordinateNotFoundError, ObjectNotFoundError
from .server import serve_paths
from .validation import PackageValidationError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bcast", description="Read and validate public BCAST packages.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate a local BCAST package")
    validate.add_argument("package")

    get = subparsers.add_parser("get", help="Retrieve one canonical object record")
    get.add_argument("package")
    get.add_argument("object_id")

    children = subparsers.add_parser("children", help="List direct structural children")
    children.add_argument("package")
    children.add_argument("object_id")

    tree = subparsers.add_parser("tree", help="Print the local public structural tree")
    tree.add_argument("package")

    serve = subparsers.add_parser("serve", help="Serve validated local packages through bcast.api/0.1.0")
    serve.add_argument("packages", nargs="+")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)

    api = subparsers.add_parser("api", help="Call a bcast.api/0.1.0 endpoint")
    api.add_argument("base_url")
    api_subparsers = api.add_subparsers(dest="api_command", required=True)

    metadata = api_subparsers.add_parser("metadata", help="Retrieve package metadata")
    metadata.add_argument("package_id")

    package = api_subparsers.add_parser("package", help="Retrieve a complete package")
    package.add_argument("package_id")

    api_get = api_subparsers.add_parser("get", help="Retrieve one canonical object record")
    api_get.add_argument("package_id")
    api_get.add_argument("object_id")

    api_children = api_subparsers.add_parser("children", help="List direct structural children")
    api_children.add_argument("package_id")
    api_children.add_argument("object_id")
    return parser


def _print_json(value) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def _print_tree(package: BcastPackage) -> None:
    def visit(record, depth: int) -> None:
        label = record.get("label")
        suffix = f" {label}" if label else ""
        print(f"{'  ' * depth}{record['kind']} {record['locator']}{suffix}")
        for child in package.children(record["object_id"]):
            visit(child, depth + 1)

    for root in package.roots():
        visit(root, 0)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "serve":
            serve_paths(args.packages, host=args.host, port=args.port)
            return 0
        if args.command == "api":
            client = BcastApiClient(args.base_url)
            if args.api_command == "metadata":
                _print_json(client.get_package_metadata(args.package_id))
            elif args.api_command == "package":
                _print_json(client.get_package(args.package_id))
            elif args.api_command == "get":
                _print_json(client.get_object(args.package_id, args.object_id))
            elif args.api_command == "children":
                _print_json(client.get_children(args.package_id, args.object_id))
            return 0

        package = BcastPackage.load(args.package)
        if args.command == "validate":
            print(f"OK {args.package}")
        elif args.command == "get":
            _print_json(package.get_object(args.object_id))
        elif args.command == "children":
            _print_json(package.children(args.object_id))
        elif args.command == "tree":
            _print_tree(package)
        return 0
    except (PackageValidationError, ObjectNotFoundError, ObjectCoordinateNotFoundError, BcastApiError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
