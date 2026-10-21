"""Deterministic BCAST 0.2 package construction from provider-neutral records.

Source acquisition, interpretation, rights and provenance review happen before
this boundary. Neither source bytes nor provider SDKs are required here.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from copy import deepcopy
from typing import Any

from .identifiers import materialized_package_id, publication_id_v2, regulatory_object_id
from .validation import PackageValidationError, validate_package

_OBJECT_FIELDS = frozenset({"kind", "locator", "status", "parent", "label", "content", "provenance"})
_PARENT_FIELDS = frozenset({"kind", "locator"})


def compile_package(
    *,
    namespace: str,
    family: str,
    edition: str,
    package_version: str,
    objects: Iterable[Mapping[str, Any]],
    revision: str | None = None,
    title: str | None = None,
    issuing_body: str | None = None,
) -> dict[str, Any]:
    """Materialize and validate a canonical BCAST 0.2 package.

    Inputs are normalized publication coordinates and objects. Each optional
    parent is a {"kind": ..., "locator": ...} coordinate; callers
    cannot supply precomputed IDs or bypass the public package validator.
    Input mappings are not modified. This function makes no assertion about
    source authenticity, rights, jurisdictional applicability or fidelity.
    """
    publication: dict[str, Any] = {
        "publication_id": publication_id_v2(namespace, family, edition, revision),
        "namespace": namespace,
        "family": family,
        "edition": edition,
    }
    if revision is not None:
        publication["revision"] = revision
    if title is not None:
        publication["title"] = title
    if issuing_body is not None:
        publication["issuing_body"] = issuing_body

    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(objects):
        if not isinstance(item, Mapping):
            raise PackageValidationError([f"objects[{index}] must be a mapping"])
        invalid = set(item) - _OBJECT_FIELDS
        if invalid:
            raise PackageValidationError([f"objects[{index}] has unsupported input fields: {sorted(invalid)}"])
        missing = {"kind", "locator", "status"} - item.keys()
        if missing:
            raise PackageValidationError([f"objects[{index}] lacks required coordinates or status: {sorted(missing)}"])
        record = deepcopy(dict(item))
        parent = record.pop("parent", None)
        kind, locator = record["kind"], record["locator"]
        if not isinstance(kind, str) or not isinstance(locator, str):
            raise PackageValidationError([f"objects[{index}] kind and locator must be strings"])
        record["object_id"] = regulatory_object_id(publication["publication_id"], kind, locator)
        if parent is not None:
            if (not isinstance(parent, Mapping) or set(parent) != _PARENT_FIELDS
                    or not isinstance(parent["kind"], str) or not isinstance(parent["locator"], str)):
                raise PackageValidationError([f"objects[{index}].parent must contain only kind and locator strings"])
            record["parent_id"] = regulatory_object_id(
                publication["publication_id"], parent["kind"], parent["locator"]
            )
        normalized.append(record)

    package = {
        "schema_version": "bcast.package/0.2.0",
        "package_version": package_version,
        "publication": publication,
        "objects": sorted(normalized, key=lambda item: item["object_id"]),
    }
    package["package_id"] = materialized_package_id(package)
    validate_package(package)
    return package
