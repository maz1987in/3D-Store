from app import get_db
from app.models.authz import User, Role, Permission, RolePermission, UserRole

def _login(client, email, password):
    resp = client.post('/iam/auth/login', json={'email': email, 'password': password})
    assert resp.status_code == 200
    return resp.get_json()['access_token']


def test_groups_endpoints_require_permission(client):
    session = get_db()
    # Create user without any permissions
    user = User(name='NoPerm', email='noperm@example.com', password_hash='')
    user.set_password('pw')
    session.add(user)
    session.commit()
    token = _login(client, 'noperm@example.com', 'pw')
    headers = {'Authorization': f'Bearer {token}'}
    # Expect 403 for listing groups
    resp = client.get('/iam/groups', headers=headers)
    assert resp.status_code == 403
    # Expect 403 for creating groups
    resp2 = client.post('/iam/groups', json={'name': 'ShouldFail'}, headers=headers)
    assert resp2.status_code == 403


def test_audit_logs_require_settings_permission_and_group_perm_works(client):
    session = get_db()
    # Ensure permissions exist
    p_group = session.query(Permission).filter_by(code='ADMIN.GROUP.MANAGE').one_or_none()
    if not p_group:
        p_group = Permission(code='ADMIN.GROUP.MANAGE', service='ADMIN', action='GROUP.MANAGE', description_i18n={'en': 'manage groups'})
        session.add(p_group); session.flush()
    p_settings = session.query(Permission).filter_by(code='ADMIN.SETTINGS.MANAGE').one_or_none()
    if not p_settings:
        p_settings = Permission(code='ADMIN.SETTINGS.MANAGE', service='ADMIN', action='SETTINGS.MANAGE', description_i18n={'en': 'settings'})
        session.add(p_settings); session.flush()
    # User with only group manage
    u = User(name='GroupOnly', email='grouponly@example.com', password_hash='')
    u.set_password('pw')
    session.add(u)
    role_group = Role(name='GroupOnlyRole', is_system=False, description_i18n={'en': 'Group role'})
    session.add(role_group); session.flush()
    session.add(RolePermission(role_id=role_group.id, permission_id=p_group.id))
    session.add(UserRole(user_id=u.id, role_id=role_group.id))
    session.commit()
    token = _login(client, 'grouponly@example.com', 'pw')
    headers = {'Authorization': f'Bearer {token}'}
    # Should access groups list
    ok = client.get('/iam/groups', headers=headers)
    assert ok.status_code in (200, 204)
    # Should be forbidden for audit logs
    audit = client.get('/iam/audit/logs', headers=headers)
    assert audit.status_code == 403

