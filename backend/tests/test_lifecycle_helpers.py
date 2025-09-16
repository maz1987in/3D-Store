"""Reusable test helpers for lifecycle-based services to reduce duplication.

Patterns unified:
 - Auth header creation using direct JWT claims (when bypassing /login) or login based (print jobs use login).
 - Creation + transition sequencing with assertion helpers.
 - Error transition assertion.

Services adopting these helpers should keep their existing focused tests lightweight.
"""
from __future__ import annotations
from typing import Dict, List, Callable
from flask_jwt_extended import create_access_token
from tests.test_utils_seed import ensure_permissions, ensure_user, ensure_role, ensure_user_role_assignment
from app import get_db

# ---------- Generic Auth Helpers ---------- #

def jwt_headers(user_id: int, perms: List[str]):
    token = create_access_token(identity=str(user_id), additional_claims={
        'perms': perms,
        'roles': [],
        'groups': [],
        'branch_ids': [1]
    })
    return {'Authorization': f'Bearer {token}'}


def seed_user_with_perms(email: str, perms: List[str], role_name: str = None):
    """Ensure permissions & user; optionally attach via a role if role_name provided.

    For services exercising role-based permission resolution (e.g., print), providing a role
    maintains closer parity with production resolution.
    """
    session = get_db()
    ensure_permissions(perms)
    user = ensure_user(email)
    if role_name:
        role = ensure_role(role_name, perms)
        ensure_user_role_assignment(user, role)
    session.commit()
    return user

# ---------- Assertion Helpers ---------- #

def assert_transition(client, url: str, headers: Dict[str,str], expected_status: int, expected_body_key: str = 'status', expected_body_value: str = None):
    resp = client.post(url, headers=headers)
    assert resp.status_code == expected_status, resp.get_json()
    if expected_status < 400 and expected_body_value is not None:
        body = resp.get_json()
        assert body[expected_body_key] == expected_body_value
    return resp


def create_resource_and_assert(client, url: str, payload: dict, headers: Dict[str,str], expected_status_field: str = 'status', expected_initial_status: str = None):
    resp = client.post(url, json=payload, headers=headers)
    assert resp.status_code == 201, resp.get_json()
    body = resp.get_json()
    if expected_initial_status:
        assert body[expected_status_field] == expected_initial_status
    return body

# ---------- Domain Specific Wrappers (example usage) ---------- #

def exercise_purchase_order_lifecycle(client, headers):
    po = create_resource_and_assert(client, '/po/purchase-orders', {'vendor_name':'Acme','branch_id':1,'total_cents':123}, headers, expected_initial_status='DRAFT')
    po_id = po['id']
    assert_transition(client, f'/po/purchase-orders/{po_id}/receive', headers, 200, expected_body_value='RECEIVED')
    assert_transition(client, f'/po/purchase-orders/{po_id}/close', headers, 200, expected_body_value='CLOSED')


def exercise_repair_ticket_lifecycle(client, headers):
    ticket = create_resource_and_assert(client, '/repairs/tickets', {'customer_name':'Alice','device_type':'Printer','issue_summary':'Jam','branch_id':1}, headers, expected_initial_status='NEW')
    tid = ticket['id']
    assert_transition(client, f'/repairs/tickets/{tid}/start', headers, 200, expected_body_value='IN_PROGRESS')
    assert_transition(client, f'/repairs/tickets/{tid}/complete', headers, 200, expected_body_value='COMPLETED')
    assert_transition(client, f'/repairs/tickets/{tid}/close', headers, 200, expected_body_value='CLOSED')


def exercise_print_job_lifecycle(client, headers):
    job = create_resource_and_assert(client, '/print/jobs', {'branch_id':1,'product_id':None}, headers, expected_initial_status='QUEUED')
    jid = job['id']
    assert_transition(client, f'/print/jobs/{jid}/start', headers, 200, expected_body_value='STARTED')
    assert_transition(client, f'/print/jobs/{jid}/complete', headers, 200, expected_body_value='COMPLETED')

__all__ = [
    'jwt_headers', 'seed_user_with_perms', 'assert_transition', 'create_resource_and_assert',
    'exercise_purchase_order_lifecycle', 'exercise_repair_ticket_lifecycle', 'exercise_print_job_lifecycle'
]
