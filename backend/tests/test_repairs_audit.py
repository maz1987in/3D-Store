import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from tests.test_utils_seed import ensure_user, ensure_permissions
from app import get_db
from app.models.audit import AuditLog

PERMS = ['RPR.READ','RPR.MANAGE']
ACTIONS = ['RPR.TICKET.CREATE','RPR.TICKET.START','RPR.TICKET.COMPLETE','RPR.TICKET.CLOSE','RPR.TICKET.CANCEL']

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


def test_repairs_audit_entries(app_context: Flask):
    ensure_permissions(PERMS)
    user = ensure_user('repairs_audit@example.com')
    headers = _auth_headers(user.id, PERMS)
    client = app_context.test_client()
    # Create
    resp = client.post('/repairs/tickets', json={'customer_name':'Aud','device_type':'Printer','issue_summary':'X','branch_id':1}, headers=headers)
    assert resp.status_code == 201
    tid = resp.get_json()['id']
    # Start
    client.post(f'/repairs/tickets/{tid}/start', headers=headers)
    # Complete
    client.post(f'/repairs/tickets/{tid}/complete', headers=headers)
    # Close
    client.post(f'/repairs/tickets/{tid}/close', headers=headers)
    # Cancel is not valid after close; create another to exercise cancel
    resp = client.post('/repairs/tickets', json={'customer_name':'Aud2','device_type':'Printer','issue_summary':'Y','branch_id':1}, headers=headers)
    tid2 = resp.get_json()['id']
    client.post(f'/repairs/tickets/{tid2}/cancel', headers=headers)

    session = get_db()
    entries = session.query(AuditLog).filter(
        AuditLog.action.in_(ACTIONS),
        AuditLog.actor_user_id == user.id
    ).all()
    present = {e.action for e in entries}
    # All defined lifecycle actions should appear at least once
    assert set(ACTIONS) <= present
    for e in entries:
        assert e.actor_user_id == user.id
        assert e.entity == 'RepairTicket'
        assert e.entity_id is not None
