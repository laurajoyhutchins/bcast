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
