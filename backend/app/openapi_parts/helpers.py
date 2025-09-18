"""Helper functions for the OpenAPI builder.

These are deliberately tiny to avoid changing output ordering or semantics.
"""
from typing import Any, Dict


def schema_minimal(name: str) -> Dict[str, Any]:
    return {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}


def caching_headers() -> Dict[str, Any]:
    return {
        "ETag": {"schema": {"type": "string"}},
        "Last-Modified": {"schema": {"type": "string"}},
        "X-Last-Modified-ISO": {"schema": {"type": "string"}},
    }


__all__ = ["schema_minimal", "caching_headers"]
