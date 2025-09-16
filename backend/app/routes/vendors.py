from __future__ import annotations
from flask import Blueprint, request, abort
from flask_jwt_extended import get_jwt, get_jwt_identity
from sqlalchemy import select
from app import get_db
from app.models.vendor import Vendor
from app.decorators.auth import require_permissions
from app.decorators.audit import audit_log
from app.services.policy import assert_branch_access
from app.utils.listing import apply_pagination, handle_conditional, make_cached_list_response, compute_etag, canonicalize_timestamp, _http_date
from app.utils.filters import apply_filters
from app.utils.validation import validate_status
from app.utils.sorting import apply_multi_sort
from app.utils.listing import handle_conditional

vendors_bp = Blueprint('vendors', __name__)


@vendors_bp.get('/vendors')
@require_permissions('PO.VENDOR.READ')
def list_vendors():
    session = get_db()
    claims = get_jwt()
    q = session.query(Vendor)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(Vendor.branch_id.in_(branch_ids))
    filter_specs = {
        'name': {'op': lambda qu, v: qu.filter(Vendor.name.ilike(f'%{v}%'))},
        'status': {'op': lambda qu, v: qu.filter(Vendor.status==v), 'validate': lambda v: v in Vendor.ALL_STATUSES},
        'branch_id': {'coerce': int, 'op': lambda qu, v: qu.filter(Vendor.branch_id==v) if (not branch_ids or v in branch_ids) else qu.filter(Vendor.id==0)}
    }
    q = apply_filters(q, filter_specs, request.args)
    sort_expr = request.args.get('sort')
    allowed = {
        'name': Vendor.name,
        'status': Vendor.status,
        'updated_at': Vendor.updated_at,
        'id': Vendor.id
    }
    q = apply_multi_sort(q, sort_expr, allowed, Vendor.id)
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_vendor_json(v) for v in rows]
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        return cond
    return resp


@vendors_bp.route('/vendors', methods=['HEAD'])
@require_permissions('PO.VENDOR.READ')
def head_vendors():
    session = get_db()
    claims = get_jwt()
    q = session.query(Vendor)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(Vendor.branch_id.in_(branch_ids))
    filter_specs = {
        'name': {'op': lambda qu, v: qu.filter(Vendor.name.ilike(f'%{v}%'))},
        'status': {'op': lambda qu, v: qu.filter(Vendor.status==v), 'validate': lambda v: v in Vendor.ALL_STATUSES},
        'branch_id': {'coerce': int, 'op': lambda qu, v: qu.filter(Vendor.branch_id==v) if (not branch_ids or v in branch_ids) else qu.filter(Vendor.id==0)}
    }
    q = apply_filters(q, filter_specs, request.args)
    sort_expr = request.args.get('sort')
    allowed = {
        'name': Vendor.name,
        'status': Vendor.status,
        'updated_at': Vendor.updated_at,
        'id': Vendor.id
    }
    q = apply_multi_sort(q, sort_expr, allowed, Vendor.id)
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_vendor_json(v) for v in rows]
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    resp.set_data(b'')
    return resp


@vendors_bp.post('/vendors')
@require_permissions('PO.VENDOR.CREATE')
@audit_log('VENDOR.CREATE', entity='Vendor', entity_id_key='id', meta_keys=['name','contact_email'])
def create_vendor():
    session = get_db()
    data = request.json or {}
    name = data.get('name'); branch_id = data.get('branch_id'); contact_email = data.get('contact_email')
    if not name or branch_id is None:
        abort(400, description='name and branch_id required')
    assert_branch_access(int(branch_id))
    if session.execute(select(Vendor).where(Vendor.name==name)).scalar_one_or_none():
        abort(400, description='vendor name exists')
    user_id = int(get_jwt_identity())
    v = Vendor(name=name, branch_id=int(branch_id), contact_email=contact_email, created_by=user_id)
    session.add(v); session.commit()
    return _vendor_json(v), 201


@vendors_bp.route('/vendors/<int:vendor_id>', methods=['GET','HEAD'])
@require_permissions('PO.VENDOR.READ')
def get_vendor(vendor_id: int):
    session = get_db()
    v = session.execute(select(Vendor).where(Vendor.id==vendor_id)).scalar_one_or_none()
    if not v:
        abort(404)
    assert_branch_access(v.branch_id)
    latest_ts = v.updated_at
    seed = f"[{v.id}]|1|1|0|{latest_ts.isoformat() if latest_ts else ''}"
    etag = compute_etag([v.id], 1, 1, 0, latest_ts.isoformat().replace('+00:00','Z') if latest_ts else '')
    cond = handle_conditional(etag, latest_ts)
    if cond:
        # ensure empty body for HEAD 304
        cond.set_data(b'')
        return cond
    from flask import make_response, jsonify, request as _req
    body = _vendor_json(v)
    resp = make_response(jsonify(body))
    resp.headers['ETag'] = etag
    if latest_ts:
        lt = canonicalize_timestamp(latest_ts)
        resp.headers['Last-Modified'] = _http_date(lt)
        resp.headers['X-Last-Modified-ISO'] = lt.isoformat().replace('+00:00','Z')
    if _req.method == 'HEAD':
        resp.set_data(b'')
    return resp


@vendors_bp.put('/vendors/<int:vendor_id>')
@require_permissions('PO.VENDOR.UPDATE')
@audit_log('VENDOR.UPDATE', entity='Vendor', entity_id_key='id', diff_keys=['name','contact_email'], pre_fetch=lambda a, kw: _prefetch_vendor(kw.get('vendor_id')), meta_keys=['name','contact_email'])
def update_vendor(vendor_id: int):
    session = get_db()
    v = session.execute(select(Vendor).where(Vendor.id==vendor_id)).scalar_one_or_none()
    if not v:
        abort(404)
    assert_branch_access(v.branch_id)
    data = request.json or {}
    if 'name' in data:
        if not data['name']:
            abort(400, description='name cannot be empty')
        # uniqueness check
        dup = session.execute(select(Vendor).where(Vendor.name==data['name'], Vendor.id!=v.id)).scalar_one_or_none()
        if dup:
            abort(400, description='vendor name exists')
        v.name = data['name']
    if 'contact_email' in data:
        v.contact_email = data['contact_email']
    session.commit(); return _vendor_json(v)


@vendors_bp.post('/vendors/<int:vendor_id>/activate')
@require_permissions('PO.VENDOR.ACTIVATE')
@audit_log('VENDOR.ACTIVATE', entity='Vendor', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_vendor(kw.get('vendor_id')), meta_keys=['status'])
def activate_vendor(vendor_id: int):
    session = get_db()
    v = session.execute(select(Vendor).where(Vendor.id==vendor_id)).scalar_one_or_none()
    if not v:
        abort(404)
    assert_branch_access(v.branch_id)
    if v.status == Vendor.STATUS_ACTIVE:
        abort(400, description='already active')
    v.status = validate_status(Vendor.STATUS_ACTIVE, Vendor.ALL_STATUSES, 'status')
    session.commit(); return _vendor_json(v)


@vendors_bp.post('/vendors/<int:vendor_id>/deactivate')
@require_permissions('PO.VENDOR.DEACTIVATE')
@audit_log('VENDOR.DEACTIVATE', entity='Vendor', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_vendor(kw.get('vendor_id')), meta_keys=['status'])
def deactivate_vendor(vendor_id: int):
    session = get_db()
    v = session.execute(select(Vendor).where(Vendor.id==vendor_id)).scalar_one_or_none()
    if not v:
        abort(404)
    assert_branch_access(v.branch_id)
    if v.status == Vendor.STATUS_INACTIVE:
        abort(400, description='already inactive')
    v.status = validate_status(Vendor.STATUS_INACTIVE, Vendor.ALL_STATUSES, 'status')
    session.commit(); return _vendor_json(v)


def _vendor_json(v: Vendor):
    return {
        'id': v.id,
        'branch_id': v.branch_id,
        'name': v.name,
        'contact_email': v.contact_email,
        'status': v.status
    }


def _prefetch_vendor(vendor_id: int):
    session = get_db()
    v = session.execute(select(Vendor).where(Vendor.id==vendor_id)).scalar_one_or_none()
    if not v:
        return {}
    return {'name': v.name, 'contact_email': v.contact_email, 'status': v.status}