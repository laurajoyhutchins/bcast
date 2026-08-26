from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .validation import validate_package


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
                return json.loads(response.read().decode("utf-8"))
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
        if not isinstance(value, dict):
            raise BcastApiProtocolError("package metadata response must be an object")
        return value

    def get_package(self, package_id: str) -> dict[str, Any]:
        value = self._get_json(f"/packages/{self._segment(package_id)}")
        if not isinstance(value, dict):
            raise BcastApiProtocolError("package response must be an object")
        validate_package(value)
        return value

    def get_object(self, package_id: str, object_id: str) -> dict[str, Any]:
        value = self._get_json(
            f"/packages/{self._segment(package_id)}/objects/{self._segment(object_id)}"
        )
        if not isinstance(value, dict):
            raise BcastApiProtocolError("object response must be an object")
        return value

    def get_children(self, package_id: str, object_id: str) -> list[dict[str, Any]]:
        value = self._get_json(
            f"/packages/{self._segment(package_id)}/objects/{self._segment(object_id)}/children"
        )
        if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
            raise BcastApiProtocolError("children response must be an array of objects")
        return value
