from app import get_db
from tests.test_utils_seed import ensure_permissions, ensure_user
from tests.test_lifecycle_helpers import jwt_headers
from app.models.print_job import PrintJob
from app.models.purchase_order import PurchaseOrder
from app.models.repair_ticket import RepairTicket
from app.models.accounting_transaction import AccountingTransaction


def _scoped_headers(perms):
    ensure_permissions(perms)
    user = ensure_user('scoped_user@example.com')
    return jwt_headers(user.id, perms), user


def test_branch_scope_filters_print_jobs_and_blocks_transition(client, app_instance):
    with app_instance.app_context():
        headers, user = _scoped_headers(['PRINT.READ','PRINT.START'])
        session = get_db()
        job = PrintJob(branch_id=2, product_id=None, created_by=user.id)
        session.add(job)
        session.commit()
        # List should not reveal branch 2 job
        resp = client.get('/print/jobs', headers=headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert all(r['branch_id'] == 1 for r in body['data']) if body['data'] else True
        # Transition should 403 branch access denied
        r2 = client.post(f'/print/jobs/{job.id}/start', headers=headers)
        assert r2.status_code == 403


def test_branch_scope_filters_purchase_orders_and_blocks_transition(client, app_instance):
    with app_instance.app_context():
        headers, user = _scoped_headers(['PO.READ','PO.RECEIVE'])
        session = get_db()
        po = PurchaseOrder(branch_id=2, vendor_name='OtherVendor', total_cents=1000, created_by=user.id)
        session.add(po)
        session.commit()
        resp = client.get('/po/purchase-orders', headers=headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert all(r['branch_id'] == 1 for r in body['data']) if body['data'] else True
        r2 = client.post(f'/po/purchase-orders/{po.id}/receive', headers=headers)
        assert r2.status_code == 403


def test_branch_scope_filters_repair_tickets_and_blocks_transition(client, app_instance):
    with app_instance.app_context():
        headers, user = _scoped_headers(['RPR.READ','RPR.MANAGE'])
        session = get_db()
        t = RepairTicket(branch_id=2, customer_name='Bob', device_type='Printer', issue_summary='Paper jam', created_by=user.id)
        session.add(t)
        session.commit()
        resp = client.get('/repairs/tickets', headers=headers)
        assert resp.status_code == 200
        body = resp.get_json()
        if isinstance(body, dict) and 'data' in body:  # first repairs endpoint version returns structured object
            data_list = body['data']
        else:  # fallback if placeholder shape
            data_list = body.get('data', [])
        assert all(r.get('branch_id') == 1 for r in data_list) if data_list else True
        r2 = client.post(f'/repairs/tickets/{t.id}/start', headers=headers)
        assert r2.status_code == 403


def test_branch_scope_filters_accounting_transactions_and_blocks_transition(client, app_instance):
    with app_instance.app_context():
        headers, user = _scoped_headers(['ACC.READ','ACC.APPROVE'])
        session = get_db()
        tx = AccountingTransaction(branch_id=2, description='Out of scope', amount_cents=500, created_by=user.id)
        session.add(tx)
        session.commit()
        resp = client.get('/accounting/transactions', headers=headers)
        assert resp.status_code == 200
        body = resp.get_json()
        assert all(r['branch_id'] == 1 for r in body['data']) if body['data'] else True
        r2 = client.post(f'/accounting/transactions/{tx.id}/approve', headers=headers)
        assert r2.status_code == 403
