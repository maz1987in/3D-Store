"""Centralized constants for the OpenAPI spec builder.

Splitting these out keeps `app/openapi_builder.py` concise without changing
runtime behavior. Tests depend on deterministic ordering and content.
"""
from typing import Any, Dict, List, Tuple

# Entity registry: (SchemaName, domain prefix, collection path, id param)
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

# Declarative registry for action (state-changing) endpoints.
ACTION_REGISTRY: Dict[str, List[Dict[str, str]]] = {
    "PrintJob": [
        {"action": "start", "summary": "Start print job", "permission": "PRINT.START"},
        {"action": "complete", "summary": "Complete print job", "permission": "PRINT.COMPLETE"},
    ],
    "Order": [
        {"action": "approve", "summary": "Approve order", "permission": "SALES.APPROVE"},
        {"action": "fulfill", "summary": "Fulfill order", "permission": "SALES.FULFILL"},
        {"action": "complete", "summary": "Complete order", "permission": "SALES.COMPLETE"},
        {"action": "cancel", "summary": "Cancel order", "permission": "SALES.CANCEL"},
    ],
    "PurchaseOrder": [
        {"action": "receive", "summary": "Receive purchase order", "permission": "PO.RECEIVE"},
        {"action": "close", "summary": "Close purchase order", "permission": "PO.CLOSE"},
    ],
    "RepairTicket": [
        {"action": "start", "summary": "Start repair ticket", "permission": "RPR.MANAGE"},
        {"action": "complete", "summary": "Complete repair ticket", "permission": "RPR.MANAGE"},
        {"action": "close", "summary": "Close repair ticket", "permission": "RPR.MANAGE"},
        {"action": "cancel", "summary": "Cancel repair ticket", "permission": "RPR.MANAGE"},
    ],
    "AccountingTransaction": [
        {"action": "approve", "summary": "Approve accounting transaction", "permission": "ACC.APPROVE"},
        {"action": "pay", "summary": "Pay accounting transaction", "permission": "ACC.PAY"},
        {"action": "reject", "summary": "Reject accounting transaction", "permission": "ACC.APPROVE"},
    ],
    "CatalogItem": [
        {"action": "archive", "summary": "Archive catalog item", "permission": "CAT.MANAGE"},
        {"action": "activate", "summary": "Activate catalog item", "permission": "CAT.MANAGE"},
    ],
}

# Service code mapping for automatic READ permission assignment for list/GET/HEAD endpoints.
SERVICE_CODE = {
    "inventory": "INV",
    "sales": "SALES",
    "print": "PRINT",
    "accounting": "ACC",
    "catalog": "CAT",
    "po": "PO",
    "repairs": "RPR",
}

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

__all__ = [
    "ENTITIES",
    "ACTION_REGISTRY",
    "SERVICE_CODE",
    "SORT_PARAM_MAP",
    "SORT_DETAILS",
]
