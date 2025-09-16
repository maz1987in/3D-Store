from __future__ import annotations
from flask import Blueprint, request, abort
from flask_jwt_extended import get_jwt, get_jwt_identity
from sqlalchemy import select
from app.decorators.auth import require_permissions
from app.decorators.audit import audit_log
from app.utils.listing import make_cached_list_response, handle_conditional, apply_pagination, compute_etag, canonicalize_timestamp, _http_date
from app.utils.sorting import apply_multi_sort
from app.services.policy import assert_branch_access
from app import get_db
from app.models.repair_ticket import RepairTicket
from app.utils.validation import validate_status
from app.utils.fsm import TransitionValidator

rpr_bp = Blueprint('repairs', __name__)

REPAIRS_FSM = TransitionValidator({
    RepairTicket.STATUS_NEW: {RepairTicket.STATUS_IN_PROGRESS, RepairTicket.STATUS_CANCELLED},
    RepairTicket.STATUS_IN_PROGRESS: {RepairTicket.STATUS_COMPLETED, RepairTicket.STATUS_CANCELLED},
    RepairTicket.STATUS_COMPLETED: {RepairTicket.STATUS_CLOSED},
    RepairTicket.STATUS_CANCELLED: {RepairTicket.STATUS_CLOSED},
    RepairTicket.STATUS_CLOSED: set(),
})

@rpr_bp.get('/tickets')
@require_permissions('RPR.READ')
def list_tickets():
    session = get_db()
    claims = get_jwt()
    q = session.query(RepairTicket)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(RepairTicket.branch_id.in_(branch_ids))
    # basic filters
    customer = request.args.get('customer_name')
    status = request.args.get('status')
    if customer:
        q = q.filter(RepairTicket.customer_name.ilike(f"%{customer}%"))
    if status:
        q = q.filter(RepairTicket.status==status)
    sort_expr = request.args.get('sort')
    allowed = {
        'customer_name': RepairTicket.customer_name,
        'status': RepairTicket.status,
        'updated_at': RepairTicket.updated_at,
        'id': RepairTicket.id
    }
    q = apply_multi_sort(q, sort_expr, allowed, RepairTicket.id)
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_ticket_json(t) for t in rows]
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        return cond
    return resp

@rpr_bp.route('/tickets', methods=['HEAD'])
@require_permissions('RPR.READ')
def head_tickets():
    session = get_db()
    claims = get_jwt()
    q = session.query(RepairTicket)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(RepairTicket.branch_id.in_(branch_ids))
    sort_expr = request.args.get('sort')
    allowed = {
        'customer_name': RepairTicket.customer_name,
        'status': RepairTicket.status,
        'updated_at': RepairTicket.updated_at,
        'id': RepairTicket.id
    }
    q = apply_multi_sort(q, sort_expr, allowed, RepairTicket.id)
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_ticket_json(t) for t in rows]
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    resp.set_data(b'')
    return resp


@rpr_bp.post('/tickets')
@require_permissions('RPR.MANAGE')
@audit_log('RPR.TICKET.CREATE', entity='RepairTicket', entity_id_key='id', meta_keys=['customer_name','device_type','status'])
def create_ticket():
    session = get_db()
    data = request.json or {}
    customer_name = data.get('customer_name')
    device_type = data.get('device_type')
    issue_summary = data.get('issue_summary')
    branch_id = data.get('branch_id')
    if not all([customer_name, device_type, issue_summary]) or branch_id is None:
        abort(400, description='customer_name, device_type, issue_summary, branch_id required')
    assert_branch_access(int(branch_id))
    user_id = int(get_jwt_identity())
    t = RepairTicket(customer_name=customer_name, device_type=device_type, issue_summary=issue_summary, branch_id=int(branch_id), created_by=user_id)
    session.add(t)
    session.commit()
    return _ticket_json(t), 201


@rpr_bp.post('/tickets/<int:ticket_id>/start')
@require_permissions('RPR.MANAGE')
@audit_log('RPR.TICKET.START', entity='RepairTicket', entity_id_key='id', diff_keys=['status','assigned_user_id'], pre_fetch=lambda a, kw: _prefetch_ticket(kw.get('ticket_id')), meta_keys=['status','assigned_user_id'])
def start_ticket(ticket_id: int):
    session = get_db()
    t = session.execute(select(RepairTicket).where(RepairTicket.id==ticket_id)).scalar_one_or_none()
    if not t:
        abort(404)
    assert_branch_access(t.branch_id)
    REPAIRS_FSM.assert_can_transition(t.status, RepairTicket.STATUS_IN_PROGRESS)
    t.status = validate_status(RepairTicket.STATUS_IN_PROGRESS, RepairTicket.ALL_STATUSES)
    t.assigned_user_id = int(get_jwt_identity())
    session.commit()
    return _ticket_json(t)


@rpr_bp.post('/tickets/<int:ticket_id>/complete')
@require_permissions('RPR.MANAGE')
@audit_log('RPR.TICKET.COMPLETE', entity='RepairTicket', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_ticket(kw.get('ticket_id')), meta_keys=['status'])
def complete_ticket(ticket_id: int):
    session = get_db()
    t = session.execute(select(RepairTicket).where(RepairTicket.id==ticket_id)).scalar_one_or_none()
    if not t:
        abort(404)
    assert_branch_access(t.branch_id)
    REPAIRS_FSM.assert_can_transition(t.status, RepairTicket.STATUS_COMPLETED)
    t.status = validate_status(RepairTicket.STATUS_COMPLETED, RepairTicket.ALL_STATUSES)
    session.commit()
    return _ticket_json(t)


@rpr_bp.post('/tickets/<int:ticket_id>/close')
@require_permissions('RPR.MANAGE')
@audit_log('RPR.TICKET.CLOSE', entity='RepairTicket', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_ticket(kw.get('ticket_id')), meta_keys=['status'])
def close_ticket(ticket_id: int):
    session = get_db()
    t = session.execute(select(RepairTicket).where(RepairTicket.id==ticket_id)).scalar_one_or_none()
    if not t:
        abort(404)
    assert_branch_access(t.branch_id)
    REPAIRS_FSM.assert_can_transition(t.status, RepairTicket.STATUS_CLOSED)
    t.status = validate_status(RepairTicket.STATUS_CLOSED, RepairTicket.ALL_STATUSES)
    session.commit()
    return _ticket_json(t)


@rpr_bp.post('/tickets/<int:ticket_id>/cancel')
@require_permissions('RPR.MANAGE')
@audit_log('RPR.TICKET.CANCEL', entity='RepairTicket', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_ticket(kw.get('ticket_id')), meta_keys=['status'])
def cancel_ticket(ticket_id: int):
    session = get_db()
    t = session.execute(select(RepairTicket).where(RepairTicket.id==ticket_id)).scalar_one_or_none()
    if not t:
        abort(404)
    assert_branch_access(t.branch_id)
    REPAIRS_FSM.assert_can_transition(t.status, RepairTicket.STATUS_CANCELLED)
    t.status = validate_status(RepairTicket.STATUS_CANCELLED, RepairTicket.ALL_STATUSES)
    session.commit()
    return _ticket_json(t)

@rpr_bp.route('/tickets/<int:ticket_id>', methods=['GET','HEAD'])
@require_permissions('RPR.READ')
def get_ticket(ticket_id: int):
    session = get_db()
    t = session.execute(select(RepairTicket).where(RepairTicket.id==ticket_id)).scalar_one_or_none()
    if not t:
        abort(404)
    assert_branch_access(t.branch_id)
    latest_ts = t.updated_at
    etag = compute_etag([t.id], 1, 1, 0, latest_ts.isoformat().replace('+00:00','Z') if latest_ts else '')
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    from flask import make_response, jsonify, request as _req
    body = _ticket_json(t)
    resp = make_response(jsonify(body))
    resp.headers['ETag'] = etag
    if latest_ts:
        lt = canonicalize_timestamp(latest_ts)
        resp.headers['Last-Modified'] = _http_date(lt)
        resp.headers['X-Last-Modified-ISO'] = lt.isoformat().replace('+00:00','Z')
    if _req.method == 'HEAD':
        resp.set_data(b'')
    return resp


def _ticket_json(t: RepairTicket):
    return {
        'id': t.id,
        'branch_id': t.branch_id,
        'customer_name': t.customer_name,
        'device_type': t.device_type,
        'issue_summary': t.issue_summary,
        'status': t.status,
        'assigned_user_id': t.assigned_user_id
    }


def _prefetch_ticket(ticket_id: int):
    from sqlalchemy import select
    session = get_db()
    t = session.execute(select(RepairTicket).where(RepairTicket.id==ticket_id)).scalar_one_or_none()
    if not t:
        return {}
    return {'status': t.status, 'assigned_user_id': t.assigned_user_id}
