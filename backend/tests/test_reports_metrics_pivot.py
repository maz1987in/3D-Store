from flask import Flask
from tests.test_utils_seed import ensure_permissions, ensure_user
from tests.test_lifecycle_helpers import jwt_headers

def _headers(user_id, perms):
    return jwt_headers(user_id, perms)

PERMS = ['RPT.READ','PO.VENDOR.CREATE','PO.VENDOR.READ']

def test_metrics_includes_vendor_and_pivot(app_instance: Flask):
    with app_instance.app_context():
        client = app_instance.test_client()
        ensure_permissions(PERMS)
        u = ensure_user('metrics_vendor@example.com')
        headers = _headers(u.id, PERMS)
        # Create a vendor so it appears
        client.post('/po/vendors', json={'name': 'MetricsVendor', 'branch_id': 1}, headers=headers)
        metrics_resp = client.get('/reports/metrics', headers=headers)
        assert metrics_resp.status_code == 200
        data = metrics_resp.get_json()['data']
        assert any(m['domain'] == 'Vendor' for m in data)
        # Pivot
        pivot_resp = client.get('/reports/metrics/pivot', headers=headers)
        assert pivot_resp.status_code == 200
        pdata = pivot_resp.get_json()['data']
        assert isinstance(pdata, list) and len(pdata) >= 1
        pivot = pdata[0]['pivot']
        assert 'Vendor' in pivot
        # HEAD
        head_resp = client.head('/reports/metrics/pivot', headers=headers)
        assert head_resp.status_code in (200,304)
        if head_resp.status_code == 200:
            assert 'ETag' in head_resp.headers
