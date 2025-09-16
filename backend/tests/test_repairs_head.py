import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from tests.test_utils_seed import ensure_user, ensure_permissions

PERMS = ['RPR.READ','RPR.MANAGE']

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


def test_repairs_head_validators(app_context: Flask):
    client = app_context.test_client()
    ensure_permissions(PERMS)
    user = ensure_user('repairs_head@example.com')
    headers = _auth_headers(user.id, PERMS)
    # create one ticket so Last-Modified appears
    resp = client.post('/repairs/tickets', json={'customer_name':'Head','device_type':'Printer','issue_summary':'Test','branch_id':1}, headers=headers)
    assert resp.status_code == 201
    # HEAD request
    resp = client.head('/repairs/tickets', headers=headers)
    assert resp.status_code in (200, 304)
    assert resp.data in (b'', None)
    assert 'ETag' in resp.headers
    if resp.status_code == 200:
        # With at least one record, expect Last-Modified headers
        assert 'Last-Modified' in resp.headers
        assert 'X-Last-Modified-ISO' in resp.headers
