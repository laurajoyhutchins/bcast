#!/usr/bin/env python3
"""Validate public package fixtures using the same rules as the installed client."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator

from bcast.validation import PackageValidationError, load_schema, validate_package


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("schema", type=Path)
    parser.add_argument("packages", nargs="+", type=Path)
    args = parser.parse_args()

    try:
        supplied_schema = load_json(args.schema)
        Draft202012Validator.check_schema(supplied_schema)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR {args.schema}: {exc}", file=sys.stderr)
        return 1

    version = supplied_schema.get("properties", {}).get("schema_version", {}).get("const")
    try:
        packaged_schema = load_schema(version)
    except ValueError as exc:
        print(f"ERROR {args.schema}: {exc}", file=sys.stderr)
        return 1
    if supplied_schema != packaged_schema:
        print(f"ERROR {args.schema}: schema differs from the packaged client schema", file=sys.stderr)
        return 1

    failed = False
    for path in args.packages:
        try:
            value = load_json(path)
            validate_package(value)
            if value["schema_version"] != version:
                raise PackageValidationError(["package contract differs from supplied schema"])
        except (OSError, json.JSONDecodeError, PackageValidationError) as exc:
            failed = True
            print(f"ERROR {path}: {exc}", file=sys.stderr)
        else:
            print(f"OK {path}")

    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
