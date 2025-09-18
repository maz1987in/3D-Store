"""Public import for the OpenAPI builder.

Keeps a stable import path while the implementation lives in
`openapi_builder.py`.
"""
from .openapi_builder import build_openapi_spec  # noqa: F401

__all__ = ["build_openapi_spec"]
