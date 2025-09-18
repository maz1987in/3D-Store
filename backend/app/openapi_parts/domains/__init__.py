"""Per-service OpenAPI path builders.

Each module exports `build_paths(schema_name, coll, id_param)` and delegates to
the common base to preserve consistent behavior and ordering.
"""

__all__ = [
    "inventory",
    "sales",
    "print",
    "accounting",
    "catalog",
    "po",
    "repairs",
]
