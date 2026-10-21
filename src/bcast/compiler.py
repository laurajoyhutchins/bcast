"""Provider-neutral BCAST package materialization.

Inputs are already normalized publication metadata and object coordinates.
This module does not fetch, interpret, license, or certify regulatory sources.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping

from .identifiers import materialized_package_id, publication_id_v2, regulatory_object_id
from .validation import validate_package


def build_package_v2(
    *,
    publication: Mapping[str, Any],
    package_version: str,
    objects: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a validated, content-addressed bcast.package/0.2.0 package.

    Each input object has `kind` and `locator`, and optionally `parent` as
    `{"kind": ..., "locator": ...}`. Identifiers are derived here, never
    provided by source adapters. Remaining fields must satisfy the normative
    package schema. The caller remains responsible for source fidelity,
    lawful acquisition, source-to-record mapping, and rights decisions.
    """
    if not isinstance(publication, Mapping) or "publication_id" in publication:
        raise ValueError("publication must be metadata without a derived publication_id")
    metadata = deepcopy(dict(publication))
    for field in ("namespace", "family", "edition"):
        if not isinstance(metadata.get(field), str):
            raise ValueError(f"publication.{field} must be a string")
    publication_id = publication_id_v2(
        metadata["namespace"], metadata["family"], metadata["edition"], metadata.get("revision")
    )
    records: list[dict[str, Any]] = []
    for draft in objects:
        if not isinstance(draft, Mapping):
            raise ValueError("normalized objects must be mappings")
        if "object_id" in draft or "parent_id" in draft:
            raise ValueError("normalized input must not supply derived object_id or parent_id")
        kind, locator = draft.get("kind"), draft.get("locator")
        if not isinstance(kind, str) or not isinstance(locator, str):
            raise ValueError("object kind and locator must be strings")
        record: dict[str, Any] = {
            "object_id": regulatory_object_id(publication_id, kind, locator),
            "kind": kind,
            "locator": locator,
        }
        if "parent" in draft:
            parent = draft["parent"]
            if (
                not isinstance(parent, Mapping)
                or set(parent) != {"kind", "locator"}
                or not isinstance(parent["kind"], str)
                or not isinstance(parent["locator"], str)
            ):
                raise ValueError("parent must identify exactly one (kind, locator) coordinate")
            record["parent_id"] = regulatory_object_id(
                publication_id, parent["kind"], parent["locator"]
            )
        for key, value in draft.items():
            if key not in {"kind", "locator", "parent"}:
                record[key] = deepcopy(value)
        records.append(record)

    package = {
        "schema_version": "bcast.package/0.2.0",
        "package_version": package_version,
        "publication": {"publication_id": publication_id, **metadata},
        "objects": sorted(records, key=lambda item: item["object_id"]),
    }
    package["package_id"] = materialized_package_id(package)
    validate_package(package)
    return package
