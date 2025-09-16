from tests.test_utils_seed import ensure_permissions, ensure_user
from tests.test_lifecycle_helpers import jwt_headers

ORDER_PERMS = ['SALES.READ','SALES.CREATE']
VENDOR_PERMS = ['PO.VENDOR.READ','PO.VENDOR.CREATE']


def test_orders_multi_sort(client, app_instance):
    with app_instance.app_context():
        ensure_permissions(ORDER_PERMS)
        user = ensure_user('order_sort@example.com')
        headers = jwt_headers(user.id, ORDER_PERMS)
    # seed orders same total different names
    client.post('/sales/orders', json={'customer_name':'Charlie','branch_id':1,'total_cents':500}, headers=headers)
    client.post('/sales/orders', json={'customer_name':'Bravo','branch_id':1,'total_cents':500}, headers=headers)
    client.post('/sales/orders', json={'customer_name':'Alpha','branch_id':1,'total_cents':500}, headers=headers)
    resp = client.get('/sales/orders?sort=total_cents,-customer_name', headers=headers)
    assert resp.status_code == 200
    names = [o['customer_name'] for o in resp.get_json()['data'] if o['total_cents']==500]
    # Expect descending alpha within equal total
    # Filter only seeded 3
    subset = [n for n in names if n in ('Alpha','Bravo','Charlie')]
    if len(subset) == 3:
        assert subset == ['Charlie','Bravo','Alpha']


def test_vendors_multi_sort(client, app_instance):
    with app_instance.app_context():
        ensure_permissions(VENDOR_PERMS)
        user = ensure_user('vendor_sort@example.com')
        headers = jwt_headers(user.id, VENDOR_PERMS)
    client.post('/po/vendors', json={'name':'Gamma','branch_id':1}, headers=headers)
    client.post('/po/vendors', json={'name':'Beta','branch_id':1}, headers=headers)
    client.post('/po/vendors', json={'name':'AlphaVendor','branch_id':1}, headers=headers)
    resp = client.get('/po/vendors?sort=-name', headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()['data']
    names = [v['name'] for v in data if v['name'] in ('Gamma','Beta','AlphaVendor')]
    # Descending
    target = sorted(names, reverse=True)
    assert names[:len(target)] == target
