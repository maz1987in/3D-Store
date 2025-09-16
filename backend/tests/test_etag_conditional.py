def test_etag_conditional_inventory(client):
    # Setup user with perms
    from app import get_db
    from app.models.authz import User, Role, Permission, RolePermission, Group, GroupRole, UserGroup
    from sqlalchemy import select
    session = get_db()
    u = session.query(User).filter_by(email='etag_inv@example.com').one_or_none()
    if not u:
        u = User(name='ETagInv', email='etag_inv@example.com', password_hash=''); u.set_password('pw'); session.add(u)
    role = session.query(Role).filter_by(name='ETagInvRole').one_or_none()
    if not role:
        role = Role(name='ETagInvRole', is_system=False, description_i18n={'en': 'etag'}); session.add(role); session.flush()
        for code in ['INV.READ','INV.ADJUST']:
            p = session.execute(select(Permission).where(Permission.code==code)).scalar_one_or_none()
            if not p:
                svc, action = code.split('.', 1)
                p = Permission(code=code, service=svc, action=action, description_i18n={'en': code}); session.add(p); session.flush()
            session.add(RolePermission(role_id=role.id, permission_id=p.id))
    g = session.query(Group).filter_by(name='ETagInvGroup').one_or_none()
    if not g:
        g = Group(name='ETagInvGroup', description_i18n={'en': 'g'}, branch_scope={'allow': [1]}); session.add(g); session.flush()
        session.add(GroupRole(group_id=g.id, role_id=role.id)); session.add(UserGroup(user_id=u.id, group_id=g.id))
    session.commit()
    token = client.post('/iam/auth/login', json={'email': 'etag_inv@example.com', 'password': 'pw'}).get_json()['access_token']
    headers={'Authorization': f'Bearer {token}'}
    # Seed one product
    client.post('/inventory/products', json={'name': 'ETagWidget', 'sku': 'ETAGSKU', 'branch_id':1, 'quantity':1}, headers=headers)
    first = client.get('/inventory/products?limit=5', headers=headers)
    assert first.status_code == 200
    etag = first.headers.get('ETag')
    assert etag
    # Conditional request
    second = client.get('/inventory/products?limit=5', headers={**headers, 'If-None-Match': etag})
    assert second.status_code == 304
    assert second.headers.get('ETag') == etag
    # If-Modified-Since should also 304 when using Last-Modified from first response
    lm = first.headers.get('Last-Modified')
    if lm:
        third = client.get('/inventory/products?limit=5', headers={**headers, 'If-Modified-Since': lm})
        assert third.status_code == 304
        assert third.headers.get('ETag') == etag

def test_etag_conditional_sales(client):
    from app import get_db
    from app.models.authz import User, Role, Permission, RolePermission, Group, GroupRole, UserGroup
    from sqlalchemy import select
    session = get_db()
    u = session.query(User).filter_by(email='etag_sales@example.com').one_or_none()
    if not u:
        u = User(name='ETagSales', email='etag_sales@example.com', password_hash=''); u.set_password('pw'); session.add(u)
    role = session.query(Role).filter_by(name='ETagSalesRole').one_or_none()
    if not role:
        role = Role(name='ETagSalesRole', is_system=False, description_i18n={'en': 'etag'}); session.add(role); session.flush()
        for code in ['SALES.READ','SALES.CREATE']:
            p = session.execute(select(Permission).where(Permission.code==code)).scalar_one_or_none()
            if not p:
                svc, action = code.split('.', 1)
                p = Permission(code=code, service=svc, action=action, description_i18n={'en': code}); session.add(p); session.flush()
            session.add(RolePermission(role_id=role.id, permission_id=p.id))
    g = session.query(Group).filter_by(name='ETagSalesGroup').one_or_none()
    if not g:
        g = Group(name='ETagSalesGroup', description_i18n={'en': 'g'}, branch_scope={'allow': [5]}); session.add(g); session.flush()
        session.add(GroupRole(group_id=g.id, role_id=role.id)); session.add(UserGroup(user_id=u.id, group_id=g.id))
    session.commit()
    token = client.post('/iam/auth/login', json={'email': 'etag_sales@example.com', 'password': 'pw'}).get_json()['access_token']
    headers={'Authorization': f'Bearer {token}'}
    client.post('/sales/orders', json={'customer_name': 'ETagCustomer', 'branch_id':5, 'total_cents': 10}, headers=headers)
    first = client.get('/sales/orders?limit=5', headers=headers)
    assert first.status_code == 200
    etag = first.headers.get('ETag')
    assert etag
    second = client.get('/sales/orders?limit=5', headers={**headers, 'If-None-Match': etag})
    assert second.status_code == 304
    assert second.headers.get('ETag') == etag
    lm = first.headers.get('Last-Modified')
    if lm:
        third = client.get('/sales/orders?limit=5', headers={**headers, 'If-Modified-Since': lm})
        assert third.status_code == 304
        assert third.headers.get('ETag') == etag