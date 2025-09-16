from tests.test_utils_seed import ensure_permissions, ensure_user
from tests.test_lifecycle_helpers import jwt_headers


def seed_accounting_user(perms):
    ensure_permissions(perms)
    return ensure_user('acc@example.com')


def test_accounting_transaction_lifecycle(client, app_instance):
    user = seed_accounting_user(['ACC.READ','ACC.UPDATE','ACC.APPROVE','ACC.PAY'])
    with app_instance.app_context():
        headers = jwt_headers(user.id, ['ACC.READ','ACC.UPDATE','ACC.APPROVE','ACC.PAY'])
    # Create
    resp = client.post('/accounting/transactions', json={'description':'Office chairs','branch_id':1,'amount_cents':5000}, headers=headers)
    assert resp.status_code == 201, resp.get_json()
    tx = resp.get_json()
    assert tx['status'] == 'NEW'
    tx_id = tx['id']
    # Approve
    resp = client.post(f'/accounting/transactions/{tx_id}/approve', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'APPROVED'
    # Pay
    resp = client.post(f'/accounting/transactions/{tx_id}/pay', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'PAID'


def test_accounting_transaction_reject_path(client, app_instance):
    user = seed_accounting_user(['ACC.READ','ACC.UPDATE','ACC.APPROVE'])
    with app_instance.app_context():
        headers = jwt_headers(user.id, ['ACC.READ','ACC.UPDATE','ACC.APPROVE'])
    resp = client.post('/accounting/transactions', json={'description':'Faulty parts','branch_id':1,'amount_cents':900}, headers=headers)
    tx = resp.get_json()
    tx_id = tx['id']
    resp = client.post(f'/accounting/transactions/{tx_id}/reject', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'REJECTED'


def test_accounting_invalid_transition(client, app_instance):
    user = seed_accounting_user(['ACC.READ','ACC.UPDATE','ACC.PAY'])
    with app_instance.app_context():
        headers = jwt_headers(user.id, ['ACC.READ','ACC.UPDATE','ACC.PAY'])
    resp = client.post('/accounting/transactions', json={'description':'Supplies','branch_id':1,'amount_cents':1000}, headers=headers)
    tx_id = resp.get_json()['id']
    # Attempt paying directly from NEW should fail
    resp = client.post(f'/accounting/transactions/{tx_id}/pay', headers=headers)
    assert resp.status_code == 400


def test_accounting_head_and_openapi(client, app_instance):
    user = seed_accounting_user(['ACC.READ'])
    with app_instance.app_context():
        headers = jwt_headers(user.id, ['ACC.READ'])
    resp = client.head('/accounting/transactions', headers=headers)
    assert resp.status_code in (200,304)
    spec = client.get('/openapi.json').get_json()
    assert 'AccountingTransaction' in spec['components']['schemas']
    assert 'x-transitions' in spec['components']['schemas']['AccountingTransaction']
