from __future__ import annotations

import json
from importlib import resources
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from .identifiers import package_id, publication_id, regulatory_object_id


class PackageValidationError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = tuple(errors)
        super().__init__("; ".join(errors))


def load_schema() -> dict[str, Any]:
    text = resources.files("bcast").joinpath("schemas/package-0.1.0.schema.json").read_text(encoding="utf-8")
    return json.loads(text)


def _schema_errors(package: Any) -> list[str]:
    validator = Draft202012Validator(load_schema())
    errors = []
    for failure in sorted(validator.iter_errors(package), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in failure.absolute_path) or "<root>"
        errors.append(f"schema {location}: {failure.message}")
    return errors


def _semantic_errors(package: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    publication = package["publication"]
    expected_publication_id = publication_id(
        publication["family"],
        publication["edition"],
        publication.get("revision"),
    )
    if publication["publication_id"] != expected_publication_id:
        failures.append("publication_id does not match canonical provider-neutral identity")

    expected_package_id = package_id(publication["publication_id"], package["package_version"])
    if package["package_id"] != expected_package_id:
        failures.append("package_id does not match canonical package identity")

    ids: set[str] = set()
    coordinates: set[tuple[str, str]] = set()
    by_id: dict[str, Mapping[str, Any]] = {}
    for index, item in enumerate(package["objects"]):
        expected_object_id = regulatory_object_id(
            publication["publication_id"],
            item["kind"],
            item["locator"],
        )
        if item["object_id"] != expected_object_id:
            failures.append(f"objects[{index}].object_id does not match canonical object identity")
        object_id = item["object_id"]
        if object_id in ids:
            failures.append(f"duplicate object_id: {object_id}")
        ids.add(object_id)
        by_id[object_id] = item
        coordinate = (item["kind"], item["locator"])
        if coordinate in coordinates:
            failures.append(f"duplicate object coordinate: kind={item['kind']} locator={item['locator']}")
        coordinates.add(coordinate)

    for item in package["objects"]:
        parent_id = item.get("parent_id")
        if parent_id is None:
            continue
        if parent_id == item["object_id"]:
            failures.append(f"object cannot parent itself: {item['object_id']}")
        elif parent_id not in by_id:
            failures.append(f"missing parent object: {parent_id}")

    for item in package["objects"]:
        seen: set[str] = set()
        cursor = item
        while "parent_id" in cursor:
            parent_id = cursor["parent_id"]
            if parent_id in seen:
                failures.append(f"structural parent cycle reaches {parent_id}")
                break
            seen.add(parent_id)
            parent = by_id.get(parent_id)
            if parent is None:
                break
            cursor = parent
    return failures


def validate_package(package: Any) -> None:
    failures = _schema_errors(package)
    if not failures:
        failures.extend(_semantic_errors(package))
    if failures:
        raise PackageValidationError(failures)
