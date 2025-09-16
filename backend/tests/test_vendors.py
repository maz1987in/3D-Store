import pytest
from flask import Flask
from tests.test_utils_seed import ensure_permissions, ensure_user
from tests.test_lifecycle_helpers import jwt_headers

BASE_PERMS = [
    'PO.VENDOR.READ','PO.VENDOR.CREATE','PO.VENDOR.UPDATE','PO.VENDOR.ACTIVATE','PO.VENDOR.DEACTIVATE'
]

@pytest.fixture()
def app_context(app_instance):
    with app_instance.app_context():
        yield app_instance

def _auth_headers(user_id: int, perms=None):
    perms = perms or BASE_PERMS
    return jwt_headers(user_id, perms)

def seed_vendor_user():
    ensure_permissions(BASE_PERMS)
    return ensure_user('vendor_user@example.com')


def test_vendor_crud_and_status_flow(app_context: Flask):
    client = app_context.test_client()
    u = seed_vendor_user()
    headers = _auth_headers(u.id)
    # Create
    resp = client.post('/po/vendors', json={'name': 'Alpha Supplies', 'branch_id': 1, 'contact_email': 'alpha@example.com'}, headers=headers)
    assert resp.status_code == 201
    vendor = resp.get_json()
    vid = vendor['id']
    assert vendor['status'] == 'ACTIVE'
    # Update
    resp = client.put(f'/po/vendors/{vid}', json={'name': 'Alpha Supplies Co', 'contact_email': 'sales@alpha.example'}, headers=headers)
    assert resp.status_code == 200
    updated = resp.get_json()
    assert updated['name'] == 'Alpha Supplies Co'
    # Deactivate
    resp = client.post(f'/po/vendors/{vid}/deactivate', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'INACTIVE'
    # Activate
    resp = client.post(f'/po/vendors/{vid}/activate', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'ACTIVE'


def test_vendor_list_and_head_validators(app_context: Flask):
    client = app_context.test_client()
    u = seed_vendor_user()
    headers = _auth_headers(u.id)
    # Create one to ensure validators present
    client.post('/po/vendors', json={'name': 'Validator Vendor', 'branch_id': 1}, headers=headers)
    head_resp = client.head('/po/vendors', headers=headers)
    assert head_resp.status_code in (200, 304)
    if head_resp.status_code == 200:
        assert 'ETag' in head_resp.headers
        if 'Last-Modified' in head_resp.headers:
            assert 'X-Last-Modified-ISO' in head_resp.headers
    list_resp = client.get('/po/vendors', headers=headers)
    assert list_resp.status_code == 200
    data = list_resp.get_json()['data']
    assert any(v['name'] == 'Validator Vendor' for v in data)


def test_vendor_permission_enforcement(app_context: Flask):
    client = app_context.test_client()
    # Only READ permission
    ensure_permissions(['PO.VENDOR.READ'])
    user = ensure_user('vendor_read_only@example.com')
    headers = _auth_headers(user.id, ['PO.VENDOR.READ'])
    # List allowed
    resp = client.get('/po/vendors', headers=headers)
    assert resp.status_code in (200, 204, 304)
    # Create forbidden
    resp_c = client.post('/po/vendors', json={'name': 'ShouldFail', 'branch_id': 1}, headers=headers)
    assert resp_c.status_code == 403
    # Activate forbidden
    resp_a = client.post('/po/vendors/999/activate', headers=headers)
    assert resp_a.status_code == 403


def test_vendor_not_found_and_validation_errors(app_context: Flask):
    client = app_context.test_client()
    u = seed_vendor_user()
    headers = _auth_headers(u.id)
    # Not found get
    resp = client.get('/po/vendors/99999', headers=headers)
    assert resp.status_code == 404
    # Create invalid (missing name)
    bad = client.post('/po/vendors', json={'branch_id': 1}, headers=headers)
    assert bad.status_code == 400
    # Deactivate non-existent
    resp_d = client.post('/po/vendors/99999/deactivate', headers=headers)
    assert resp_d.status_code == 404
