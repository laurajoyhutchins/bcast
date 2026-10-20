from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from jsonschema import Draft202012Validator

from .identifiers import package_id as canonical_package_id, publication_id
from .validation import PackageValidationError, load_schema, validate_package


PROBLEM_HTTP_STATUS = {
    "not_found": 404,
    "unresolved": 409,
    "unsupported": 422,
    "incompatible_version": 409,
}


class BcastApiError(RuntimeError):
    pass


class BcastApiProtocolError(BcastApiError):
    def __init__(self, message: str, http_status: int | None = None):
        self.http_status = http_status
        super().__init__(message)


class BcastApiProblem(BcastApiError):
    def __init__(self, code: str, message: str, http_status: int, resource_id: str | None = None):
        self.code = code
        self.message = message
        self.http_status = http_status
        self.resource_id = resource_id
        super().__init__(f"{code}: {message}")


def _require_public_shape(value: Any, schema: dict[str, Any], label: str) -> None:
    # Public schema conformance is an API integrity boundary, not evidence of
    # substantive regulatory correctness.
    if next(Draft202012Validator(schema).iter_errors(value), None) is not None:
        raise BcastApiProtocolError(f"{label} violates the public BCAST contract")


def _metadata_schema() -> dict[str, Any]:
    package_properties = load_schema()["properties"]
    fields = ("schema_version", "package_id", "package_version", "publication")
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(fields),
        "properties": {field: package_properties[field] for field in fields},
    }


def _object_schema() -> dict[str, Any]:
    return load_schema()["properties"]["objects"]["items"]


class BcastApiClient:
    def __init__(self, base_url: str, *, timeout: float = 10.0):
        base = base_url.strip().rstrip("/")
        if not base:
            raise ValueError("base_url must not be empty")
        self.base_url = base
        self.timeout = timeout

    @staticmethod
    def _segment(value: str) -> str:
        return quote(value, safe="")

    def _get_json(self, path: str) -> Any:
        request = Request(f"{self.base_url}{path}", headers={"Accept": "application/json"}, method="GET")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                content_type = response.headers.get_content_type()
                if content_type != "application/json":
                    raise BcastApiProtocolError(f"expected application/json, got {content_type}", response.status)
                try:
                    return json.loads(response.read().decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise BcastApiProtocolError("BCAST API returned invalid JSON", response.status) from exc
        except HTTPError as exc:
            body = exc.read()
            try:
                problem = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise BcastApiProtocolError("BCAST API returned a non-JSON error", exc.code) from exc
            if not isinstance(problem, dict) or not isinstance(problem.get("code"), str) or not isinstance(problem.get("message"), str):
                raise BcastApiProtocolError("BCAST API returned an invalid problem object", exc.code) from exc
            code = problem["code"]
            expected_status = PROBLEM_HTTP_STATUS.get(code)
            if expected_status is None or expected_status != exc.code:
                raise BcastApiProtocolError("BCAST API returned inconsistent problem semantics", exc.code) from exc
            raise BcastApiProblem(
                code,
                problem["message"],
                exc.code,
                problem.get("resource_id") if isinstance(problem.get("resource_id"), str) else None,
            ) from exc

    def get_package_metadata(self, package_id: str) -> dict[str, Any]:
        value = self._get_json(f"/packages/{self._segment(package_id)}/metadata")
        _require_public_shape(value, _metadata_schema(), "package metadata response")
        if value["package_id"] != package_id:
            raise BcastApiProtocolError("package metadata response identity differs from requested package")
        publication = value["publication"]
        expected_publication_id = publication_id(
            publication["family"], publication["edition"], publication.get("revision")
        )
        if publication["publication_id"] != expected_publication_id:
            raise BcastApiProtocolError("package metadata response has inconsistent publication identity")
        if value["package_id"] != canonical_package_id(publication["publication_id"], value["package_version"]):
            raise BcastApiProtocolError("package metadata response has inconsistent package identity")
        return value

    def get_package(self, package_id: str) -> dict[str, Any]:
        value = self._get_json(f"/packages/{self._segment(package_id)}")
        try:
            validate_package(value)
        except PackageValidationError as exc:
            raise BcastApiProtocolError("package response violates the public BCAST contract") from exc
        if value["package_id"] != package_id:
            raise BcastApiProtocolError("package response identity differs from requested package")
        return value

    def get_object(self, package_id: str, object_id: str) -> dict[str, Any]:
        value = self._get_json(
            f"/packages/{self._segment(package_id)}/objects/{self._segment(object_id)}"
        )
        _require_public_shape(value, _object_schema(), "object response")
        if value["object_id"] != object_id:
            raise BcastApiProtocolError("object response identity differs from requested object")
        return value

    def get_children(self, package_id: str, object_id: str) -> list[dict[str, Any]]:
        value = self._get_json(
            f"/packages/{self._segment(package_id)}/objects/{self._segment(object_id)}/children"
        )
        if not isinstance(value, list):
            raise BcastApiProtocolError("children response must be an array of objects")
        child_schema = _object_schema()
        ids: list[str] = []
        for child in value:
            _require_public_shape(child, child_schema, "child response")
            if child.get("parent_id") != object_id:
                raise BcastApiProtocolError("child response parent differs from requested object")
            ids.append(child["object_id"])
        if ids != sorted(set(ids)):
            raise BcastApiProtocolError("children response identities must be unique and sorted")
        return value
