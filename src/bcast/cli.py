from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .package import BcastPackage, ObjectNotFoundError
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
    return parser


def _print_json(value) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        package = BcastPackage.load(args.package)
        if args.command == "validate":
            print(f"OK {args.package}")
        elif args.command == "get":
            _print_json(package.get_object(args.object_id))
        elif args.command == "children":
            _print_json(package.children(args.object_id))
        return 0
    except (PackageValidationError, ObjectNotFoundError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
