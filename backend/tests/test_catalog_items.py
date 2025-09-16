from tests.test_utils_seed import ensure_permissions, ensure_user
from tests.test_lifecycle_helpers import jwt_headers

def seed_catalog_user(perms):
    ensure_permissions(perms)
    return ensure_user('catalog@example.com')


def test_catalog_item_crud_and_archive_activate(client, app_instance):
    user = seed_catalog_user(['CAT.READ','CAT.CREATE','CAT.MANAGE'])
    with app_instance.app_context():
        headers = jwt_headers(user.id, ['CAT.READ','CAT.CREATE','CAT.MANAGE'])
    # Create
    resp = client.post('/catalog/items', json={'name':'Widget','sku':'W1','category':'General','branch_id':1,'price_cents':1500,'description_i18n':{'en':'Widget'}}, headers=headers)
    assert resp.status_code == 201, resp.get_json()
    item = resp.get_json()
    assert item['status'] == 'ACTIVE'
    item_id = item['id']
    # Update
    resp = client.put(f'/catalog/items/{item_id}', json={'price_cents':2000,'description_i18n':{'en':'Widget updated'}}, headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['price_cents'] == 2000
    # Archive
    resp = client.post(f'/catalog/items/{item_id}/archive', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'ARCHIVED'
    # Activate
    resp = client.post(f'/catalog/items/{item_id}/activate', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'ACTIVE'


def test_catalog_list_and_head(client, app_instance):
    user = seed_catalog_user(['CAT.READ'])
    with app_instance.app_context():
        headers = jwt_headers(user.id, ['CAT.READ'])
    resp = client.get('/catalog/items', headers=headers)
    assert resp.status_code == 200
    head_resp = client.head('/catalog/items', headers=headers)
    assert head_resp.status_code in (200,304)
    # Seed a few items for filter tests (need create perm)
    with app_instance.app_context():
        creator = seed_catalog_user(['CAT.CREATE','CAT.READ'])
        creator_headers = jwt_headers(creator.id, ['CAT.CREATE','CAT.READ'])
    client.post('/catalog/items', json={'name':'Cheap','sku':'C1','category':'Gen','branch_id':1,'price_cents':100,'description_i18n':{}}, headers=creator_headers)
    client.post('/catalog/items', json={'name':'Mid','sku':'M1','category':'Gen','branch_id':1,'price_cents':500,'description_i18n':{}}, headers=creator_headers)
    client.post('/catalog/items', json={'name':'Exp','sku':'E1','category':'Gen','branch_id':1,'price_cents':1000,'description_i18n':{}}, headers=creator_headers)
    # min filter
    resp = client.get('/catalog/items?min_price_cents=400', headers=headers)
    assert all(i['price_cents'] >= 400 for i in resp.get_json()['data'])
    # max filter
    resp = client.get('/catalog/items?max_price_cents=400', headers=headers)
    assert all(i['price_cents'] <= 400 for i in resp.get_json()['data'])
    # range filter
    resp = client.get('/catalog/items?min_price_cents=200&max_price_cents=800', headers=headers)
    assert all(200 <= i['price_cents'] <= 800 for i in resp.get_json()['data'])
    # invalid range
    bad = client.get('/catalog/items?min_price_cents=900&max_price_cents=100', headers=headers)
    assert bad.status_code == 400
    # sort asc
    resp = client.get('/catalog/items?sort=price_cents', headers=headers)
    prices = [i['price_cents'] for i in resp.get_json()['data']]
    assert prices == sorted(prices)
    # sort desc
    resp = client.get('/catalog/items?sort=-price_cents', headers=headers)
    prices = [i['price_cents'] for i in resp.get_json()['data']]
    assert prices == sorted(prices, reverse=True)
    # multi-field sort: price asc then name desc (names crafted)
    client.post('/catalog/items', json={'name':'Zed','sku':'Z1','category':'Gen','branch_id':1,'price_cents':500,'description_i18n':{}}, headers=creator_headers)
    client.post('/catalog/items', json={'name':'Able','sku':'A1','category':'Gen','branch_id':1,'price_cents':500,'description_i18n':{}}, headers=creator_headers)
    resp = client.get('/catalog/items?sort=price_cents,-name', headers=headers)
    data = resp.get_json()['data']
    # Extract rows with price 500 and ensure name ordering desc within that subset (Zed before Mid before Able maybe) depending existing entries
    subset = [i['name'] for i in data if i['price_cents']==500]
    if len(subset) >= 2:
        assert subset == sorted(subset, reverse=True)


def test_catalog_invalid_description_i18n(client, app_instance):
    user = seed_catalog_user(['CAT.CREATE'])
    with app_instance.app_context():
        headers = jwt_headers(user.id, ['CAT.CREATE'])
    resp = client.post('/catalog/items', json={'name':'Bad','sku':'B1','category':'Gen','branch_id':1,'description_i18n':'not_obj'}, headers=headers)
    assert resp.status_code == 400
