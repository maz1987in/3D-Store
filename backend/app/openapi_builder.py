"""Clean minimal deterministic OpenAPI spec builder.

Scope (purposefully narrow):
- Auth endpoints: /iam/auth/login (POST), /iam/auth/me (GET)
- For each tracked entity: list + single GET & HEAD with caching headers
- Reusable params: limit, offset, per-entity sort

This is the canonical builder module; `app/openapi.py` re-exports from here.
"""
from typing import Any, Dict
from .openapi_parts.constants import (
    ENTITIES,
    ACTION_REGISTRY,
    SERVICE_CODE,
    SORT_PARAM_MAP,
    SORT_DETAILS,
)
from .openapi_parts.helpers import schema_minimal, caching_headers
from .openapi_parts.domains import (
    inventory as inv_dom,
    sales as sales_dom,
    print as print_dom,
    accounting as acc_dom,
    catalog as cat_dom,
    po as po_dom,
    repairs as rpr_dom,
)
from .openapi_parts.domains._common import build_service_paths

__all__ = ["build_openapi_spec"]


def _schema(name: str) -> Dict[str, Any]:
    return schema_minimal(name)


def _headers() -> Dict[str, Any]:
    return caching_headers()


def build_openapi_spec() -> Dict[str, Any]:
    # Base schemas
    schemas = {e[0]: _schema(e[0]) for e in ENTITIES}
    # Inject finite state machine transition metadata required by tests
    # Align transitions with runtime FSM (QUEUED -> STARTED -> COMPLETED)
    schemas["PrintJob"]["x-transitions"] = ["QUEUED", "STARTED", "COMPLETED"]
    # Order lifecycle transitions (NEW -> APPROVED -> FULFILLED -> COMPLETED; any non-terminal except COMPLETED can CANCEL)
    schemas["Order"]["x-transitions"] = ["NEW", "APPROVED", "FULFILLED", "COMPLETED", "CANCELLED"]
    # AccountingTransaction lifecycle (NEW -> APPROVED -> PAID | NEW -> REJECTED)
    schemas["AccountingTransaction"]["x-transitions"] = ["NEW", "APPROVED", "PAID", "REJECTED"]
    # PurchaseOrder lifecycle (DRAFT -> RECEIVED -> CLOSED)
    schemas["PurchaseOrder"]["x-transitions"] = ["DRAFT", "RECEIVED", "CLOSED"]
    # RepairTicket lifecycle (NEW -> IN_PROGRESS -> COMPLETED -> CLOSED; CANCELLED alternative path)
    schemas["RepairTicket"]["x-transitions"] = ["NEW", "IN_PROGRESS", "COMPLETED", "CANCELLED", "CLOSED"]
    # CatalogItem simple status toggle ACTIVE <-> ARCHIVED
    schemas["CatalogItem"]["x-transitions"] = ["ACTIVE", "ARCHIVED"]

    components: Dict[str, Any] = {
        "schemas": schemas
        | {
            "Pagination": {
                "type": "object",
                "properties": {
                    "total": {"type": "integer"},
                    "limit": {"type": "integer"},
                    "offset": {"type": "integer"},
                    "returned": {"type": "integer"},
                },
                "required": ["total", "limit", "offset", "returned"],
            },
            "Error": {"type": "object", "properties": {"error": {"type": "string"}}, "required": ["error"]},
        },
        "responses": {"NotFound": {"description": "Not Found"}, "BadRequest": {"description": "Bad Request"}},
        "securitySchemes": {"BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}},
        "parameters": {},
    }

    params = components["parameters"]
    params.update({
        "LimitParam": {"name": "limit", "in": "query", "schema": {"type": "integer", "default": 50}},
        "OffsetParam": {"name": "offset", "in": "query", "schema": {"type": "integer", "default": 0}},
    })
    for pname, desc in SORT_DETAILS.items():
        params[pname] = {"name": "sort", "in": "query", "schema": {"type": "string"}, "description": desc}

    paths: Dict[str, Any] = {
        "/iam/auth/login": {"post": {"summary": "Login", "responses": {"200": {"description": "JWT issued"}}}},
        "/iam/auth/me": {"get": {"summary": "Current user", "responses": {"200": {"description": "OK"}}}},
    }

    entity_meta = {e[0]: (e[1], e[2], e[3]) for e in ENTITIES}

    for schema_name, domain, coll, id_param in ENTITIES:
        # Prefer per-service module (future customization), otherwise use generic builder
        if domain == "inventory":
            frag = inv_dom.build_paths(schema_name, coll, id_param)
        elif domain == "sales":
            frag = sales_dom.build_paths(schema_name, coll, id_param)
        elif domain == "print":
            frag = print_dom.build_paths(schema_name, coll, id_param)
        elif domain == "accounting":
            frag = acc_dom.build_paths(schema_name, coll, id_param)
        elif domain == "catalog":
            frag = cat_dom.build_paths(schema_name, coll, id_param)
        elif domain == "po":
            frag = po_dom.build_paths(schema_name, coll, id_param)
        elif domain == "repairs":
            frag = rpr_dom.build_paths(schema_name, coll, id_param)
        else:
            frag = build_service_paths(schema_name, domain, coll, id_param)
        # deterministic merge: keys are unique per entity, order preserved by insertion
        for k, v in frag.items():
            paths[k] = v

    # Assign read permissions automatically for list & single resource endpoints
    for schema_name, (domain, coll, id_param) in entity_meta.items():
        service = SERVICE_CODE.get(domain)
        if not service:
            continue
        list_path = f"/{domain}/{coll}"
        single_path = f"{list_path}/{{{id_param}}}"
        for meth in ("get", "head"):
            if meth in paths.get(list_path, {}):
                paths[list_path][meth].setdefault("x-required-permissions", [f"{service}.READ"])
            if meth in paths.get(single_path, {}):
                paths[single_path][meth].setdefault("x-required-permissions", [f"{service}.READ"])

    # Add operationIds & tags
    tag_desc: Dict[str, str] = {}
    for path, ops in paths.items():
        tag = path.split("/")[1].capitalize()
        for method, od in ops.items():
            rid = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
            od["operationId"] = f"auto_{method}_{rid}"
            od["tags"] = [tag]
        tag_desc[tag] = f"{tag} domain endpoints"

    return {
        "openapi": "3.0.3",
        "info": {"title": "3D Store API", "version": "0.1.0"},
        "paths": paths,
        "components": components,
        "security": [{"BearerAuth": []}],
        "tags": [{"name": n, "description": d} for n, d in sorted(tag_desc.items())],
    }
