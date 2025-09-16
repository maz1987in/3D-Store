from __future__ import annotations
from flask import Blueprint, request, abort
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import select
from app import get_db
from app.models.product import Product
from app.models.authz import Permission, Role, RolePermission, UserRole, User, Group, GroupRole, UserGroup
from app.decorators.auth import require_permissions
from app.decorators.audit import audit_log
from app.services.policy import filter_query_by_branches, assert_branch_access
from app.utils.listing import apply_pagination, handle_conditional, make_cached_list_response, compute_etag, canonicalize_timestamp, _http_date
from app.utils.filters import apply_filters

inv_bp = Blueprint('inventory', __name__)


@inv_bp.get('/products')
@require_permissions('INV.READ')
def list_products():
    session = get_db()
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    q = session.query(Product)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(Product.branch_id.in_(branch_ids))
    # Optional filters
    filter_specs = {
        'sku': {'op': lambda qu, v: qu.filter(Product.sku==v)},
        'name': {'op': lambda qu, v: qu.filter(Product.name==v)},
        'branch_id': {'coerce': int, 'op': lambda qu, v: qu.filter(Product.branch_id==v) if (not branch_ids or v in branch_ids) else qu.filter(Product.id==0)}
    }
    q = apply_filters(q, filter_specs, request.args)
    q = q.order_by(Product.id.asc())
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_product_json(p) for p in rows]
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        return cond
    return resp


@inv_bp.route('/products', methods=['HEAD'])
@require_permissions('INV.READ')
def head_products():
    """Return only validator headers (ETag / Last-Modified) for products list."""
    session = get_db()
    from flask_jwt_extended import get_jwt
    claims = get_jwt()
    q = session.query(Product)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(Product.branch_id.in_(branch_ids))
    filter_specs = {
        'sku': {'op': lambda qu, v: qu.filter(Product.sku==v)},
        'name': {'op': lambda qu, v: qu.filter(Product.name==v)},
        'branch_id': {'coerce': int, 'op': lambda qu, v: qu.filter(Product.branch_id==v) if (not branch_ids or v in branch_ids) else qu.filter(Product.id==0)}
    }
    q = apply_filters(q, filter_specs, request.args)
    q = q.order_by(Product.id.asc())
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_product_json(p) for p in rows]
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        # Ensure empty body for HEAD 304
        cond.set_data(b'')
        return cond
    resp.set_data(b'')
    return resp


@inv_bp.post('/products')
@require_permissions('INV.ADJUST')
@audit_log('PRODUCT.CREATE', entity='Product', entity_id_key='id', meta_keys=['name', 'sku'])
def create_product():
    session = get_db()
    data = request.json or {}
    name = data.get('name'); sku = data.get('sku'); branch_id = data.get('branch_id'); qty = data.get('quantity', 0)
    if not all([name, sku]) or branch_id is None:
        abort(400, description='name, sku, branch_id required')
    assert_branch_access(int(branch_id))  # ensure creator may create in branch
    if session.execute(select(Product).where(Product.sku==sku)).scalar_one_or_none():
        abort(400, description='sku exists')
    # identity stored as string in JWT
    user_id = int(get_jwt_identity())
    p = Product(name=name, sku=sku, branch_id=int(branch_id), quantity=int(qty), description_i18n=data.get('description_i18n') or {}, created_by=user_id)
    session.add(p)
    session.commit()
    return _product_json(p), 201


@inv_bp.route('/products/<int:product_id>', methods=['GET','HEAD'])
@require_permissions('INV.READ')
def get_product(product_id: int):
    session = get_db()
    p = session.execute(select(Product).where(Product.id==product_id)).scalar_one_or_none()
    if not p:
        abort(404)
    assert_branch_access(p.branch_id)
    latest_ts = p.updated_at
    etag = compute_etag([p.id], 1, 1, 0, latest_ts.isoformat().replace('+00:00','Z') if latest_ts else '')
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    from flask import make_response, jsonify, request as _req
    body = _product_json(p)
    resp = make_response(jsonify(body))
    resp.headers['ETag'] = etag
    if latest_ts:
        lt = canonicalize_timestamp(latest_ts)
        resp.headers['Last-Modified'] = _http_date(lt)
        resp.headers['X-Last-Modified-ISO'] = lt.isoformat().replace('+00:00','Z')
    if _req.method == 'HEAD':
        resp.set_data(b'')
    return resp


@inv_bp.put('/products/<int:product_id>/adjust')
@require_permissions('INV.ADJUST')
@audit_log(
    'PRODUCT.ADJUST',
    entity='Product',
    entity_id_key='id',
    diff_keys=['quantity'],
    pre_fetch=lambda a, kw: _prefetch_product(kw.get('product_id')),
    meta_keys=['quantity']
)
def adjust_product(product_id: int):
    session = get_db()
    p = session.execute(select(Product).where(Product.id==product_id)).scalar_one_or_none()
    if not p:
        abort(404)
    assert_branch_access(p.branch_id)
    data = request.json or {}
    delta = data.get('delta')
    if delta is None:
        abort(400, description='delta required')
    try:
        delta = int(delta)
    except Exception:
        abort(400, description='delta must be int')
    p.quantity = int(p.quantity) + delta
    session.commit()
    return _product_json(p)


def _product_json(p: Product):
    return {
        'id': p.id,
        'name': p.name,
        'sku': p.sku,
        'branch_id': p.branch_id,
        'quantity': p.quantity,
        'description_i18n': p.description_i18n or {}
    }


def _prefetch_product(product_id: int):
    from sqlalchemy import select
    session = get_db()
    p = session.execute(select(Product).where(Product.id==product_id)).scalar_one_or_none()
    if not p:
        return {}
    return {'quantity': p.quantity}
