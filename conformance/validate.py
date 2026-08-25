#!/usr/bin/env python3
"""Validate BCAST public package contracts without invoking compiler machinery."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def stable_id(prefix: str, payload: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return f"{prefix}:sha256:{digest}"


def error(path: Path, message: str) -> str:
    return f"{path}: {message}"


def validate_semantics(path: Path, package: dict[str, Any]) -> list[str]:
    failures: list[str] = []

    publication = package["publication"]
    publication_identity = {
        "family": publication["family"],
        "edition": publication["edition"],
    }
    if "revision" in publication:
        publication_identity["revision"] = publication["revision"]
    expected_publication_id = stable_id("bcastpub", publication_identity)
    if publication["publication_id"] != expected_publication_id:
        failures.append(
            error(
                path,
                "publication_id does not match canonical provider-neutral identity",
            )
        )

    expected_package_id = stable_id(
        "bcastpkg",
        {
            "publication_id": publication["publication_id"],
            "package_version": package["package_version"],
        },
    )
    if package["package_id"] != expected_package_id:
        failures.append(error(path, "package_id does not match canonical package identity"))

    objects = package["objects"]
    ids: set[str] = set()
    coordinates: set[tuple[str, str]] = set()
    by_id: dict[str, dict[str, Any]] = {}

    for index, item in enumerate(objects):
        expected_object_id = stable_id(
            "bcastobj",
            {
                "publication_id": publication["publication_id"],
                "kind": item["kind"],
                "locator": item["locator"],
            },
        )
        if item["object_id"] != expected_object_id:
            failures.append(
                error(
                    path,
                    f"objects[{index}].object_id does not match canonical object identity",
                )
            )

        object_id = item["object_id"]
        if object_id in ids:
            failures.append(error(path, f"duplicate object_id: {object_id}"))
        ids.add(object_id)
        by_id[object_id] = item

        coordinate = (item["kind"], item["locator"])
        if coordinate in coordinates:
            failures.append(
                error(
                    path,
                    f"duplicate object coordinate: kind={item['kind']} locator={item['locator']}",
                )
            )
        coordinates.add(coordinate)

    for item in objects:
        parent_id = item.get("parent_id")
        if parent_id is None:
            continue
        if parent_id == item["object_id"]:
            failures.append(error(path, f"object cannot parent itself: {item['object_id']}"))
        elif parent_id not in by_id:
            failures.append(error(path, f"missing parent object: {parent_id}"))

    for item in objects:
        seen: set[str] = set()
        cursor = item
        while "parent_id" in cursor:
            parent_id = cursor["parent_id"]
            if parent_id in seen:
                failures.append(
                    error(path, f"structural parent cycle reaches {parent_id}")
                )
                break
            seen.add(parent_id)
            parent = by_id.get(parent_id)
            if parent is None:
                break
            cursor = parent

    return failures


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("schema", type=Path)
    parser.add_argument("packages", nargs="+", type=Path)
    args = parser.parse_args()

    schema = load_json(args.schema)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    failed = False
    for package_path in args.packages:
        package = load_json(package_path)
        failures: list[str] = []

        for validation_error in sorted(
            validator.iter_errors(package),
            key=lambda item: list(item.absolute_path),
        ):
            location = ".".join(str(part) for part in validation_error.absolute_path)
            failures.append(
                error(
                    package_path,
                    f"schema {location or '<root>'}: {validation_error.message}",
                )
            )

        if not failures:
            failures.extend(validate_semantics(package_path, package))

        if failures:
            failed = True
            for failure in failures:
                print(f"ERROR {failure}", file=sys.stderr)
        else:
            print(f"OK {package_path}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
