from app import get_db
from app.models.authz import User, Role, Permission, RolePermission, UserRole

def _login(client, email, password):
    r = client.post('/iam/auth/login', json={'email': email, 'password': password})
    assert r.status_code == 200
    return r.get_json()['access_token']

def test_audit_logs_conditional(client):
    session = get_db()
    # Ensure permissions
    needed = ['ADMIN.SETTINGS.MANAGE', 'ADMIN.ROLE.MANAGE']
    perm_objs = {}
    for code in needed:
        p = session.query(Permission).filter_by(code=code).one_or_none()
        if not p:
            svc, action = code.split('.',1)
            p = Permission(code=code, service=svc, action=action, description_i18n={'en': code})
            session.add(p); session.flush()
        perm_objs[code] = p
    user = session.query(User).filter_by(email='auditcache@example.com').one_or_none()
    if not user:
        user = User(name='AuditCache', email='auditcache@example.com', password_hash='')
        user.set_password('pw'); session.add(user); session.flush()
    role = session.query(Role).filter_by(name='AuditCacheRole').one_or_none()
    if not role:
        role = Role(name='AuditCacheRole', is_system=False, description_i18n={'en': 'audit cache'}); session.add(role); session.flush()
        for p in perm_objs.values():
            session.add(RolePermission(role_id=role.id, permission_id=p.id))
    # Link user-role
    if not session.query(UserRole).filter_by(user_id=user.id, role_id=role.id).one_or_none():
        session.add(UserRole(user_id=user.id, role_id=role.id))
    session.commit()
    token = _login(client, 'auditcache@example.com', 'pw')
    headers={'Authorization': f'Bearer {token}'}
    # Generate an audit log entry by creating a role (ROLE.CREATE has audit decorator)
    client.post('/iam/roles', json={'name': 'CacheRoleTest'}, headers=headers)
    first = client.get('/iam/audit/logs?limit=5', headers=headers)
    assert first.status_code == 200
    etag = first.headers.get('ETag'); assert etag
    lm = first.headers.get('Last-Modified'); assert lm
    second = client.get('/iam/audit/logs?limit=5', headers={**headers, 'If-None-Match': etag})
    assert second.status_code == 304
    assert second.headers.get('ETag') == etag
    # If-Modified-Since path
    third = client.get('/iam/audit/logs?limit=5', headers={**headers, 'If-Modified-Since': lm})
    assert third.status_code == 304
    assert third.headers.get('ETag') == etag