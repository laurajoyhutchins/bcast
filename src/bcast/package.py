from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Mapping

from .validation import load_schema, validate_package


class ObjectNotFoundError(LookupError):
    def __init__(self, object_id: str):
        self.object_id = object_id
        super().__init__(f"BCAST object not found: {object_id}")


class ObjectCoordinateNotFoundError(LookupError):
    def __init__(self, kind: str, locator: str):
        self.kind = kind
        self.locator = locator
        super().__init__(f"BCAST object not found: kind={kind} locator={locator}")


class BcastPackage:
    def __init__(self, data: Mapping[str, Any]):
        # Validate before constructing indexes, including for in-memory packages.
        self._data = deepcopy(dict(data))
        validate_package(self._data)
        self._objects = {item["object_id"]: item for item in self._data["objects"]}
        self._coordinates = {
            (item["kind"], item["locator"]): item for item in self._data["objects"]
        }
        self._children: dict[str, list[dict[str, Any]]] = {}
        self._roots: list[dict[str, Any]] = []
        for item in self._data["objects"]:
            parent_id = item.get("parent_id")
            if parent_id is None:
                self._roots.append(item)
            else:
                self._children.setdefault(parent_id, []).append(item)
        self._roots.sort(key=lambda item: item["object_id"])
        for records in self._children.values():
            records.sort(key=lambda item: item["object_id"])

    @classmethod
    def load(cls, path: str | Path) -> "BcastPackage":
        with Path(path).open("r", encoding="utf-8") as handle:
            return cls.from_mapping(json.load(handle))

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "BcastPackage":
        return cls(value)

    @classmethod
    def schema(cls, version: str = "bcast.package/0.1.0") -> dict[str, Any]:
        return deepcopy(load_schema(version))

    @property
    def schema_version(self) -> str:
        return self._data["schema_version"]

    @property
    def package_id(self) -> str:
        return self._data["package_id"]

    @property
    def package_version(self) -> str:
        return self._data["package_version"]

    def as_dict(self) -> dict[str, Any]:
        return deepcopy(self._data)

    def metadata(self) -> dict[str, Any]:
        return deepcopy(
            {
                "schema_version": self._data["schema_version"],
                "package_id": self._data["package_id"],
                "package_version": self._data["package_version"],
                "publication": self._data["publication"],
            }
        )

    def get_object(self, object_id: str) -> dict[str, Any]:
        record = self._objects.get(object_id)
        if record is None:
            raise ObjectNotFoundError(object_id)
        return deepcopy(record)

    def children(self, object_id: str) -> list[dict[str, Any]]:
        if object_id not in self._objects:
            raise ObjectNotFoundError(object_id)
        return deepcopy(self._children.get(object_id, []))

    def roots(self) -> list[dict[str, Any]]:
        return deepcopy(self._roots)

    def parent(self, object_id: str) -> dict[str, Any] | None:
        record = self._objects.get(object_id)
        if record is None:
            raise ObjectNotFoundError(object_id)
        parent_id = record.get("parent_id")
        return None if parent_id is None else deepcopy(self._objects[parent_id])

    def ancestors(self, object_id: str) -> list[dict[str, Any]]:
        if object_id not in self._objects:
            raise ObjectNotFoundError(object_id)
        chain: list[dict[str, Any]] = []
        parent_id = self._objects[object_id].get("parent_id")
        while parent_id is not None:
            record = self._objects[parent_id]
            chain.append(record)
            parent_id = record.get("parent_id")
        chain.reverse()
        return deepcopy(chain)

    def descendants(self, object_id: str) -> list[dict[str, Any]]:
        if object_id not in self._objects:
            raise ObjectNotFoundError(object_id)
        pending = list(self._children.get(object_id, []))
        found: list[dict[str, Any]] = []
        while pending:
            current = pending.pop()
            found.append(current)
            pending.extend(self._children.get(current["object_id"], []))
        return deepcopy(sorted(found, key=lambda item: item["object_id"]))

    def find(self, kind: str, locator: str) -> dict[str, Any]:
        record = self._coordinates.get((kind, locator))
        if record is None:
            raise ObjectCoordinateNotFoundError(kind, locator)
        return deepcopy(record)
