"""Clean minimal deterministic OpenAPI spec builder.

Scope (purposefully narrow):
- Auth endpoints: /iam/auth/login (POST), /iam/auth/me (GET)
- For each tracked entity: list + single GET & HEAD with caching headers
- Reusable params: limit, offset, per-entity sort

This replaces the previously corrupted openapi.py. Import build_openapi_spec from this module.
"""
from typing import Any, Dict, List, Tuple

__all__ = ["build_openapi_spec"]

ENTITIES: List[Tuple[str, str, str, str]] = [
    ("Product", "inventory", "products", "product_id"),
    ("Order", "sales", "orders", "order_id"),
    ("PrintJob", "print", "jobs", "job_id"),
    ("AccountingTransaction", "accounting", "transactions", "tx_id"),
    ("CatalogItem", "catalog", "items", "item_id"),
    ("PurchaseOrder", "po", "purchase-orders", "po_id"),
    ("Vendor", "po", "vendors", "vendor_id"),
    ("RepairTicket", "repairs", "tickets", "ticket_id"),
]

SORT_PARAM_MAP = {
    "Product": "SortProductsParam",
    "Order": "SortOrdersParam",
    "PrintJob": "SortPrintJobsParam",
    "AccountingTransaction": "SortAccountingParam",
    "CatalogItem": "SortCatalogItemsParam",
    "PurchaseOrder": "SortPurchaseOrdersParam",
    "Vendor": "SortVendorsParam",
    "RepairTicket": "SortRepairsParam",
}

SORT_DETAILS = {
    "SortProductsParam": "Multi-field sort (name,sku,updated_at,id). Prefix - for desc",
    "SortOrdersParam": "Multi-field sort (customer_name,status,total_cents,updated_at,id). Prefix - for desc",
    "SortPrintJobsParam": "Multi-field sort (status,updated_at,id). Prefix - for desc",
    "SortAccountingParam": "Multi-field sort (status,amount_cents,updated_at,id). Prefix - for desc",
    "SortCatalogItemsParam": "Multi-field sort (price_cents,name,updated_at,id). Prefix - for desc",
    "SortPurchaseOrdersParam": "Multi-field sort (vendor_name,status,total_cents,updated_at,id). Prefix - for desc",
    "SortVendorsParam": "Multi-field sort (name,status,updated_at,id). Prefix - for desc",
    "SortRepairsParam": "Multi-field sort (customer_name,status,updated_at,id). Prefix - for desc",
}

def _schema(name: str) -> Dict[str, Any]:
    return {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}

def _headers() -> Dict[str, Any]:
    return {
        "ETag": {"schema": {"type": "string"}},
        "Last-Modified": {"schema": {"type": "string"}},
        "X-Last-Modified-ISO": {"schema": {"type": "string"}},
    }

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
        "schemas": schemas | {
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

    for schema_name, domain, coll, id_param in ENTITIES:
        list_path = f"/{domain}/{coll}"
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
                        "headers": _headers(),
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
            "head": {"summary": f"{schema_name} list validators", "responses": {"200": {"description": "Headers only", "headers": _headers()}, "304": {"description": "Not Modified"}}},
        }
        single_path = f"{list_path}/{{{id_param}}}"
        readable = schema_name.lower().replace("transaction", " transaction").replace("purchaseorder", "purchase order")
        paths[single_path] = {
            "get": {
                "summary": f"Get {readable}",
                "parameters": [{"name": id_param, "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {
                    "200": {"description": "OK", "headers": _headers(), "content": {"application/json": {"schema": {"$ref": f"#/components/schemas/{schema_name}"}}}},
                    "304": {"description": "Not Modified"},
                    "404": {"$ref": "#/components/responses/NotFound"},
                },
            },
            "head": {
                "summary": f"{schema_name} validators",
                "parameters": [{"name": id_param, "in": "path", "required": True, "schema": {"type": "integer"}}],
                "responses": {
                    "200": {"description": "Headers only", "headers": _headers()},
                    "304": {"description": "Not Modified"},
                    "404": {"$ref": "#/components/responses/NotFound"},
                },
            },
        }

        # Domain-specific action endpoints
        if schema_name == "PrintJob":
            action_common_params = [{"name": id_param, "in": "path", "required": True, "schema": {"type": "integer"}}]
            for action, summary in [
                ("start", "Start print job"),
                ("complete", "Complete print job"),
            ]:
                act_path = f"{single_path}/{action}"
                paths[act_path] = {
                    "post": {
                        "summary": summary,
                        "parameters": action_common_params,
                        "responses": {
                            "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PrintJob"}}}},
                            "400": {"$ref": "#/components/responses/BadRequest"},
                            "404": {"$ref": "#/components/responses/NotFound"},
                        },
                    }
                }
        elif schema_name == "Order":
            action_common_params = [{"name": id_param, "in": "path", "required": True, "schema": {"type": "integer"}}]
            for action, summary in [
                ("approve", "Approve order"),
                ("fulfill", "Fulfill order"),
                ("complete", "Complete order"),
                ("cancel", "Cancel order"),
            ]:
                act_path = f"{single_path}/{action}"
                paths[act_path] = {
                    "post": {
                        "summary": summary,
                        "parameters": action_common_params,
                        "responses": {
                            "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Order"}}}},
                            "400": {"$ref": "#/components/responses/BadRequest"},
                            "404": {"$ref": "#/components/responses/NotFound"},
                        },
                    }
                }
        elif schema_name == "PurchaseOrder":
            action_common_params = [{"name": id_param, "in": "path", "required": True, "schema": {"type": "integer"}}]
            for action, summary in [
                ("receive", "Receive purchase order"),
                ("close", "Close purchase order"),
            ]:
                act_path = f"{single_path}/{action}"
                paths[act_path] = {
                    "post": {
                        "summary": summary,
                        "parameters": action_common_params,
                        "responses": {
                            "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PurchaseOrder"}}}},
                            "400": {"$ref": "#/components/responses/BadRequest"},
                            "404": {"$ref": "#/components/responses/NotFound"},
                        },
                    }
                }
        elif schema_name == "RepairTicket":
            action_common_params = [{"name": id_param, "in": "path", "required": True, "schema": {"type": "integer"}}]
            for action, summary in [
                ("start", "Start repair ticket"),
                ("complete", "Complete repair ticket"),
                ("close", "Close repair ticket"),
                ("cancel", "Cancel repair ticket"),
            ]:
                act_path = f"{single_path}/{action}"
                paths[act_path] = {
                    "post": {
                        "summary": summary,
                        "parameters": action_common_params,
                        "responses": {
                            "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RepairTicket"}}}},
                            "400": {"$ref": "#/components/responses/BadRequest"},
                            "404": {"$ref": "#/components/responses/NotFound"},
                        },
                    }
                }
        elif schema_name == "AccountingTransaction":
            action_common_params = [{"name": id_param, "in": "path", "required": True, "schema": {"type": "integer"}}]
            for action, summary in [
                ("approve", "Approve accounting transaction"),
                ("pay", "Pay accounting transaction"),
                ("reject", "Reject accounting transaction"),
            ]:
                act_path = f"{single_path}/{action}"
                paths[act_path] = {
                    "post": {
                        "summary": summary,
                        "parameters": action_common_params,
                        "responses": {
                            "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AccountingTransaction"}}}},
                            "400": {"$ref": "#/components/responses/BadRequest"},
                            "404": {"$ref": "#/components/responses/NotFound"},
                        },
                    }
                }
        elif schema_name == "CatalogItem":
            action_common_params = [{"name": id_param, "in": "path", "required": True, "schema": {"type": "integer"}}]
            for action, summary in [
                ("archive", "Archive catalog item"),
                ("activate", "Activate catalog item"),
            ]:
                act_path = f"{single_path}/{action}"
                paths[act_path] = {
                    "post": {
                        "summary": summary,
                        "parameters": action_common_params,
                        "responses": {
                            "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CatalogItem"}}}},
                            "400": {"$ref": "#/components/responses/BadRequest"},
                            "404": {"$ref": "#/components/responses/NotFound"},
                        },
                    }
                }

    # Inject x-required-permissions based on simple heuristics from path patterns
    for path, ops in paths.items():
        for method, od in ops.items():
            # Skip if already annotated
            if 'x-required-permissions' in od:
                continue
            perms: list[str] = []
            if path.startswith('/iam/auth'):
                perms = []  # auth open
            elif '/print/jobs' in path:
                if path.endswith('/start'):
                    perms = ['PRINT.START']
                elif path.endswith('/complete'):
                    perms = ['PRINT.COMPLETE']
                else:
                    perms = ['PRINT.READ'] if method in ('get','head') else []
            elif '/sales/orders' in path:
                if path.endswith('/approve'):
                    perms = ['SALES.APPROVE']
                elif path.endswith('/fulfill'):
                    perms = ['SALES.FULFILL']
                elif path.endswith('/complete'):
                    perms = ['SALES.COMPLETE']
                elif path.endswith('/cancel'):
                    perms = ['SALES.CANCEL']
                else:
                    perms = ['SALES.READ'] if method in ('get','head') else []
            elif '/po/purchase-orders' in path:
                if path.endswith('/receive'):
                    perms = ['PO.RECEIVE']
                elif path.endswith('/close'):
                    perms = ['PO.CLOSE']
                else:
                    perms = ['PO.READ'] if method in ('get','head') else []
            elif '/repairs/tickets' in path:
                if any(path.endswith(suf) for suf in ('/start','/complete','/close','/cancel')):
                    perms = ['RPR.MANAGE']
                else:
                    perms = ['RPR.READ'] if method in ('get','head') else []
            elif '/accounting/transactions' in path:
                if path.endswith('/approve'):
                    perms = ['ACC.APPROVE']
                elif path.endswith('/pay'):
                    perms = ['ACC.PAY']
                elif path.endswith('/reject'):
                    perms = ['ACC.APPROVE']
                else:
                    perms = ['ACC.READ'] if method in ('get','head') else []
            elif '/inventory/products' in path:
                perms = ['INV.READ'] if method in ('get','head') else []
            elif '/catalog/items' in path:
                perms = ['CAT.READ'] if method in ('get','head') else []
            elif '/vendors' in path:
                perms = ['PO.READ'] if method in ('get','head') else []
            # Only attach if determined
            if perms:
                od['x-required-permissions'] = perms
            action_common_params = [{"name": id_param, "in": "path", "required": True, "schema": {"type": "integer"}}]
            for action, summary in [
                ("start", "Start repair ticket"),
                ("complete", "Complete repair ticket"),
                ("close", "Close repair ticket"),
                ("cancel", "Cancel repair ticket"),
            ]:
                act_path = f"{single_path}/{action}"
                paths[act_path] = {
                    "post": {
                        "summary": summary,
                        "parameters": action_common_params,
                        "responses": {
                            "200": {"description": "OK", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RepairTicket"}}}},
                            "400": {"$ref": "#/components/responses/BadRequest"},
                            "404": {"$ref": "#/components/responses/NotFound"},
                        },
                    }
                }

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
