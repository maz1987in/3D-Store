from __future__ import annotations
from flask import Blueprint, request, abort
from flask_jwt_extended import get_jwt, get_jwt_identity
from sqlalchemy import select, func
from app.decorators.auth import require_permissions
from app.decorators.audit import audit_log
from app.utils.listing import make_cached_list_response, handle_conditional, apply_pagination, compute_etag, canonicalize_timestamp, _http_date
from app.utils.sorting import apply_multi_sort
from app.services.policy import assert_branch_access
from app.models.accounting_transaction import AccountingTransaction
from app.utils.validation import validate_status
from app.utils.fsm import TransitionValidator
from app import get_db

acc_bp = Blueprint('accounting', __name__)

TX_FSM = TransitionValidator({
    AccountingTransaction.STATUS_NEW: {AccountingTransaction.STATUS_APPROVED, AccountingTransaction.STATUS_REJECTED},
    AccountingTransaction.STATUS_APPROVED: {AccountingTransaction.STATUS_PAID},
    AccountingTransaction.STATUS_PAID: set(),
    AccountingTransaction.STATUS_REJECTED: set(),
})

def _tx_json(tx: AccountingTransaction):
    return {
        'id': tx.id,
        'branch_id': tx.branch_id,
        'description': tx.description,
        'amount_cents': tx.amount_cents,
        'status': tx.status
    }

@acc_bp.get('/transactions')
@require_permissions('ACC.READ')
def list_transactions():
    session = get_db()
    claims = get_jwt()
    q = session.query(AccountingTransaction)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(AccountingTransaction.branch_id.in_(branch_ids))
    status = request.args.get('status')
    if status:
        q = q.filter(AccountingTransaction.status==status)
    sort_expr = request.args.get('sort')
    allowed = {
        'status': AccountingTransaction.status,
        'amount_cents': AccountingTransaction.amount_cents,
        'updated_at': AccountingTransaction.updated_at,
        'id': AccountingTransaction.id
    }
    q = apply_multi_sort(q, sort_expr, allowed, AccountingTransaction.id)
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_tx_json(r) for r in rows]
    latest_ts = rows[0].updated_at if rows else None
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        return cond
    return resp

@acc_bp.route('/transactions', methods=['HEAD'])
@require_permissions('ACC.READ')
def head_transactions():
    session = get_db()
    claims = get_jwt()
    q = session.query(AccountingTransaction)
    branch_ids = claims.get('branch_ids') or []
    if branch_ids:
        q = q.filter(AccountingTransaction.branch_id.in_(branch_ids))
    sort_expr = request.args.get('sort')
    allowed = {
        'status': AccountingTransaction.status,
        'amount_cents': AccountingTransaction.amount_cents,
        'updated_at': AccountingTransaction.updated_at,
        'id': AccountingTransaction.id
    }
    q = apply_multi_sort(q, sort_expr, allowed, AccountingTransaction.id)
    paged_q, total, limit, offset = apply_pagination(q)
    rows = paged_q.all()
    rows_json = [_tx_json(r) for r in rows]
    latest_ts = rows[0].updated_at if rows else None
    if not rows:
        latest_ts = session.query(func.max(AccountingTransaction.updated_at)).scalar()
    resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    resp.set_data(b'')
    return resp

@acc_bp.post('/transactions')
@require_permissions('ACC.UPDATE')
@audit_log('ACC.TX.CREATE', entity='AccountingTransaction', entity_id_key='id', meta_keys=['status','branch_id','amount_cents'])
def create_transaction():
    session = get_db()
    data = request.json or {}
    description = data.get('description')
    branch_id = data.get('branch_id')
    amount_cents = data.get('amount_cents', 0)
    if not description or branch_id is None:
        abort(400, description='description and branch_id required')
    assert_branch_access(int(branch_id))
    try:
        amount_cents = int(amount_cents)
    except Exception:
        abort(400, description='amount_cents must be int')
    user_id = int(get_jwt_identity())
    tx = AccountingTransaction(description=description, branch_id=int(branch_id), amount_cents=amount_cents, created_by=user_id)
    session.add(tx)
    session.commit()
    return _tx_json(tx), 201

def _prefetch_tx(tx_id: int):
    session = get_db()
    return session.execute(select(AccountingTransaction).where(AccountingTransaction.id==tx_id)).scalar_one_or_none()

@acc_bp.post('/transactions/<int:tx_id>/approve')
@require_permissions('ACC.APPROVE')
@audit_log('ACC.TX.APPROVE', entity='AccountingTransaction', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_tx(kw.get('tx_id')), meta_keys=['status'])
def approve_transaction(tx_id: int):
    session = get_db()
    tx = session.execute(select(AccountingTransaction).where(AccountingTransaction.id==tx_id)).scalar_one_or_none()
    if not tx:
        abort(404)
    assert_branch_access(tx.branch_id)
    TX_FSM.assert_can_transition(tx.status, AccountingTransaction.STATUS_APPROVED)
    tx.status = validate_status(AccountingTransaction.STATUS_APPROVED, AccountingTransaction.ALL_STATUSES)
    session.commit()
    return _tx_json(tx)

@acc_bp.post('/transactions/<int:tx_id>/pay')
@require_permissions('ACC.PAY')
@audit_log('ACC.TX.PAY', entity='AccountingTransaction', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_tx(kw.get('tx_id')), meta_keys=['status'])
def pay_transaction(tx_id: int):
    session = get_db()
    tx = session.execute(select(AccountingTransaction).where(AccountingTransaction.id==tx_id)).scalar_one_or_none()
    if not tx:
        abort(404)
    assert_branch_access(tx.branch_id)
    TX_FSM.assert_can_transition(tx.status, AccountingTransaction.STATUS_PAID)
    tx.status = validate_status(AccountingTransaction.STATUS_PAID, AccountingTransaction.ALL_STATUSES)
    session.commit()
    return _tx_json(tx)

@acc_bp.post('/transactions/<int:tx_id>/reject')
@require_permissions('ACC.APPROVE')
@audit_log('ACC.TX.REJECT', entity='AccountingTransaction', entity_id_key='id', diff_keys=['status'], pre_fetch=lambda a, kw: _prefetch_tx(kw.get('tx_id')), meta_keys=['status'])
def reject_transaction(tx_id: int):
    session = get_db()
    tx = session.execute(select(AccountingTransaction).where(AccountingTransaction.id==tx_id)).scalar_one_or_none()
    if not tx:
        abort(404)
    assert_branch_access(tx.branch_id)
    TX_FSM.assert_can_transition(tx.status, AccountingTransaction.STATUS_REJECTED)
    tx.status = validate_status(AccountingTransaction.STATUS_REJECTED, AccountingTransaction.ALL_STATUSES)
    session.commit()
    return _tx_json(tx)

@acc_bp.route('/transactions/<int:tx_id>', methods=['GET','HEAD'])
@require_permissions('ACC.READ')
def get_transaction(tx_id: int):
    session = get_db()
    tx = session.execute(select(AccountingTransaction).where(AccountingTransaction.id==tx_id)).scalar_one_or_none()
    if not tx:
        abort(404)
    assert_branch_access(tx.branch_id)
    latest_ts = tx.updated_at
    etag = compute_etag([tx.id], 1, 1, 0, latest_ts.isoformat().replace('+00:00','Z') if latest_ts else '')
    cond = handle_conditional(etag, latest_ts)
    if cond:
        cond.set_data(b'')
        return cond
    from flask import make_response, jsonify, request as _req
    body = _tx_json(tx)
    resp = make_response(jsonify(body))
    resp.headers['ETag'] = etag
    if latest_ts:
        lt = canonicalize_timestamp(latest_ts)
        resp.headers['Last-Modified'] = _http_date(lt)
        resp.headers['X-Last-Modified-ISO'] = lt.isoformat().replace('+00:00','Z')
    if _req.method == 'HEAD':
        resp.set_data(b'')
    return resp
