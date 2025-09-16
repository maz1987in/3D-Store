from __future__ import annotations
from flask import Blueprint, request, abort
from flask_jwt_extended import get_jwt, get_jwt_identity
from sqlalchemy import select
from app import get_db
from app.decorators.auth import require_permissions
from app.decorators.audit import audit_log
from app.services.policy import assert_branch_access
from app.utils.listing import make_cached_list_response, handle_conditional, apply_pagination, compute_etag, canonicalize_timestamp, _http_date
from app.utils.sorting import apply_multi_sort
from app.utils.filters import apply_filters
from app.models.purchase_order import PurchaseOrder
from app.utils.validation import validate_status
from app.utils.fsm import TransitionValidator
from sqlalchemy import func

po_bp = Blueprint('po', __name__)

# Finite state machine for PurchaseOrder transitions
PO_FSM = TransitionValidator({
    PurchaseOrder.STATUS_DRAFT: {PurchaseOrder.STATUS_RECEIVED},
    PurchaseOrder.STATUS_RECEIVED: {PurchaseOrder.STATUS_CLOSED},
    PurchaseOrder.STATUS_CLOSED: set(),
})

@po_bp.get('/purchase-orders')
@require_permissions('PO.READ')
def list_purchase_orders():
    session = get_db()
    claims = get_jwt()
    q = session.query(PurchaseOrder)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(PurchaseOrder.branch_id.in_(branch_ids))
    filter_specs = {
        'vendor_name': {'op': lambda qu, v: qu.filter(PurchaseOrder.vendor_name.ilike(f'%{v}%'))},
    'status': {'op': lambda qu, v: qu.filter(PurchaseOrder.status==v), 'validate': lambda v: v in PurchaseOrder.ALL_STATUSES},
        'branch_id': {'coerce': int, 'op': lambda qu, v: qu.filter(PurchaseOrder.branch_id==v) if (not branch_ids or v in branch_ids) else qu.filter(PurchaseOrder.id==0)}
    }
    q = apply_filters(q, filter_specs, request.args)
    sort_expr = request.args.get('sort')
    allowed = {
        'vendor_name': PurchaseOrder.vendor_name,
        'status': PurchaseOrder.status,
        'total_cents': PurchaseOrder.total_cents,
        'updated_at': PurchaseOrder.updated_at,
        'id': PurchaseOrder.id
    }
    q = apply_multi_sort(q, sort_expr, allowed, PurchaseOrder.id)
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_po_json(r) for r in rows]
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        return cond
    return resp

@po_bp.route('/purchase-orders', methods=['HEAD'])
@require_permissions('PO.READ')
def head_purchase_orders():
    session = get_db()
    claims = get_jwt()
    q = session.query(PurchaseOrder)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(PurchaseOrder.branch_id.in_(branch_ids))
    filter_specs = {
        'vendor_name': {'op': lambda qu, v: qu.filter(PurchaseOrder.vendor_name.ilike(f'%{v}%'))},
    'status': {'op': lambda qu, v: qu.filter(PurchaseOrder.status==v), 'validate': lambda v: v in PurchaseOrder.ALL_STATUSES},
        'branch_id': {'coerce': int, 'op': lambda qu, v: qu.filter(PurchaseOrder.branch_id==v) if (not branch_ids or v in branch_ids) else qu.filter(PurchaseOrder.id==0)}
    }
    q = apply_filters(q, filter_specs, request.args)
    sort_expr = request.args.get('sort')
    allowed = {
        'vendor_name': PurchaseOrder.vendor_name,
        'status': PurchaseOrder.status,
        'total_cents': PurchaseOrder.total_cents,
        'updated_at': PurchaseOrder.updated_at,
        'id': PurchaseOrder.id
    }
    q = apply_multi_sort(q, sort_expr, allowed, PurchaseOrder.id)
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_po_json(r) for r in rows]
    if rows:
        latest_ts = rows[0].updated_at
    else:
        # fallback: compute max updated_at across all (unpaged) filtered rows
        latest_ts = session.query(func.max(PurchaseOrder.updated_at)).scalar()
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    resp.set_data(b'')
    return resp


@po_bp.post('/purchase-orders')
@require_permissions('PO.CREATE')
@audit_log('PO.CREATE', entity='PurchaseOrder', entity_id_key='id', meta_keys=['vendor_name','total_cents'])
def create_purchase_order():
    session = get_db()
    data = request.json or {}
    vendor_name = data.get('vendor_name')
    branch_id = data.get('branch_id')
    total_cents = data.get('total_cents', 0)
    if not vendor_name or branch_id is None:
        abort(400, description='vendor_name and branch_id required')
    assert_branch_access(int(branch_id))
    try:
        total_cents = int(total_cents)
    except Exception:
        abort(400, description='total_cents must be int')
    user_id = int(get_jwt_identity())
    po = PurchaseOrder(vendor_name=vendor_name, branch_id=int(branch_id), total_cents=total_cents, created_by=user_id)
    session.add(po)
    session.commit()
    return _po_json(po), 201


@po_bp.post('/purchase-orders/<int:po_id>/receive')
@require_permissions('PO.RECEIVE')
@audit_log(
    'PO.RECEIVE',
    entity='PurchaseOrder',
    entity_id_key='id',
    diff_keys=['status'],
    pre_fetch=lambda a, kw: _prefetch_po(kw.get('po_id')),
    meta_keys=['status']
)
def receive_purchase_order(po_id: int):
    session = get_db()
    po = session.execute(select(PurchaseOrder).where(PurchaseOrder.id==po_id)).scalar_one_or_none()
    if not po:
        abort(404)
    assert_branch_access(po.branch_id)
    PO_FSM.assert_can_transition(po.status, PurchaseOrder.STATUS_RECEIVED)
    po.status = validate_status(PurchaseOrder.STATUS_RECEIVED, PurchaseOrder.ALL_STATUSES)
    session.commit()
    return _po_json(po)


@po_bp.post('/purchase-orders/<int:po_id>/close')
@require_permissions('PO.CLOSE')
@audit_log(
    'PO.CLOSE',
    entity='PurchaseOrder',
    entity_id_key='id',
    diff_keys=['status'],
    pre_fetch=lambda a, kw: _prefetch_po(kw.get('po_id')),
    meta_keys=['status']
)
def close_purchase_order(po_id: int):
    session = get_db()
    po = session.execute(select(PurchaseOrder).where(PurchaseOrder.id==po_id)).scalar_one_or_none()
    if not po:
        abort(404)
    assert_branch_access(po.branch_id)
    PO_FSM.assert_can_transition(po.status, PurchaseOrder.STATUS_CLOSED)
    po.status = validate_status(PurchaseOrder.STATUS_CLOSED, PurchaseOrder.ALL_STATUSES)
    session.commit()
    return _po_json(po)

@po_bp.route('/purchase-orders/<int:po_id>', methods=['GET','HEAD'])
@require_permissions('PO.READ')
def get_purchase_order(po_id: int):
    session = get_db()
    po = session.execute(select(PurchaseOrder).where(PurchaseOrder.id==po_id)).scalar_one_or_none()
    if not po:
        abort(404)
    assert_branch_access(po.branch_id)
    latest_ts = po.updated_at
    etag = compute_etag([po.id], 1, 1, 0, latest_ts.isoformat().replace('+00:00','Z') if latest_ts else '')
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    from flask import make_response, jsonify, request as _req
    body = _po_json(po)
    resp = make_response(jsonify(body))
    resp.headers['ETag'] = etag
    if latest_ts:
        lt = canonicalize_timestamp(latest_ts)
        resp.headers['Last-Modified'] = _http_date(lt)
        resp.headers['X-Last-Modified-ISO'] = lt.isoformat().replace('+00:00','Z')
    if _req.method == 'HEAD':
        resp.set_data(b'')
    return resp


def _po_json(po: PurchaseOrder):
    return {
        'id': po.id,
        'branch_id': po.branch_id,
        'vendor_name': po.vendor_name,
        'total_cents': po.total_cents,
        'status': po.status
    }


def _prefetch_po(po_id: int):
    from sqlalchemy import select
    session = get_db()
    po = session.execute(select(PurchaseOrder).where(PurchaseOrder.id==po_id)).scalar_one_or_none()
    if not po:
        return {}
    return {'status': po.status}
