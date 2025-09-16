from app import get_db
from app.models.authz import User, Role, Permission, RolePermission, UserRole


def _login(client, email, password):
    r = client.post('/iam/auth/login', json={'email': email, 'password': password})
    assert r.status_code == 200
    return r.get_json()['access_token']


def test_roles_groups_permissions_pagination(client):
    session = get_db()
    # user
    u = User(name='PagAdmin', email='pagadmin@example.com', password_hash='')
    u.set_password('pw')
    session.add(u)
    # permissions needed
    perm_role = session.query(Permission).filter_by(code='ADMIN.ROLE.MANAGE').one_or_none()
    if not perm_role:
        perm_role = Permission(code='ADMIN.ROLE.MANAGE', service='ADMIN', action='ROLE.MANAGE', description_i18n={'en': 'manage roles'})
        session.add(perm_role); session.flush()
    perm_group = session.query(Permission).filter_by(code='ADMIN.GROUP.MANAGE').one_or_none()
    if not perm_group:
        perm_group = Permission(code='ADMIN.GROUP.MANAGE', service='ADMIN', action='GROUP.MANAGE', description_i18n={'en': 'manage groups'})
        session.add(perm_group); session.flush()
    # role for user
    r = Role(name='PagAdminRole', is_system=False, description_i18n={'en': 'pagination admin'})
    session.add(r); session.flush()
    session.add(RolePermission(role_id=r.id, permission_id=perm_role.id))
    session.add(RolePermission(role_id=r.id, permission_id=perm_group.id))
    session.add(UserRole(user_id=u.id, role_id=r.id))
    session.commit()

    token = _login(client, 'pagadmin@example.com', 'pw')
    headers={'Authorization': f'Bearer {token}'}

    # Create extra roles to exceed limit
    for i in range(3):
        client.post('/iam/roles', json={'name': f'PagRole{i}'}, headers=headers)
    # Create groups
    for i in range(3):
        client.post('/iam/groups', json={'name': f'PagGroup{i}'}, headers=headers)

    roles_resp = client.get('/iam/roles?limit=2&offset=0', headers=headers).get_json()
    assert 'pagination' in roles_resp and roles_resp['pagination']['limit'] == 2
    assert roles_resp['pagination']['returned'] <= 2
    assert roles_resp['pagination']['total'] >= roles_resp['pagination']['returned']

    groups_resp = client.get('/iam/groups?limit=2&offset=0', headers=headers).get_json()
    assert 'pagination' in groups_resp and groups_resp['pagination']['limit'] == 2
    assert groups_resp['pagination']['returned'] <= 2

    perms_resp = client.get('/iam/permissions?limit=5', headers=headers).get_json()
    assert 'pagination' in perms_resp
    assert perms_resp['pagination']['limit'] == 5
    assert perms_resp['pagination']['returned'] <= 5
    assert perms_resp['pagination']['total'] >= perms_resp['pagination']['returned']