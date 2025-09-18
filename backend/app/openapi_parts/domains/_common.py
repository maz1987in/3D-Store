"""Common helper for building service paths with deterministic structure."""
from typing import Any, Dict, List
from ..constants import ACTION_REGISTRY, SORT_PARAM_MAP
from ..helpers import caching_headers


def build_service_paths(schema_name: str, domain: str, coll: str, id_param: str) -> Dict[str, Any]:
    paths: Dict[str, Any] = {}
    list_path = f"/{domain}/{coll}"
    single_path = f"{list_path}/{{{id_param}}}"

    # List endpoint
    paths[list_path] = {
        "get": {
            "summary": f"List {coll.replace('-', ' ')}",
            "parameters": [
                {"$ref": "#/components/parameters/LimitParam"},
                {"$ref": "#/components/parameters/OffsetParam"},
                {"$ref": f"#/components/parameters/{SORT_PARAM_MAP[schema_name]}"},
            ],
            "responses": {
                "200": {
                    "description": "OK",
                    "headers": caching_headers(),
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "data": {"type": "array", "items": {"$ref": f"#/components/schemas/{schema_name}"}},
                                    "pagination": {"$ref": "#/components/schemas/Pagination"},
                                },
                            }
                        }
                    },
                },
                "304": {"description": "Not Modified"},
                "400": {"$ref": "#/components/responses/BadRequest"},
            },
        },
        "head": {
            "summary": f"{schema_name} list validators",
            "responses": {
                "200": {"description": "Headers only", "headers": caching_headers()},
                "304": {"description": "Not Modified"},
            },
        },
    }

    # Single resource
    readable = schema_name.lower().replace("transaction", " transaction").replace("purchaseorder", "purchase order")
    paths[single_path] = {
        "get": {
            "summary": f"Get {readable}",
            "parameters": [{"name": id_param, "in": "path", "required": True, "schema": {"type": "integer"}}],
            "responses": {
                "200": {
                    "description": "OK",
                    "headers": caching_headers(),
                    "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{schema_name}"}}},
                },
                "304": {"description": "Not Modified"},
                "404": {"$ref": "#/components/responses/NotFound"},
            },
        },
        "head": {
            "summary": f"{schema_name} validators",
            "parameters": [{"name": id_param, "in": "path", "required": True, "schema": {"type": "integer"}}],
            "responses": {
                "200": {"description": "Headers only", "headers": caching_headers()},
                "304": {"description": "Not Modified"},
                "404": {"$ref": "#/components/responses/NotFound"},
            },
        },
    }

    # Action endpoints (POST)
    actions: List[Dict[str, str]] = ACTION_REGISTRY.get(schema_name, [])
    if actions:
        action_common_params = [{"name": id_param, "in": "path", "required": True, "schema": {"type": "integer"}}]
        for spec in actions:
            act_path = f"{single_path}/{spec['action']}"
            paths[act_path] = {
                "post": {
                    "summary": spec["summary"],
                    "parameters": action_common_params,
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{schema_name}"}}},
                        },
                        "400": {"$ref": "#/components/responses/BadRequest"},
                        "404": {"$ref": "#/components/responses/NotFound"},
                    },
                    "x-required-permissions": [spec["permission"]],
                }
            }

    return paths

__all__ = ["build_service_paths"]
