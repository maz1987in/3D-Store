from __future__ import annotations
from flask import Blueprint, request
from sqlalchemy import func, select, and_
from flask_jwt_extended import get_jwt
from app.decorators.auth import require_permissions
from app.utils.listing import make_cached_list_response, handle_conditional, apply_pagination
from app import get_db
from app.models.order import Order
from app.models.print_job import PrintJob
from app.models.purchase_order import PurchaseOrder
from app.models.repair_ticket import RepairTicket
from app.models.accounting_transaction import AccountingTransaction
from app.models.catalog_item import CatalogItem
from app.models.vendor import Vendor

rpt_bp = Blueprint('reports', __name__)

def _parse_date(value: str):
    from datetime import datetime
    if not value:
        return None
    for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S%z'):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None

def _gather_metrics(branch_ids, include_financial: bool = False, start_date=None, end_date=None):
    session = get_db()
    metrics = []
    # Helper to run grouped count when statuses exist
    def status_counts(model, domain_name, sum_field=None):
        # Base grouped query (counts)
        q = session.query(model.status, func.count(model.id))
        if branch_ids:
            q = q.filter(model.branch_id.in_(branch_ids))
        if start_date or end_date:
            dt_filters = []
            if start_date:
                dt_filters.append(model.updated_at >= start_date)
            if end_date:
                dt_filters.append(model.updated_at <= end_date)
            if dt_filters:
                q = q.filter(and_(*dt_filters))
        q = q.group_by(model.status)
        counts = {status: int(count) for status, count in q.all()}
        sums = {}
        if include_financial and sum_field is not None:
            q2 = session.query(model.status, func.coalesce(func.sum(sum_field), 0))
            if branch_ids:
                q2 = q2.filter(model.branch_id.in_(branch_ids))
            if start_date or end_date:
                dt_filters2 = []
                if start_date:
                    dt_filters2.append(model.updated_at >= start_date)
                if end_date:
                    dt_filters2.append(model.updated_at <= end_date)
                if dt_filters2:
                    q2 = q2.filter(and_(*dt_filters2))
            q2 = q2.group_by(model.status)
            sums = {status: int(total) for status, total in q2.all()}
        for status, count in counts.items():
            row = {"domain": domain_name, "status": status, "count": count}
            if include_financial and sum_field is not None:
                row["sum_cents"] = sums.get(status, 0)
            metrics.append(row)

    status_counts(Order, 'Order', Order.total_cents)
    status_counts(PrintJob, 'PrintJob')
    status_counts(PurchaseOrder, 'PurchaseOrder', PurchaseOrder.total_cents)
    status_counts(RepairTicket, 'RepairTicket')
    status_counts(AccountingTransaction, 'AccountingTransaction', AccountingTransaction.amount_cents)
    status_counts(CatalogItem, 'CatalogItem')
    status_counts(Vendor, 'Vendor')
    # Deterministic ordering
    metrics.sort(key=lambda m: (m['domain'], m.get('status') or ''))
    # Compute latest updated_at across involved models for caching headers
    latest_candidates = []
    for model in (Order, PrintJob, PurchaseOrder, RepairTicket, AccountingTransaction, CatalogItem, Vendor):
        subq = session.execute(select(func.max(model.updated_at))).scalar_one_or_none()
        if subq is not None:
            latest_candidates.append(subq)
    latest_ts = None
    if latest_candidates:
        latest_ts = max([c for c in latest_candidates if c is not None])
    return metrics, latest_ts


@rpt_bp.get('/metrics')
@require_permissions('RPT.READ')
def list_metrics():
    claims = get_jwt()
    branch_ids = claims.get('branch_ids') or []
    include_financial = request.args.get('include_financial') == 'true'
    start_date = _parse_date(request.args.get('start_date'))
    end_date = _parse_date(request.args.get('end_date'))
    metrics, latest_ts = _gather_metrics(branch_ids, include_financial, start_date, end_date)
    # Apply simple pagination over metric rows
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    total = len(metrics)
    sliced = metrics[offset:offset+limit]
    resp, etag = make_cached_list_response(sliced, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        return cond
    return resp

@rpt_bp.route('/metrics', methods=['HEAD'])
@require_permissions('RPT.READ')
def head_metrics():
    claims = get_jwt()
    branch_ids = claims.get('branch_ids') or []
    include_financial = request.args.get('include_financial') == 'true'
    start_date = _parse_date(request.args.get('start_date'))
    end_date = _parse_date(request.args.get('end_date'))
    metrics, latest_ts = _gather_metrics(branch_ids, include_financial, start_date, end_date)
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    total = len(metrics)
    sliced = metrics[offset:offset+limit]
    resp, etag = make_cached_list_response(sliced, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    resp.set_data(b'')
    return resp


@rpt_bp.get('/metrics/pivot')
@require_permissions('RPT.READ')
def list_metrics_pivot():
    """Return pivoted metrics: { domain: { status: count, ... }, ... }"""
    claims = get_jwt()
    branch_ids = claims.get('branch_ids') or []
    include_financial = request.args.get('include_financial') == 'true'
    start_date = _parse_date(request.args.get('start_date'))
    end_date = _parse_date(request.args.get('end_date'))
    metrics, latest_ts = _gather_metrics(branch_ids, include_financial, start_date, end_date)
    pivot = {}
    for m in metrics:
        pivot.setdefault(m['domain'], {})[m['status']] = m['count']
    # Flatten into deterministic list for pagination though pivot is nested
    # We still apply limit/offset on the domain keys for consistency
    domain_items = sorted(pivot.items())
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    total = len(domain_items)
    sliced = domain_items[offset:offset+limit]
    sliced_dict = {k: v for k, v in sliced}
    # Reuse list response helper (wrap into data list with single object) to keep pagination contract
    rows_json = [{"pivot": sliced_dict}]
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        return cond
    return resp


@rpt_bp.route('/metrics/pivot', methods=['HEAD'])
@require_permissions('RPT.READ')
def head_metrics_pivot():
    claims = get_jwt()
    branch_ids = claims.get('branch_ids') or []
    include_financial = request.args.get('include_financial') == 'true'
    start_date = _parse_date(request.args.get('start_date'))
    end_date = _parse_date(request.args.get('end_date'))
    metrics, latest_ts = _gather_metrics(branch_ids, include_financial, start_date, end_date)
    pivot = {}
    for m in metrics:
        pivot.setdefault(m['domain'], {})[m['status']] = m['count']
    domain_items = sorted(pivot.items())
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    total = len(domain_items)
    sliced = domain_items[offset:offset+limit]
    sliced_dict = {k: v for k, v in sliced}
    rows_json = [{"pivot": sliced_dict}]
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    resp.set_data(b'')
    return resp
