"""Shim module re-exporting clean OpenAPI builder.
Temporary while replacing corrupted previous implementation.
"""
from .openapi_clean import build_openapi_spec  # noqa: F401

__all__ = ["build_openapi_spec"]
