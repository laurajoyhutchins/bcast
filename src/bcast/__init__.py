"""Thin public consumer client for BCAST package and API contracts."""

from .api import BcastApiClient, BcastApiError, BcastApiProblem, BcastApiProtocolError
from .identifiers import materialized_package_id, package_id, publication_id, publication_id_v2, regulatory_object_id
from .package import BcastPackage, ObjectCoordinateNotFoundError, ObjectNotFoundError
from .validation import PackageValidationError, validate_package

__all__ = [
    "BcastApiClient",
    "BcastApiError",
    "BcastApiProblem",
    "BcastApiProtocolError",
    "BcastPackage",
    "ObjectNotFoundError",
    "ObjectCoordinateNotFoundError",
    "PackageValidationError",
    "package_id",
    "materialized_package_id",
    "publication_id_v2",
    "publication_id",
    "regulatory_object_id",
    "validate_package",
]
