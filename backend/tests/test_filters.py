from app import get_db
from app.models.authz import User, Role, Permission, RolePermission, Group, GroupRole, UserGroup, UserRole


def _login(client, email, password):
    r = client.post('/iam/auth/login', json={'email': email, 'password': password})
    assert r.status_code == 200
    return r.get_json()['access_token']


def _ensure_perm(session, code):
    from app.models.authz import Permission
    p = session.query(Permission).filter_by(code=code).one_or_none()
    if not p:
        svc, action = code.split('.', 1)
        p = Permission(code=code, service=svc, action=action, description_i18n={'en': code})
        session.add(p); session.flush()
    return p


def test_inventory_filters(client):
    session = get_db()
    # User with INV.READ
    u = User(name='InvFilter', email='invfilter@example.com', password_hash=''); u.set_password('pw'); session.add(u)
    role = Role(name='InvFilterRole', is_system=False, description_i18n={'en': 'inv filter'}); session.add(role); session.flush()
    for code in ['INV.READ', 'INV.ADJUST']:
        p = _ensure_perm(session, code); session.add(RolePermission(role_id=role.id, permission_id=p.id))
    # Group restricting to branch 1
    g = Group(name='InvFilterGroup', description_i18n={'en': 'filter'}, branch_scope={'allow': [1]}); session.add(g); session.flush()
    session.add(GroupRole(group_id=g.id, role_id=role.id)); session.add(UserGroup(user_id=u.id, group_id=g.id))
    session.commit()
    token = _login(client, 'invfilter@example.com', 'pw'); headers={'Authorization': f'Bearer {token}'}
    # Seed products across branches
    client.post('/inventory/products', json={'name': 'Widget', 'sku': 'W1', 'branch_id': 1, 'quantity': 2}, headers=headers)
    client.post('/inventory/products', json={'name': 'Gadget', 'sku': 'G1', 'branch_id': 1, 'quantity': 3}, headers=headers)
    session.commit()
    # Out-of-scope branch product (should be invisible)
    client.post('/inventory/products', json={'name': 'External', 'sku': 'X2', 'branch_id': 2, 'quantity': 1}, headers=headers)
    # Filter by sku
    by_sku = client.get('/inventory/products?sku=G1', headers=headers).get_json()
    assert by_sku['pagination']['returned'] == 1
    assert by_sku['data'][0]['sku'] == 'G1'
    # Filter by name substring
    by_name = client.get('/inventory/products?name=Widget', headers=headers).get_json()
    assert by_name['pagination']['returned'] == 1
    assert by_name['data'][0]['name'] == 'Widget'
    # Filter by out-of-scope branch -> empty
    out = client.get('/inventory/products?branch_id=2', headers=headers).get_json()
    assert out['pagination']['returned'] == 0


def test_sales_filters(client):
    session = get_db()
    u = User(name='SalesFilter', email='salesfilter@example.com', password_hash=''); u.set_password('pw'); session.add(u)
    role = Role(name='SalesFilterRole', is_system=False, description_i18n={'en': 'sales filter'}); session.add(role); session.flush()
    for code in ['SALES.READ', 'SALES.CREATE', 'SALES.APPROVE']:
        p = _ensure_perm(session, code); session.add(RolePermission(role_id=role.id, permission_id=p.id))
    g = Group(name='SalesFilterGroup', description_i18n={'en': 'filter'}, branch_scope={'allow': [5]}); session.add(g); session.flush()
    session.add(GroupRole(group_id=g.id, role_id=role.id)); session.add(UserGroup(user_id=u.id, group_id=g.id)); session.commit()
    token = _login(client, 'salesfilter@example.com', 'pw'); headers={'Authorization': f'Bearer {token}'}
    # Create orders
    o1 = client.post('/sales/orders', json={'customer_name': 'Acme A', 'branch_id': 5, 'total_cents': 100}, headers=headers)
    assert o1.status_code == 201
    o2 = client.post('/sales/orders', json={'customer_name': 'Beta B', 'branch_id': 5, 'total_cents': 200}, headers=headers)
    # Approve second order
    client.post(f"/sales/orders/{o2.get_json()['id']}/approve", headers=headers)
    # Out-of-scope branch attempt (should be invisible)
    client.post('/sales/orders', json={'customer_name': 'Hidden', 'branch_id': 6, 'total_cents': 50}, headers=headers)
    # Filter by customer_name substring
    acme = client.get('/sales/orders?customer_name=Acme', headers=headers).get_json()
    assert acme['pagination']['returned'] == 1
    assert acme['data'][0]['customer_name'].startswith('Acme')
    # Filter by status APPROVED
    approved = client.get('/sales/orders?status=APPROVED', headers=headers).get_json()
    assert approved['pagination']['returned'] == 1
    assert approved['data'][0]['status'] == 'APPROVED'
    # Filter by out-of-scope branch
    out = client.get('/sales/orders?branch_id=6', headers=headers).get_json()
    assert out['pagination']['returned'] == 0