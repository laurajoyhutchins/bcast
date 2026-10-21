from __future__ import annotations

import json
import unicodedata
from importlib import resources
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from .identifiers import (
    materialized_package_id,
    package_id,
    publication_id,
    publication_id_v2,
    regulatory_object_id,
)


class PackageValidationError(ValueError):
    def __init__(self, errors: list[str]):
        self.errors = tuple(errors)
        super().__init__("; ".join(errors))


PACKAGE_CONTRACTS = ("bcast.package/0.1.0", "bcast.package/0.2.0")


def load_schema(version: str = "bcast.package/0.1.0") -> dict[str, Any]:
    if version not in PACKAGE_CONTRACTS:
        raise ValueError(f"unsupported BCAST package contract: {version}")
    filename = f"schemas/package-{version.removeprefix('bcast.package/')}.schema.json"
    return json.loads(resources.files("bcast").joinpath(filename).read_text(encoding="utf-8"))


def _schema_errors(package: Any, version: str) -> list[str]:
    validator = Draft202012Validator(load_schema(version))
    errors = []
    for failure in sorted(
        validator.iter_errors(package), key=lambda item: list(item.absolute_path)
    ):
        location = ".".join(str(part) for part in failure.absolute_path) or "<root>"
        errors.append(f"schema {location}: {failure.message}")
    return errors


def _semantic_errors(package: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    publication = package["publication"]
    version = package["schema_version"]
    if version == "bcast.package/0.2.0":
        expected_publication_id = publication_id_v2(
            publication["namespace"],
            publication["family"],
            publication["edition"],
            publication.get("revision"),
        )
        for field in ("edition", "revision"):
            value = publication.get(field)
            if value is not None and (
                value != value.strip() or unicodedata.normalize("NFC", value) != value
            ):
                failures.append(f"publication.{field} must be trimmed NFC Unicode")
    else:
        expected_publication_id = publication_id(
            publication["family"], publication["edition"], publication.get("revision")
        )
    if publication["publication_id"] != expected_publication_id:
        failures.append("publication_id does not match canonical provider-neutral identity")

    expected_package_id = (
        materialized_package_id(package)
        if version == "bcast.package/0.2.0"
        else package_id(publication["publication_id"], package["package_version"])
    )
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
            failures.append(
                f"duplicate object coordinate: kind={item['kind']} locator={item['locator']}"
            )
        coordinates.add(coordinate)

    for item in package["objects"]:
        parent_id = item.get("parent_id")
        if parent_id is None:
            continue
        if parent_id == item["object_id"]:
            failures.append(f"object cannot parent itself: {item['object_id']}")
        elif parent_id not in by_id:
            failures.append(f"missing parent object: {parent_id}")

    # Walk each parent chain once. The previous per-object traversal was
    # quadratic for deep publications, even when every parent was valid.
    visited: set[str] = set()
    for start in by_id:
        if start in visited:
            continue
        chain: set[str] = set()
        cursor: str | None = start
        while cursor is not None and cursor in by_id and cursor not in visited:
            if cursor in chain:
                failures.append(f"structural parent cycle reaches {cursor}")
                break
            chain.add(cursor)
            parent_id = by_id[cursor].get("parent_id")
            if parent_id == cursor:
                break  # Already reported as an immediate self-parent.
            cursor = parent_id
        visited.update(chain)
    return failures


def validate_package(package: Any) -> None:
    version = package.get("schema_version") if isinstance(package, Mapping) else None
    if version not in PACKAGE_CONTRACTS:
        raise PackageValidationError([f"unsupported BCAST schema_version: {version!r}"])
    failures = _schema_errors(package, version)
    if not failures:
        failures.extend(_semantic_errors(package))
    if failures:
        raise PackageValidationError(failures)
