from __future__ import annotations
from flask import Blueprint, request, abort
from flask_jwt_extended import get_jwt, get_jwt_identity
from sqlalchemy import select
from app import get_db
from app.models.order import Order
from app.decorators.auth import require_permissions
from app.decorators.audit import audit_log
from app.services.policy import assert_branch_access
from app.utils.listing import apply_pagination, handle_conditional, make_cached_list_response, compute_etag, canonicalize_timestamp, _http_date
from app.utils.filters import apply_filters
from app.utils.fsm import TransitionValidator
from app.utils.validation import validate_status
from app.utils.sorting import apply_multi_sort

sales_bp = Blueprint('sales', __name__)

# Order lifecycle graph:
# NEW -> APPROVED -> FULFILLED -> COMPLETED
# NEW -> CANCELLED
# APPROVED -> CANCELLED
# FULFILLED -> CANCELLED (allow cancellation until completed)
ORDER_FSM = TransitionValidator({
    Order.STATUS_NEW: {Order.STATUS_APPROVED, Order.STATUS_CANCELLED},
    Order.STATUS_APPROVED: {Order.STATUS_FULFILLED, Order.STATUS_CANCELLED},
    Order.STATUS_FULFILLED: {Order.STATUS_COMPLETED, Order.STATUS_CANCELLED},
    Order.STATUS_COMPLETED: set(),
    Order.STATUS_CANCELLED: set()
})


@sales_bp.get('/orders')
@require_permissions('SALES.READ')
def list_orders():
    session = get_db()
    claims = get_jwt()
    q = session.query(Order)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(Order.branch_id.in_(branch_ids))
    # Filters
    filter_specs = {
        'customer_name': {'op': lambda qu, v: qu.filter(Order.customer_name.ilike(f'%{v}%'))},
        'status': {'op': lambda qu, v: qu.filter(Order.status==v), 'validate': lambda v: v in Order.ALL_STATUSES},
        'branch_id': {'coerce': int, 'op': lambda qu, v: qu.filter(Order.branch_id==v) if (not branch_ids or v in branch_ids) else qu.filter(Order.id==0)}
    }
    q = apply_filters(q, filter_specs, request.args)
    sort_expr = request.args.get('sort')
    allowed = {
        'customer_name': Order.customer_name,
        'status': Order.status,
        'total_cents': Order.total_cents,
        'updated_at': Order.updated_at,
        'id': Order.id
    }
    q = apply_multi_sort(q, sort_expr, allowed, Order.id)
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_order_json(o) for o in rows]
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        return cond
    return resp


@sales_bp.route('/orders', methods=['HEAD'])
@require_permissions('SALES.READ')
def head_orders():
    """Return only validator headers (ETag / Last-Modified) for orders list."""
    session = get_db()
    claims = get_jwt()
    q = session.query(Order)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(Order.branch_id.in_(branch_ids))
    filter_specs = {
        'customer_name': {'op': lambda qu, v: qu.filter(Order.customer_name.ilike(f'%{v}%'))},
        'status': {'op': lambda qu, v: qu.filter(Order.status==v), 'validate': lambda v: v in Order.ALL_STATUSES},
        'branch_id': {'coerce': int, 'op': lambda qu, v: qu.filter(Order.branch_id==v) if (not branch_ids or v in branch_ids) else qu.filter(Order.id==0)}
    }
    q = apply_filters(q, filter_specs, request.args)
    sort_expr = request.args.get('sort')
    allowed = {
        'customer_name': Order.customer_name,
        'status': Order.status,
        'total_cents': Order.total_cents,
        'updated_at': Order.updated_at,
        'id': Order.id
    }
    q = apply_multi_sort(q, sort_expr, allowed, Order.id)
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_order_json(o) for o in rows]
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    resp.set_data(b'')
    return resp


@sales_bp.post('/orders')
@require_permissions('SALES.CREATE')
@audit_log('ORDER.CREATE', entity='Order', entity_id_key='id', meta_keys=['customer_name', 'total_cents'])
def create_order():
    session = get_db()
    data = request.json or {}
    customer_name = data.get('customer_name')
    branch_id = data.get('branch_id')
    total_cents = data.get('total_cents', 0)
    if not customer_name or branch_id is None:
        abort(400, description='customer_name and branch_id required')
    assert_branch_access(int(branch_id))
    try:
        total_cents = int(total_cents)
    except Exception:
        abort(400, description='total_cents must be int')
    user_id = int(get_jwt_identity())
    o = Order(customer_name=customer_name, branch_id=int(branch_id), total_cents=total_cents, created_by=user_id)
    session.add(o)
    session.commit()
    return _order_json(o), 201


@sales_bp.put('/orders/<int:order_id>')
@require_permissions('SALES.UPDATE')
@audit_log(
    'ORDER.UPDATE',
    entity='Order',
    entity_id_key='id',
    diff_keys=['customer_name', 'total_cents'],
    pre_fetch=lambda a, kw: _prefetch_order(kw.get('order_id')),
    meta_keys=['customer_name', 'total_cents']
)
def update_order(order_id: int):
    session = get_db()
    o = session.execute(select(Order).where(Order.id==order_id)).scalar_one_or_none()
    if not o:
        abort(404)
    assert_branch_access(o.branch_id)
    data = request.json or {}
    if 'customer_name' in data:
        if not data['customer_name']:
            abort(400, description='customer_name cannot be empty')
        o.customer_name = data['customer_name']
    if 'total_cents' in data:
        try:
            o.total_cents = int(data['total_cents'])
        except Exception:
            abort(400, description='total_cents must be int')
    session.commit()
    return _order_json(o)


@sales_bp.route('/orders/<int:order_id>', methods=['GET','HEAD'])
@require_permissions('SALES.READ')
def get_order(order_id: int):
    session = get_db()
    o = session.execute(select(Order).where(Order.id==order_id)).scalar_one_or_none()
    if not o:
        abort(404)
    assert_branch_access(o.branch_id)
    latest_ts = o.updated_at
    etag = compute_etag([o.id], 1, 1, 0, latest_ts.isoformat().replace('+00:00','Z') if latest_ts else '')
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    from flask import make_response, jsonify, request as _req
    body = _order_json(o)
    resp = make_response(jsonify(body))
    resp.headers['ETag'] = etag
    if latest_ts:
        lt = canonicalize_timestamp(latest_ts)
        resp.headers['Last-Modified'] = _http_date(lt)
        resp.headers['X-Last-Modified-ISO'] = lt.isoformat().replace('+00:00','Z')
    if _req.method == 'HEAD':
        resp.set_data(b'')
    return resp


def _transition(order_id: int, target_status: str, action: str, required_perm: str):
    """Internal helper to perform an order status transition under audit."""
    session = get_db()
    o = session.execute(select(Order).where(Order.id==order_id)).scalar_one_or_none()
    if not o:
        abort(404)
    assert_branch_access(o.branch_id)
    # Validate target status string
    validate_status(target_status, Order.ALL_STATUSES, 'status')
    # FSM enforce
    try:
        ORDER_FSM.assert_can_transition(o.status, target_status)
    except Exception:
        abort(400, description=f'Invalid transition {o.status} -> {target_status}')
    o.status = target_status
    session.commit()
    return o


def _transition_audit_meta(order_id: int):
    return _prefetch_order(order_id)


@sales_bp.post('/orders/<int:order_id>/approve')
@require_permissions('SALES.APPROVE')
@audit_log('ORDER.APPROVE', entity='Order', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_order(kw.get('order_id')), meta_keys=['status'])
def approve_order(order_id: int):
    o = _transition(order_id, Order.STATUS_APPROVED, 'ORDER.APPROVE', 'SALES.APPROVE')
    return _order_json(o)


@sales_bp.post('/orders/<int:order_id>/fulfill')
@require_permissions('SALES.FULFILL')
@audit_log('ORDER.FULFILL', entity='Order', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_order(kw.get('order_id')), meta_keys=['status'])
def fulfill_order(order_id: int):
    o = _transition(order_id, Order.STATUS_FULFILLED, 'ORDER.FULFILL', 'SALES.FULFILL')
    return _order_json(o)


@sales_bp.post('/orders/<int:order_id>/complete')
@require_permissions('SALES.COMPLETE')
@audit_log('ORDER.COMPLETE', entity='Order', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_order(kw.get('order_id')), meta_keys=['status'])
def complete_order(order_id: int):
    o = _transition(order_id, Order.STATUS_COMPLETED, 'ORDER.COMPLETE', 'SALES.COMPLETE')
    return _order_json(o)


@sales_bp.post('/orders/<int:order_id>/cancel')
@require_permissions('SALES.CANCEL')
@audit_log('ORDER.CANCEL', entity='Order', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_order(kw.get('order_id')), meta_keys=['status'])
def cancel_order(order_id: int):
    o = _transition(order_id, Order.STATUS_CANCELLED, 'ORDER.CANCEL', 'SALES.CANCEL')
    return _order_json(o)


def _order_json(o: Order):
    return {
        'id': o.id,
        'branch_id': o.branch_id,
        'customer_name': o.customer_name,
        'total_cents': o.total_cents,
        'status': o.status
    }


def _prefetch_order(order_id: int):
    from sqlalchemy import select
    session = get_db()
    o = session.execute(select(Order).where(Order.id==order_id)).scalar_one_or_none()
    if not o:
        return {}
    return {'customer_name': o.customer_name, 'total_cents': o.total_cents, 'status': o.status}
