from app import get_db
from app.models.authz import User, Role, Permission, RolePermission, UserRole, Group, GroupRole, UserGroup
from sqlalchemy import select


def _login(client, email, password):
    resp = client.post('/iam/auth/login', json={'email': email, 'password': password})
    assert resp.status_code == 200, resp.get_json()
    return resp.get_json()['access_token']


def _ensure_perm(session, code: str):
    p = session.execute(select(Permission).where(Permission.code==code)).scalar_one_or_none()
    if p:
        return p
    svc, action = code.split('.', 1)
    p = Permission(code=code, service=svc, action=action, description_i18n={'en': code})
    session.add(p); session.flush()
    return p


def test_sales_order_flow_and_audit(client):
    session = get_db()
    try:
        session.rollback()
    except Exception:
        pass
    # Create user
    u = User(name='SalesUser', email='sales@example.com', password_hash=''); u.set_password('pw'); session.add(u)
    # Role with sales perms
    r = Role(name='SalesRole', is_system=False, description_i18n={'en': 'Sales'}); session.add(r); session.flush()
    for code in ['SALES.READ', 'SALES.CREATE', 'SALES.UPDATE', 'SALES.APPROVE', 'SALES.FULFILL', 'SALES.COMPLETE', 'SALES.CANCEL']:
        perm = _ensure_perm(session, code)
        session.add(RolePermission(role_id=r.id, permission_id=perm.id))
    # Group with branch scope for branch 5
    g = Group(name='SalesBranch5', description_i18n={'en': 'B5'}, branch_scope={'allow': [5]}); session.add(g); session.flush()
    session.add(GroupRole(group_id=g.id, role_id=r.id))
    session.add(UserGroup(user_id=u.id, group_id=g.id))
    session.commit()
    token = _login(client, 'sales@example.com', 'pw')
    headers = {'Authorization': f'Bearer {token}'}
    # Create order
    create_resp = client.post('/sales/orders', json={'customer_name': 'Acme', 'branch_id': 5, 'total_cents': 1500}, headers=headers)
    assert create_resp.status_code == 201, create_resp.get_json()
    oid = create_resp.get_json()['id']
    # Update order
    upd_resp = client.put(f'/sales/orders/{oid}', json={'customer_name': 'Acme Intl', 'total_cents': 1750}, headers=headers)
    assert upd_resp.status_code == 200
    # Approve -> Fulfill -> Complete sequence
    approve_resp = client.post(f'/sales/orders/{oid}/approve', headers=headers)
    assert approve_resp.status_code == 200 and approve_resp.get_json()['status'] == 'APPROVED'
    fulfill_resp = client.post(f'/sales/orders/{oid}/fulfill', headers=headers)
    assert fulfill_resp.status_code == 200 and fulfill_resp.get_json()['status'] == 'FULFILLED'
    complete_resp = client.post(f'/sales/orders/{oid}/complete', headers=headers)
    assert complete_resp.status_code == 200 and complete_resp.get_json()['status'] == 'COMPLETED'
    # List orders
    list_resp = client.get('/sales/orders?limit=25', headers=headers)
    assert list_resp.status_code == 200 and list_resp.get_json()['data']
    assert 'pagination' in list_resp.get_json()
    # Audit logs
    from app.models.audit import AuditLog
    audits = session.query(AuditLog).filter(AuditLog.action.in_([
        'ORDER.CREATE', 'ORDER.UPDATE', 'ORDER.APPROVE', 'ORDER.FULFILL', 'ORDER.COMPLETE'
    ])).all()
    assert len(audits) >= 5
    # Check diff meta for update & approve
    update_audit = session.query(AuditLog).filter(AuditLog.action=='ORDER.UPDATE').order_by(AuditLog.id.desc()).first()
    assert update_audit and 'changes' in (update_audit.meta or {})
    approve_audit = session.query(AuditLog).filter(AuditLog.action=='ORDER.APPROVE').order_by(AuditLog.id.desc()).first()
    assert approve_audit and 'changes' in (approve_audit.meta or {})
    fulfill_audit = session.query(AuditLog).filter(AuditLog.action=='ORDER.FULFILL').order_by(AuditLog.id.desc()).first()
    assert fulfill_audit and 'changes' in (fulfill_audit.meta or {})
    complete_audit = session.query(AuditLog).filter(AuditLog.action=='ORDER.COMPLETE').order_by(AuditLog.id.desc()).first()
    assert complete_audit and 'changes' in (complete_audit.meta or {})


def test_sales_order_cancel_paths_and_invalid_transition(client):
    session = get_db()
    try:
        session.rollback()
    except Exception:
        pass
    # User and role
    u = User(name='SalesCancel', email='salescancel@example.com', password_hash=''); u.set_password('pw'); session.add(u)
    r = Role(name='SalesCancelRole', is_system=False, description_i18n={'en': 'Sales'}); session.add(r); session.flush()
    for code in ['SALES.READ', 'SALES.CREATE', 'SALES.APPROVE', 'SALES.FULFILL', 'SALES.COMPLETE', 'SALES.CANCEL']:
        perm = _ensure_perm(session, code); session.add(RolePermission(role_id=r.id, permission_id=perm.id))
    g = Group(name='SalesCancelGroup', description_i18n={'en': 'B10'}, branch_scope={'allow': [10]}); session.add(g); session.flush()
    session.add(GroupRole(group_id=g.id, role_id=r.id)); session.add(UserGroup(user_id=u.id, group_id=g.id)); session.commit()
    token = _login(client, 'salescancel@example.com', 'pw'); headers={'Authorization': f'Bearer {token}'}
    # Create order
    o = client.post('/sales/orders', json={'customer_name': 'Cancelable', 'branch_id': 10, 'total_cents': 500}, headers=headers).get_json(); oid = o['id']
    # Cancel directly from NEW
    c1 = client.post(f'/sales/orders/{oid}/cancel', headers=headers)
    assert c1.status_code == 200 and c1.get_json()['status'] == 'CANCELLED'
    # Invalid transition: try approve after cancel
    bad = client.post(f'/sales/orders/{oid}/approve', headers=headers)
    assert bad.status_code == 400
    # Create second order and take to FULFILLED then cancel
    o2 = client.post('/sales/orders', json={'customer_name': 'Cancelable2', 'branch_id': 10, 'total_cents': 600}, headers=headers).get_json(); oid2 = o2['id']
    client.post(f'/sales/orders/{oid2}/approve', headers=headers)
    client.post(f'/sales/orders/{oid2}/fulfill', headers=headers)
    c2 = client.post(f'/sales/orders/{oid2}/cancel', headers=headers)
    assert c2.status_code == 200 and c2.get_json()['status'] == 'CANCELLED'
    # Create third order complete path then attempt cancel (should 400)
    o3 = client.post('/sales/orders', json={'customer_name': 'CompleteFirst', 'branch_id': 10, 'total_cents': 700}, headers=headers).get_json(); oid3 = o3['id']
    client.post(f'/sales/orders/{oid3}/approve', headers=headers)
    client.post(f'/sales/orders/{oid3}/fulfill', headers=headers)
    client.post(f'/sales/orders/{oid3}/complete', headers=headers)
    c3 = client.post(f'/sales/orders/{oid3}/cancel', headers=headers)
    assert c3.status_code == 400


def test_sales_branch_scope_filtering(client):
    session = get_db()
    try:
        session.rollback()
    except Exception:
        pass
    # User with branch scope [7]
    u = User(name='ScopedSales', email='scopedsales@example.com', password_hash=''); u.set_password('pw'); session.add(u)
    r = Role(name='ScopedSalesRole', is_system=False, description_i18n={'en': 'Sales'}); session.add(r); session.flush()
    for code in ['SALES.READ', 'SALES.CREATE']:
        perm = _ensure_perm(session, code); session.add(RolePermission(role_id=r.id, permission_id=perm.id))
    g = Group(name='SalesBranch7', description_i18n={'en': 'B7'}, branch_scope={'allow': [7]}); session.add(g); session.flush()
    session.add(GroupRole(group_id=g.id, role_id=r.id)); session.add(UserGroup(user_id=u.id, group_id=g.id))
    session.commit()
    token = _login(client, 'scopedsales@example.com', 'pw'); headers = {'Authorization': f'Bearer {token}'}
    # Create order in allowed branch 7
    c_ok = client.post('/sales/orders', json={'customer_name': 'Client', 'branch_id': 7, 'total_cents': 500}, headers=headers)
    assert c_ok.status_code == 201
    # Attempt to create order in disallowed branch 8
    c_bad = client.post('/sales/orders', json={'customer_name': 'Client2', 'branch_id': 8, 'total_cents': 600}, headers=headers)
    assert c_bad.status_code in (400, 403)
    # List -> only branch 7 orders
    lst = client.get('/sales/orders?limit=10', headers=headers)
    assert lst.status_code == 200
    assert all(o['branch_id']==7 for o in lst.get_json()['data'])
    assert 'pagination' in lst.get_json()


def test_sales_pagination(client):
    session = get_db()
    try:
        session.rollback()
    except Exception:
        pass
    from app.models.authz import User, Role, Permission, RolePermission, UserGroup, Group, GroupRole
    from sqlalchemy import select
    u = session.query(User).filter_by(email='salespag@example.com').one_or_none()
    if not u:
        u = User(name='SalesPag', email='salespag@example.com', password_hash=''); u.set_password('pw'); session.add(u)
    r = session.query(Role).filter_by(name='SalesPagRole').one_or_none()
    if not r:
        r = Role(name='SalesPagRole', is_system=False, description_i18n={'en': 'Sales'}); session.add(r); session.flush()
        for code in ['SALES.READ', 'SALES.CREATE']:
            p = session.execute(select(Permission).where(Permission.code==code)).scalar_one_or_none()
            if not p:
                svc, action = code.split('.', 1)
                p = Permission(code=code, service=svc, action=action, description_i18n={'en': code}); session.add(p); session.flush()
            session.add(RolePermission(role_id=r.id, permission_id=p.id))
    g = session.query(Group).filter_by(name='SalesPagGroup').one_or_none()
    if not g:
        g = Group(name='SalesPagGroup', description_i18n={'en': 'B9'}, branch_scope={'allow': [9]}); session.add(g); session.flush()
        session.add(GroupRole(group_id=g.id, role_id=r.id))
        session.add(UserGroup(user_id=u.id, group_id=g.id))
    session.commit()
    token = _login(client, 'salespag@example.com', 'pw'); headers={'Authorization': f'Bearer {token}'}
    for i in range(6):
        client.post('/sales/orders', json={'customer_name': f'C{i}', 'branch_id': 9, 'total_cents': 100+i}, headers=headers)
    lst1 = client.get('/sales/orders?limit=3&offset=0', headers=headers).get_json()
    lst2 = client.get('/sales/orders?limit=3&offset=3', headers=headers).get_json()
    assert lst1['pagination']['returned'] == 3
    assert lst2['pagination']['returned'] == 3
    assert lst1['pagination']['total'] >= 6
