"""Backward-compatible shim for the OpenAPI builder.

This module re-exports the canonical builder from `openapi_builder.py` and
also exposes constants for legacy imports used in tests.
"""

from .openapi_builder import build_openapi_spec  # noqa: F401
from .openapi_parts.constants import (  # noqa: F401
    ACTION_REGISTRY,
    ENTITIES,
    SERVICE_CODE,
    SORT_PARAM_MAP,
    SORT_DETAILS,
)

__all__ = [
    "build_openapi_spec",
    "ACTION_REGISTRY",
    "ENTITIES",
    "SERVICE_CODE",
    "SORT_PARAM_MAP",
    "SORT_DETAILS",
]
