from tests.test_utils_seed import ensure_permissions, ensure_user
from tests.test_lifecycle_helpers import jwt_headers

VENDOR_PERMS = ['PO.VENDOR.READ','PO.VENDOR.CREATE']
PROD_PERMS = ['INV.READ','INV.ADJUST']
ORDER_PERMS = ['SALES.READ','SALES.CREATE']


def _headers(app, user_id: int, perms):
    # create_access_token requires an active app context
    with app.app_context():
        return jwt_headers(user_id, perms)


def test_head_vendor_resource(app_instance):
    with app_instance.app_context():
        ensure_permissions(VENDOR_PERMS)
        u = ensure_user('head_vendor@example.com')
    client = app_instance.test_client()
    headers = _headers(app_instance, u.id, VENDOR_PERMS)
    # create
    resp = client.post('/po/vendors', json={'name': 'HV1', 'branch_id': 1}, headers=headers)
    assert resp.status_code == 201
    vid = resp.get_json()['id']
    # HEAD existing
    h1 = client.head(f'/po/vendors/{vid}', headers=headers)
    assert h1.status_code == 200
    assert 'ETag' in h1.headers
    # Conditional 304
    inm = {'If-None-Match': h1.headers['ETag'], **headers}
    h2 = client.head(f'/po/vendors/{vid}', headers=inm)
    assert h2.status_code == 304


def test_head_product_resource(app_instance):
    with app_instance.app_context():
        ensure_permissions(PROD_PERMS)
        u = ensure_user('head_product@example.com')
    client = app_instance.test_client()
    headers = _headers(app_instance, u.id, PROD_PERMS)
    # create product
    resp = client.post('/inventory/products', json={'name':'Widget','sku':'W-HEAD','branch_id':1}, headers=headers)
    assert resp.status_code == 201
    pid = resp.get_json()['id']
    h1 = client.head(f'/inventory/products/{pid}', headers=headers)
    assert h1.status_code == 200
    assert 'ETag' in h1.headers
    inm = {'If-None-Match': h1.headers['ETag'], **headers}
    h2 = client.head(f'/inventory/products/{pid}', headers=inm)
    assert h2.status_code == 304


def test_head_order_resource(app_instance):
    from tests.test_lifecycle_helpers import jwt_headers
    with app_instance.app_context():
        ensure_permissions(ORDER_PERMS)
        u = ensure_user('head_order@example.com')
    client = app_instance.test_client()
    headers = _headers(app_instance, u.id, ORDER_PERMS)
    # create order
    resp = client.post('/sales/orders', json={'customer_name':'Acme','branch_id':1,'total_cents':1234}, headers=headers)
    assert resp.status_code == 201
    oid = resp.get_json()['id']
    h1 = client.head(f'/sales/orders/{oid}', headers=headers)
    assert h1.status_code == 200
    assert 'ETag' in h1.headers
    inm = {'If-None-Match': h1.headers['ETag'], **headers}
    h2 = client.head(f'/sales/orders/{oid}', headers=inm)
    assert h2.status_code == 304
