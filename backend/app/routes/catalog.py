from __future__ import annotations
from flask import Blueprint, request, abort
from flask_jwt_extended import get_jwt, get_jwt_identity
from sqlalchemy import select, func
from app.decorators.auth import require_permissions
from app.decorators.audit import audit_log
from app.utils.listing import make_cached_list_response, handle_conditional, apply_pagination, compute_etag, canonicalize_timestamp, _http_date
from app.services.policy import assert_branch_access
from app.models.catalog_item import CatalogItem
from app.utils.validation import validate_status
from app import get_db
from app.utils.sorting import apply_multi_sort

cat_bp = Blueprint('catalog', __name__)

def _item_json(i: CatalogItem):
    return {
        'id': i.id,
        'branch_id': i.branch_id,
        'name': i.name,
        'category': i.category,
        'sku': i.sku,
        'price_cents': i.price_cents,
        'status': i.status,
        'description_i18n': i.description_i18n or {}
    }

@cat_bp.get('/items')
@require_permissions('CAT.READ')
def list_items():
    session = get_db()
    claims = get_jwt()
    q = session.query(CatalogItem)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(CatalogItem.branch_id.in_(branch_ids))
    # filters
    if name := request.args.get('name'):
        q = q.filter(CatalogItem.name.ilike(f"%{name}%"))
    if category := request.args.get('category'):
        q = q.filter(CatalogItem.category==category)
    if sku := request.args.get('sku'):
        q = q.filter(CatalogItem.sku==sku)
    if status := request.args.get('status'):
        q = q.filter(CatalogItem.status==status)
    # price range filters
    min_price = request.args.get('min_price_cents')
    max_price = request.args.get('max_price_cents')
    try:
        if min_price is not None:
            min_val = int(min_price)
            q = q.filter(CatalogItem.price_cents >= min_val)
        if max_price is not None:
            max_val = int(max_price)
            q = q.filter(CatalogItem.price_cents <= max_val)
        if min_price is not None and max_price is not None and int(min_price) > int(max_price):
            abort(400, description='min_price_cents cannot exceed max_price_cents')
    except ValueError:
        abort(400, description='min_price_cents/max_price_cents must be integers')
    # sorting
    sort_expr = request.args.get('sort')
    allowed = {
        'price_cents': CatalogItem.price_cents,
        'name': CatalogItem.name,
        'updated_at': CatalogItem.updated_at,
        'id': CatalogItem.id
    }
    q = apply_multi_sort(q, sort_expr, allowed, CatalogItem.id)
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_item_json(r) for r in rows]
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        return cond
    return resp

@cat_bp.route('/items', methods=['HEAD'])
@require_permissions('CAT.READ')
def head_items():
    session = get_db()
    claims = get_jwt()
    q = session.query(CatalogItem)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(CatalogItem.branch_id.in_(branch_ids))
    # replicate filters for cache correctness
    if name := request.args.get('name'):
        q = q.filter(CatalogItem.name.ilike(f"%{name}%"))
    if category := request.args.get('category'):
        q = q.filter(CatalogItem.category==category)
    if sku := request.args.get('sku'):
        q = q.filter(CatalogItem.sku==sku)
    if status := request.args.get('status'):
        q = q.filter(CatalogItem.status==status)
    min_price = request.args.get('min_price_cents')
    max_price = request.args.get('max_price_cents')
    try:
        if min_price is not None:
            q = q.filter(CatalogItem.price_cents >= int(min_price))
        if max_price is not None:
            q = q.filter(CatalogItem.price_cents <= int(max_price))
        if min_price is not None and max_price is not None and int(min_price) > int(max_price):
            abort(400, description='min_price_cents cannot exceed max_price_cents')
    except ValueError:
        abort(400, description='min_price_cents/max_price_cents must be integers')
    sort_expr = request.args.get('sort')
    allowed = {
        'price_cents': CatalogItem.price_cents,
        'name': CatalogItem.name,
        'updated_at': CatalogItem.updated_at,
        'id': CatalogItem.id
    }
    q = apply_multi_sort(q, sort_expr, allowed, CatalogItem.id)
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_item_json(r) for r in rows]
    latest_ts = rows[0].updated_at if rows else None
    if not rows:
        latest_ts = session.query(func.max(CatalogItem.updated_at)).scalar()
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    resp.set_data(b'')
    return resp

@cat_bp.post('/items')
@require_permissions('CAT.CREATE')
@audit_log('CAT.ITEM.CREATE', entity='CatalogItem', entity_id_key='id', meta_keys=['name','sku','category','status'])
def create_item():
    session = get_db()
    data = request.json or {}
    required = ['name','sku','category','branch_id']
    if any(data.get(k) in (None, '') for k in required):
        abort(400, description='name, sku, category, branch_id required')
    branch_id = int(data['branch_id'])
    assert_branch_access(branch_id)
    price_cents = int(data.get('price_cents', 0))
    description_i18n = data.get('description_i18n') or {}
    if not isinstance(description_i18n, dict):
        abort(400, description='description_i18n must be object')
    user_id = int(get_jwt_identity())
    item = CatalogItem(
        branch_id=branch_id,
        name=data['name'],
        sku=data['sku'],
        category=data['category'],
        price_cents=price_cents,
        description_i18n=description_i18n,
        created_by=user_id
    )
    session.add(item)
    session.commit()
    return _item_json(item), 201

def _prefetch_item(item_id: int):
    session = get_db()
    return session.execute(select(CatalogItem).where(CatalogItem.id==item_id)).scalar_one_or_none()

@cat_bp.put('/items/<int:item_id>')
@require_permissions('CAT.MANAGE')
@audit_log('CAT.ITEM.UPDATE', entity='CatalogItem', entity_id_key='id', diff_keys=['name','category','price_cents','description_i18n'], pre_fetch=lambda a, kw: _prefetch_item(kw.get('item_id')), meta_keys=['name','category','status'])
def update_item(item_id: int):
    session = get_db()
    item = session.execute(select(CatalogItem).where(CatalogItem.id==item_id)).scalar_one_or_none()
    if not item:
        abort(404)
    assert_branch_access(item.branch_id)
    data = request.json or {}
    for field in ['name','category','price_cents','description_i18n']:
        if field in data:
            if field == 'price_cents':
                try:
                    setattr(item, field, int(data[field]))
                except Exception:
                    abort(400, description='price_cents must be int')
            elif field == 'description_i18n':
                if not isinstance(data[field], dict):
                    abort(400, description='description_i18n must be object')
                setattr(item, field, data[field])
            else:
                setattr(item, field, data[field])
    session.commit()
    return _item_json(item)

@cat_bp.post('/items/<int:item_id>/archive')
@require_permissions('CAT.MANAGE')
@audit_log('CAT.ITEM.ARCHIVE', entity='CatalogItem', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_item(kw.get('item_id')), meta_keys=['status'])
def archive_item(item_id: int):
    session = get_db()
    item = session.execute(select(CatalogItem).where(CatalogItem.id==item_id)).scalar_one_or_none()
    if not item:
        abort(404)
    assert_branch_access(item.branch_id)
    if item.status == CatalogItem.STATUS_ARCHIVED:
        abort(400, description='Already archived')
    item.status = validate_status(CatalogItem.STATUS_ARCHIVED, CatalogItem.ALL_STATUSES)
    session.commit()
    return _item_json(item)

@cat_bp.post('/items/<int:item_id>/activate')
@require_permissions('CAT.MANAGE')
@audit_log('CAT.ITEM.ACTIVATE', entity='CatalogItem', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_item(kw.get('item_id')), meta_keys=['status'])
def activate_item(item_id: int):
    session = get_db()
    item = session.execute(select(CatalogItem).where(CatalogItem.id==item_id)).scalar_one_or_none()
    if not item:
        abort(404)
    assert_branch_access(item.branch_id)
    if item.status == CatalogItem.STATUS_ACTIVE:
        abort(400, description='Already active')
    item.status = validate_status(CatalogItem.STATUS_ACTIVE, CatalogItem.ALL_STATUSES)
    session.commit()
    return _item_json(item)

@cat_bp.route('/items/<int:item_id>', methods=['GET','HEAD'])
@require_permissions('CAT.READ')
def get_item(item_id: int):
    session = get_db()
    item = session.execute(select(CatalogItem).where(CatalogItem.id==item_id)).scalar_one_or_none()
    if not item:
        abort(404)
    assert_branch_access(item.branch_id)
    latest_ts = item.updated_at
    etag = compute_etag([item.id], 1, 1, 0, latest_ts.isoformat().replace('+00:00','Z') if latest_ts else '')
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    from flask import make_response, jsonify, request as _req
    body = _item_json(item)
    resp = make_response(jsonify(body))
    resp.headers['ETag'] = etag
    if latest_ts:
        lt = canonicalize_timestamp(latest_ts)
        resp.headers['Last-Modified'] = _http_date(lt)
        resp.headers['X-Last-Modified-ISO'] = lt.isoformat().replace('+00:00','Z')
    if _req.method == 'HEAD':
        resp.set_data(b'')
    return resp
