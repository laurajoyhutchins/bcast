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


class BcastPackage:
    def __init__(self, data: Mapping[str, Any]):
        self._data = deepcopy(dict(data))
        self._objects = {item["object_id"]: item for item in self._data["objects"]}

    @classmethod
    def load(cls, path: str | Path) -> "BcastPackage":
        source = Path(path)
        with source.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return cls.from_mapping(data)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "BcastPackage":
        data = deepcopy(dict(value))
        validate_package(data)
        return cls(data)

    @classmethod
    def schema(cls) -> dict[str, Any]:
        return deepcopy(load_schema())

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
        return deepcopy({
            "schema_version": self._data["schema_version"],
            "package_id": self._data["package_id"],
            "package_version": self._data["package_version"],
            "publication": self._data["publication"],
        })

    def get_object(self, object_id: str) -> dict[str, Any]:
        record = self._objects.get(object_id)
        if record is None:
            raise ObjectNotFoundError(object_id)
        return deepcopy(record)

    def children(self, object_id: str) -> list[dict[str, Any]]:
        self.get_object(object_id)
        matches = [item for item in self._data["objects"] if item.get("parent_id") == object_id]
        return deepcopy(sorted(matches, key=lambda item: item["object_id"]))
