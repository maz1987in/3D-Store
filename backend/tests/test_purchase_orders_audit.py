import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import get_db
from tests.test_utils_seed import ensure_user, ensure_permissions
from app.models.audit import AuditLog

@pytest.fixture()
def app_context(app_instance):
    with app_instance.app_context():
        yield app_instance


def _auth_headers(user_id: int, perms):
    token = create_access_token(identity=str(user_id), additional_claims={
        'perms': perms,
        'roles': [],
        'groups': [],
        'branch_ids': [1]
    })
    return {'Authorization': f'Bearer {token}'}


def test_po_audit_entries(app_context: Flask):
    perms = ['PO.READ','PO.CREATE','PO.RECEIVE','PO.CLOSE']
    ensure_permissions(perms)
    user = ensure_user('po_audit@example.com')
    headers = _auth_headers(user.id, perms)
    client = app_context.test_client()
    # Create
    resp = client.post('/po/purchase-orders', json={'vendor_name':'Auditor','branch_id':1,'total_cents':10}, headers=headers)
    assert resp.status_code == 201
    po_id = resp.get_json()['id']
    # Receive
    resp = client.post(f'/po/purchase-orders/{po_id}/receive', headers=headers)
    assert resp.status_code == 200
    # Close
    resp = client.post(f'/po/purchase-orders/{po_id}/close', headers=headers)
    assert resp.status_code == 200
    # Query audits
    session = get_db()
    entries = session.query(AuditLog).filter(
        AuditLog.action.in_(['PO.CREATE','PO.RECEIVE','PO.CLOSE']),
        AuditLog.actor_user_id == user.id
    ).all()
    actions = {e.action for e in entries}
    assert {'PO.CREATE','PO.RECEIVE','PO.CLOSE'} <= actions
    # Basic shape checks
    for e in entries:
        assert e.actor_user_id == user.id
        assert e.entity == 'PurchaseOrder'
        # entity_id stored as string in audit table
        assert int(e.entity_id) == po_id
