from flask import Flask
from datetime import datetime, timedelta
from tests.test_utils_seed import ensure_permissions, ensure_user
from tests.test_lifecycle_helpers import jwt_headers

PERMS = ['RPT.READ','SALES.CREATE','SALES.READ']

def _headers(uid, perms):
    return jwt_headers(uid, perms)

def test_metrics_date_filter_excludes_older_rows(app_instance: Flask):
    with app_instance.app_context():
        client = app_instance.test_client()
        ensure_permissions(PERMS)
        u = ensure_user('metrics_dates@example.com')
        headers = _headers(u.id, PERMS)
        # Create an order (will have current updated_at)
        client.post('/sales/orders', json={'customer_name': 'Date Test', 'branch_id':1, 'total_cents': 10}, headers=headers)
        # Baseline metrics
        base = client.get('/reports/metrics', headers=headers).get_json()['data']
        order_counts = [r for r in base if r['domain']=='Order']
        assert order_counts
        # Use start_date in the future to exclude current rows
        future = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d')
        filtered = client.get(f'/reports/metrics?start_date={future}', headers=headers).get_json()['data']
        order_counts_future = [r for r in filtered if r['domain']=='Order']
        # Expect either empty or all zero counts
        assert order_counts_future == []
