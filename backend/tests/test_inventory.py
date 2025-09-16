from app import get_db
from app.models.authz import User, Role, Permission, RolePermission, UserRole, Group, GroupRole, UserGroup
from app.models.product import Product
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


def test_inventory_branch_scope_and_adjust(client):
    session = get_db()
    try:
        session.rollback()
    except Exception:
        pass
    # Create user
    u = User(name='InvUser', email='inv@example.com', password_hash='')
    u.set_password('pw'); session.add(u)
    # Role with inventory perms
    r = Role(name='InventoryUser', is_system=False, description_i18n={'en': 'Inventory'})
    session.add(r); session.flush()
    for code in ['INV.READ', 'INV.ADJUST']:
        perm = _ensure_perm(session, code)
        session.add(RolePermission(role_id=r.id, permission_id=perm.id))
    # Group with branch scope allowing branch 1 only
    g = Group(name='InvBranch1', description_i18n={'en': 'B1'}, branch_scope={'allow': [1]})
    session.add(g); session.flush()
    session.add(GroupRole(group_id=g.id, role_id=r.id))
    session.add(UserGroup(user_id=u.id, group_id=g.id))
    session.commit()

    token = _login(client, 'inv@example.com', 'pw')
    headers = {'Authorization': f'Bearer {token}'}

    # Create product in allowed branch 1
    p1_resp = client.post('/inventory/products', json={'name': 'Widget', 'sku': 'W1_SCOPE', 'branch_id': 1, 'quantity': 5}, headers=headers)
    assert p1_resp.status_code == 201, p1_resp.get_json()
    p1_id = p1_resp.get_json()['id']

    # Attempt create product in disallowed branch 2 (should 403)
    p2_resp = client.post('/inventory/products', json={'name': 'Widget2', 'sku': 'W2', 'branch_id': 2, 'quantity': 3}, headers=headers)
    assert p2_resp.status_code in (400, 403)

    # List products should only show branch 1 product
    list_resp = client.get('/inventory/products?limit=10', headers=headers)
    assert list_resp.status_code == 200
    body = list_resp.get_json()
    data = body['data']
    assert all(p['branch_id']==1 for p in data)
    assert 'pagination' in body

    # Adjust quantity
    adj_resp = client.put(f'/inventory/products/{p1_id}/adjust', json={'delta': 4}, headers=headers)
    assert adj_resp.status_code == 200
    body_adj = adj_resp.get_json()
    assert body_adj['quantity'] == 9

    # Audit log for adjustment recorded (PRODUCT.ADJUST)
    from app.models.audit import AuditLog
    audits = session.query(AuditLog).filter(AuditLog.action=='PRODUCT.ADJUST').all()
    assert audits, 'Expected PRODUCT.ADJUST audit entry'

    # Ensure diff captured
    adj_audit = audits[-1]
    changes = (adj_audit.meta or {}).get('changes')
    assert changes and 'quantity' in changes, 'Expected quantity diff in audit meta'


def test_inventory_pagination(client):
    session = get_db()
    try:
        session.rollback()
    except Exception:
        pass
    from app.models.authz import User, Role, Permission, RolePermission, UserGroup, Group, GroupRole
    from sqlalchemy import select
    u = session.query(User).filter_by(email='invpag@example.com').one_or_none()
    if not u:
        u = User(name='InvPag', email='invpag@example.com', password_hash=''); u.set_password('pw'); session.add(u)
    r = session.query(Role).filter_by(name='InvPagRole').one_or_none()
    if not r:
        r = Role(name='InvPagRole', is_system=False, description_i18n={'en': 'Inv'}); session.add(r); session.flush()
        for code in ['INV.READ', 'INV.ADJUST']:
            p = session.execute(select(Permission).where(Permission.code==code)).scalar_one_or_none()
            if not p:
                svc, action = code.split('.', 1)
                p = Permission(code=code, service=svc, action=action, description_i18n={'en': code}); session.add(p); session.flush()
            session.add(RolePermission(role_id=r.id, permission_id=p.id))
    g = session.query(Group).filter_by(name='InvPagGroup').one_or_none()
    if not g:
        g = Group(name='InvPagGroup', description_i18n={'en': 'B1'}, branch_scope={'allow': [1]}); session.add(g); session.flush()
        session.add(GroupRole(group_id=g.id, role_id=r.id))
        session.add(UserGroup(user_id=u.id, group_id=g.id))
    session.commit()
    token = _login(client, 'invpag@example.com', 'pw'); headers={'Authorization': f'Bearer {token}'}
    for i in range(5):
        client.post('/inventory/products', json={'name': f'P{i}', 'sku': f'PP{i}', 'branch_id': 1, 'quantity': i}, headers=headers)
    lst1 = client.get('/inventory/products?limit=2&offset=0', headers=headers).get_json()
    lst2 = client.get('/inventory/products?limit=2&offset=2', headers=headers).get_json()
    assert lst1['pagination']['total'] >= 5
    assert lst1['pagination']['returned'] == 2
    assert lst2['pagination']['returned'] == 2

