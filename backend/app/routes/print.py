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
from app.models.print_job import PrintJob
from app.utils.validation import validate_status
from app.utils.fsm import TransitionValidator

print_bp = Blueprint('print', __name__)

PRINT_FSM = TransitionValidator({
    PrintJob.STATUS_QUEUED: {PrintJob.STATUS_STARTED},
    PrintJob.STATUS_STARTED: {PrintJob.STATUS_COMPLETED},
    PrintJob.STATUS_COMPLETED: set(),
})

@print_bp.get('/jobs')
@require_permissions('PRINT.READ')
def list_jobs():
    session = get_db()
    claims = get_jwt()
    q = session.query(PrintJob)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(PrintJob.branch_id.in_(branch_ids))
    sort_expr = request.args.get('sort')
    allowed = {
        'status': PrintJob.status,
        'updated_at': PrintJob.updated_at,
        'id': PrintJob.id
    }
    q = apply_multi_sort(q, sort_expr, allowed, PrintJob.id)
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_job_json(j) for j in rows]
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        return cond
    return resp

@print_bp.route('/jobs', methods=['HEAD'])
@require_permissions('PRINT.READ')
def head_jobs():
    session = get_db()
    claims = get_jwt()
    q = session.query(PrintJob)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(PrintJob.branch_id.in_(branch_ids))
    sort_expr = request.args.get('sort')
    allowed = {
        'status': PrintJob.status,
        'updated_at': PrintJob.updated_at,
        'id': PrintJob.id
    }
    q = apply_multi_sort(q, sort_expr, allowed, PrintJob.id)
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_job_json(j) for j in rows]
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    resp.set_data(b'')
    return resp

@print_bp.post('/jobs')
@require_permissions('PRINT.START')
@audit_log('PRINTJOB.CREATE', entity='PrintJob', entity_id_key='id', meta_keys=['status','branch_id','product_id'])
def create_job():
    session = get_db()
    data = request.json or {}
    branch_id = data.get('branch_id')
    product_id = data.get('product_id')
    if branch_id is None:
        abort(400, description='branch_id required')
    assert_branch_access(int(branch_id))
    user_id = int(get_jwt_identity())
    job = PrintJob(branch_id=int(branch_id), product_id=product_id, created_by=user_id)
    session.add(job)
    session.commit()
    return _job_json(job), 201

@print_bp.post('/jobs/<int:job_id>/start')
@require_permissions('PRINT.START')
@audit_log('PRINTJOB.START', entity='PrintJob', entity_id_key='id', diff_keys=['status','assigned_user_id'], pre_fetch=lambda a, kw: _prefetch_job(kw.get('job_id')), meta_keys=['status','assigned_user_id'])
def start_job(job_id: int):
    session = get_db()
    j = session.execute(select(PrintJob).where(PrintJob.id==job_id)).scalar_one_or_none()
    if not j:
        abort(404)
    assert_branch_access(j.branch_id)
    PRINT_FSM.assert_can_transition(j.status, PrintJob.STATUS_STARTED)
    j.status = validate_status(PrintJob.STATUS_STARTED, PrintJob.ALL_STATUSES)
    j.assigned_user_id = int(get_jwt_identity())
    session.commit()
    return _job_json(j)

@print_bp.post('/jobs/<int:job_id>/complete')
@require_permissions('PRINT.COMPLETE')
@audit_log('PRINTJOB.COMPLETE', entity='PrintJob', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_job(kw.get('job_id')), meta_keys=['status'])
def complete_job(job_id: int):
    session = get_db()
    j = session.execute(select(PrintJob).where(PrintJob.id==job_id)).scalar_one_or_none()
    if not j:
        abort(404)
    assert_branch_access(j.branch_id)
    PRINT_FSM.assert_can_transition(j.status, PrintJob.STATUS_COMPLETED)
    j.status = validate_status(PrintJob.STATUS_COMPLETED, PrintJob.ALL_STATUSES)
    session.commit()
    return _job_json(j)

@print_bp.route('/jobs/<int:job_id>', methods=['GET','HEAD'])
@require_permissions('PRINT.READ')
def get_job(job_id: int):
    session = get_db()
    j = session.execute(select(PrintJob).where(PrintJob.id==job_id)).scalar_one_or_none()
    if not j:
        abort(404)
    assert_branch_access(j.branch_id)
    latest_ts = j.updated_at
    etag = compute_etag([j.id], 1, 1, 0, latest_ts.isoformat().replace('+00:00','Z') if latest_ts else '')
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    from flask import make_response, jsonify, request as _req
    body = _job_json(j)
    resp = make_response(jsonify(body))
    resp.headers['ETag'] = etag
    if latest_ts:
        lt = canonicalize_timestamp(latest_ts)
        resp.headers['Last-Modified'] = _http_date(lt)
        resp.headers['X-Last-Modified-ISO'] = lt.isoformat().replace('+00:00','Z')
    if _req.method == 'HEAD':
        resp.set_data(b'')
    return resp

def _job_json(j: PrintJob):
    return {
        'id': j.id,
        'branch_id': j.branch_id,
        'product_id': j.product_id,
        'status': j.status,
        'assigned_user_id': j.assigned_user_id
    }

def _prefetch_job(job_id: int):
    from sqlalchemy import select
    session = get_db()
    j = session.execute(select(PrintJob).where(PrintJob.id==job_id)).scalar_one_or_none()
    if not j:
        return {}
    return {'status': j.status, 'assigned_user_id': j.assigned_user_id}
