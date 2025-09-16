import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from tests.test_utils_seed import ensure_user, ensure_permissions

READ_ONLY = ['RPR.READ']

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


def test_repair_ticket_missing_manage(app_context: Flask):
    client = app_context.test_client()
    ensure_permissions(READ_ONLY)
    user = ensure_user('repairs_readonly@example.com')
    headers = _auth_headers(user.id, READ_ONLY)
    # Attempt create without manage
    resp = client.post('/repairs/tickets', json={'customer_name':'No','device_type':'Device','issue_summary':'Issue','branch_id':1}, headers=headers)
    assert resp.status_code == 403
