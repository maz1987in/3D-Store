import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import get_db
from tests.test_utils_seed import ensure_user, ensure_permissions

# Helpers

def seed_po_user_with_perms(perms):
    ensure_permissions(perms)
    return ensure_user('po_negative@example.com')

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


def test_po_missing_receive_permission(app_context: Flask):
    client = app_context.test_client()
    # User has create + read only
    user = seed_po_user_with_perms(['PO.READ','PO.CREATE'])
    headers = _auth_headers(user.id, ['PO.READ','PO.CREATE'])
    # Create PO
    resp = client.post('/po/purchase-orders', json={'vendor_name':'V1','branch_id':1,'total_cents':100}, headers=headers)
    assert resp.status_code == 201, resp.get_json()
    po_id = resp.get_json()['id']
    # Attempt receive without perm
    resp = client.post(f'/po/purchase-orders/{po_id}/receive', headers=headers)
    assert resp.status_code == 403


def test_po_missing_close_permission(app_context: Flask):
    client = app_context.test_client()
    # User has create + receive
    user = seed_po_user_with_perms(['PO.READ','PO.CREATE','PO.RECEIVE'])
    headers = _auth_headers(user.id, ['PO.READ','PO.CREATE','PO.RECEIVE'])
    # Create
    resp = client.post('/po/purchase-orders', json={'vendor_name':'V2','branch_id':1,'total_cents':50}, headers=headers)
    po_id = resp.get_json()['id']
    # Receive (allowed)
    resp = client.post(f'/po/purchase-orders/{po_id}/receive', headers=headers)
    assert resp.status_code == 200
    # Close without PO.CLOSE perm
    resp = client.post(f'/po/purchase-orders/{po_id}/close', headers=headers)
    assert resp.status_code == 403
