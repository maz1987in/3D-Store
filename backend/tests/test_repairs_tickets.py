import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from tests.test_utils_seed import ensure_user, ensure_permissions
from tests.test_lifecycle_helpers import jwt_headers, exercise_repair_ticket_lifecycle

PERMS = ['RPR.READ','RPR.MANAGE']

@pytest.fixture()
def app_context(app_instance):
    with app_instance.app_context():
        yield app_instance

def _auth_headers(user_id: int, perms):
    return jwt_headers(user_id, perms)


def seed_repair_user():
    ensure_permissions(PERMS)
    return ensure_user('repairs@example.com')


def test_repair_ticket_lifecycle(app_context: Flask):
    client = app_context.test_client()
    user = seed_repair_user()
    headers = _auth_headers(user.id, PERMS)
    exercise_repair_ticket_lifecycle(client, headers)


def test_repair_ticket_invalid_transitions(app_context: Flask):
    client = app_context.test_client()
    user = seed_repair_user()
    headers = _auth_headers(user.id, PERMS)
    resp = client.post('/repairs/tickets', json={'customer_name':'Bob','device_type':'Scanner','issue_summary':'Noise','branch_id':1}, headers=headers)
    tid = resp.get_json()['id']
    # Complete before start
    resp = client.post(f'/repairs/tickets/{tid}/complete', headers=headers)
    assert resp.status_code == 400
    # Close before complete
    resp = client.post(f'/repairs/tickets/{tid}/close', headers=headers)
    assert resp.status_code == 400
    # Cancel valid from NEW
    resp = client.post(f'/repairs/tickets/{tid}/cancel', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'CANCELLED'
    # Start after cancel invalid
    resp = client.post(f'/repairs/tickets/{tid}/start', headers=headers)
    assert resp.status_code == 400
    # Close after cancel valid? Should be allowed because cancel sets CANCELLED -> close allowed
    resp = client.post(f'/repairs/tickets/{tid}/close', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'CLOSED'
