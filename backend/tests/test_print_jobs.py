from __future__ import annotations
import pytest
from flask import Flask
from app import create_app, get_db
from tests.test_utils_seed import ensure_permissions, ensure_user, ensure_role, ensure_user_role_assignment
from tests.test_lifecycle_helpers import exercise_print_job_lifecycle


@pytest.fixture()
def app_context(app_instance):
    # Reuse session-scoped app with in-memory DB already initialized
    with app_instance.app_context():
        yield app_instance


def _auth_headers(client, email="printer@example.com"):
    resp = client.post('/iam/auth/login', json={'email': email, 'password': 'pw'})
    assert resp.status_code == 200
    token = resp.json['access_token']
    return {'Authorization': f'Bearer {token}'}


def seed_printer_user():
    session = get_db()
    perms = ['PRINT.READ', 'PRINT.START', 'PRINT.COMPLETE']
    ensure_permissions(perms)
    role = ensure_role('PrinterLifecycle', perms)
    user = ensure_user('printer@example.com')
    ensure_user_role_assignment(user, role)
    session.commit()


def test_print_job_lifecycle(app_context: Flask):
    client = app_context.test_client()
    seed_printer_user()
    headers = _auth_headers(client)
    exercise_print_job_lifecycle(client, headers)
    # Wrong extra completion attempt
    # Last job id retrieval requires re-create or adapt helper; simply attempt complete on latest created job
    # Re-create to test invalid transition
    resp = client.post('/print/jobs', json={'branch_id': 1, 'product_id': None}, headers=headers)
    jid = resp.json['id']
    # Start then complete once
    client.post(f'/print/jobs/{jid}/start', headers=headers)
    client.post(f'/print/jobs/{jid}/complete', headers=headers)
    # Second completion invalid
    resp = client.post(f'/print/jobs/{jid}/complete', headers=headers)
    assert resp.status_code == 400


def test_print_job_wrong_transition(app_context: Flask):
    client = app_context.test_client()
    seed_printer_user()
    headers = _auth_headers(client)
    resp = client.post('/print/jobs', json={'branch_id': 1}, headers=headers)
    job_id = resp.json['id']
    resp = client.post(f'/print/jobs/{job_id}/complete', headers=headers)
    assert resp.status_code == 400