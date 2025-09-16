import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from tests.test_utils_seed import ensure_permissions, ensure_user
from tests.test_lifecycle_helpers import jwt_headers, exercise_purchase_order_lifecycle


@pytest.fixture()
def app_context(app_instance):
    with app_instance.app_context():
        yield app_instance


PERMS = ['PO.READ','PO.CREATE','PO.RECEIVE','PO.CLOSE']

def seed_po_user():
    ensure_permissions(PERMS)
    return ensure_user('po_user@example.com')

def _auth_headers(user_id: int):
    return jwt_headers(user_id, PERMS)


def test_purchase_order_lifecycle(app_context: Flask):
    client = app_context.test_client()
    u = seed_po_user()
    headers = _auth_headers(u.id)
    exercise_purchase_order_lifecycle(client, headers)


def test_purchase_order_invalid_transitions(app_context: Flask):
    client = app_context.test_client()
    u = seed_po_user()
    headers = _auth_headers(u.id)
    resp = client.post('/po/purchase-orders', json={'vendor_name': 'Supplier', 'branch_id': 1, 'total_cents': 1000}, headers=headers)
    po_id = resp.get_json()['id']
    # Close before receive
    resp = client.post(f'/po/purchase-orders/{po_id}/close', headers=headers)
    assert resp.status_code == 400
    # Receive
    resp = client.post(f'/po/purchase-orders/{po_id}/receive', headers=headers)
    assert resp.status_code == 200
    # Receive again invalid
    resp = client.post(f'/po/purchase-orders/{po_id}/receive', headers=headers)
    assert resp.status_code == 400