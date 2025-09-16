from flask import Flask
from tests.test_utils_seed import ensure_permissions, ensure_user
from tests.test_lifecycle_helpers import jwt_headers

def _headers(user_id, perms):
    return jwt_headers(user_id, perms)

PERMS = ['RPT.READ','SALES.CREATE','SALES.READ','ACC.READ','ACC.UPDATE','PO.CREATE','PO.READ']

def test_metrics_include_financial(app_instance: Flask):
    with app_instance.app_context():
        client = app_instance.test_client()
        ensure_permissions(PERMS)
        u = ensure_user('metrics_financial@example.com')
        headers = _headers(u.id, PERMS)
        # Create order & accounting txn & purchase order to have sums
        client.post('/sales/orders', json={'customer_name': 'Fin Cust', 'branch_id': 1, 'total_cents': 1234}, headers=headers)
        client.post('/accounting/transactions', json={'description': 'Invoice', 'branch_id':1, 'amount_cents': 555}, headers=headers)
        client.post('/po/purchase-orders', json={'vendor_name': 'Supplier A', 'branch_id':1, 'total_cents': 777}, headers=headers)
        resp = client.get('/reports/metrics?include_financial=true', headers=headers)
        assert resp.status_code == 200
        rows = resp.get_json()['data']
        # Ensure sum_cents present for relevant domains
        order_rows = [r for r in rows if r['domain']=='Order']
        acct_rows = [r for r in rows if r['domain']=='AccountingTransaction']
        assert any('sum_cents' in r for r in order_rows)
        assert any('sum_cents' in r for r in acct_rows)
        po_rows = [r for r in rows if r['domain']=='PurchaseOrder']
        assert any('sum_cents' in r for r in po_rows)
        # Pivot variant
        piv = client.get('/reports/metrics/pivot?include_financial=true', headers=headers)
        assert piv.status_code == 200
        pdata = piv.get_json()['data'][0]['pivot']
        assert 'Order' in pdata and 'AccountingTransaction' in pdata and 'PurchaseOrder' in pdata
