from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json(dict(payload)).encode("utf-8")).hexdigest()
    return f"{prefix}:sha256:{digest}"


def publication_id(family: str, edition: str, revision: str | None = None) -> str:
    identity = {"edition": edition, "family": family}
    if revision is not None:
        identity["revision"] = revision
    return stable_id("bcastpub", identity)


def regulatory_object_id(publication_id: str, kind: str, locator: str) -> str:
    return stable_id(
        "bcastobj",
        {"kind": kind, "locator": locator, "publication_id": publication_id},
    )


def package_id(publication_id: str, package_version: str) -> str:
    return stable_id(
        "bcastpkg",
        {"package_version": package_version, "publication_id": publication_id},
    )


def publication_id_v2(
    namespace: str, family: str, edition: str, revision: str | None = None
) -> str:
    """Identity under the issuing authority's stable namespace, never a provider ID."""
    identity = {"namespace": namespace, "family": family, "edition": edition}
    if revision is not None:
        identity["revision"] = revision
    return stable_id("bcastpub", identity)


def materialized_package_id(package: Mapping[str, Any]) -> str:
    """Address the complete public package, ignoring only object enumeration order."""
    body = {key: value for key, value in package.items() if key != "package_id"}
    body["objects"] = sorted(package["objects"], key=lambda item: item["object_id"])
    return stable_id("bcastpkg", body)
