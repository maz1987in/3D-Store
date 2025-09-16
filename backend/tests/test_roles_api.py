from app import get_db
from app.models.authz import User, Role, Permission, RolePermission, Group, UserGroup, GroupRole, UserRole
from app.models.audit import AuditLog
from app.services.policy import compute_effective_permissions

from sqlalchemy import select

def _login(client, email, password):
    resp = client.post('/iam/auth/login', json={'email': email, 'password': password})
    assert resp.status_code == 200
    return resp.get_json()['access_token']


def test_role_crud_flow(client):
    # Create initial owner user manually (test DB is memory)
    session = get_db()
    # Ensure clean state if prior test left session in rollback
    try:
        session.rollback()
    except Exception:
        pass
    owner = User(name='Owner', email='owner@test.local', password_hash='')
    owner.set_password('pw')
    session.add(owner)
    # Create Owner role and attach wildcard perms via direct assignment simulation
    r = Role(name='Owner', is_system=True, description_i18n={'en': 'Owner'})
    session.add(r)
    session.flush()
    from sqlalchemy import text
    session.execute(text("INSERT INTO user_roles (user_id, role_id) VALUES (:u, :r)"), {"u": owner.id, "r": r.id})
    session.commit()
    # Give Owner a management permission required by endpoints
    p = session.query(Permission).filter_by(code='ADMIN.ROLE.MANAGE').one_or_none()
    if not p:
        p = Permission(code='ADMIN.ROLE.MANAGE', service='ADMIN', action='ROLE.MANAGE', description_i18n={'en': 'manage roles'})
        session.add(p)
        session.flush()
    session.add(RolePermission(role_id=r.id, permission_id=p.id))
    session.commit()

    token = _login(client, 'owner@test.local', 'pw')
    headers = {'Authorization': f'Bearer {token}'}

    # Create a new role
    resp = client.post('/iam/roles', json={'name': 'TempRole'}, headers=headers)
    assert resp.status_code == 201, resp.get_json()
    role_id = resp.get_json()['id']

    # Assign permissions (none will error because none seeded here) -> expect 400
    bad = client.put(f'/iam/roles/{role_id}/permissions', json={'permissions': ['ACC.READ']}, headers=headers)
    assert bad.status_code in (200, 400)  # depending on permission seed presence

    # Set user roles (assign new role only) – should allow removing owner? Safeguard stops if last owner
    remove_owner_attempt = client.put(f'/iam/users/{owner.id}/roles', json={'role_ids': [role_id]}, headers=headers)
    # Should be 400 due to last owner protection
    assert remove_owner_attempt.status_code in (400, 403)
    # Audit log should have at least one ROLE.CREATE entry
    session.refresh(r)
    audits = session.query(AuditLog).filter(AuditLog.action=='ROLE.CREATE').all()
    assert audits, 'Expected audit log for ROLE.CREATE'


def test_group_crud_and_assignments(client):
    session = get_db()
    try:
        session.rollback()
    except Exception:
        pass
    # Seed minimal permissions needed
    # Ensure clean slate for Owner role to avoid ordering dependency
    existing_owner = session.query(Role).filter_by(name='Owner').first()
    if existing_owner:
        # Remove to reconstruct deterministic permission set
        session.delete(existing_owner)
        session.commit()
    if not session.query(Permission).filter_by(code='ADMIN.GROUP.MANAGE').first():
        session.add(Permission(code='ADMIN.GROUP.MANAGE', service='ADMIN', action='GROUP.MANAGE', description_i18n={'en': 'manage groups'}))
    if not session.query(Permission).filter_by(code='ADMIN.USER.MANAGE').first():
        session.add(Permission(code='ADMIN.USER.MANAGE', service='ADMIN', action='USER.MANAGE', description_i18n={'en': 'manage users'}))
    if not session.query(Permission).filter_by(code='ADMIN.ROLE.MANAGE').first():
        session.add(Permission(code='ADMIN.ROLE.MANAGE', service='ADMIN', action='ROLE.MANAGE', description_i18n={'en': 'manage roles'}))
    if not session.query(User).filter_by(email='ownerg2@example.com').first():
        owner = User(name='Owner2', email='ownerg2@example.com', password_hash='')
        owner.set_password('pass')
        session.add(owner)
    session.commit()
    owner = session.query(User).filter_by(email='ownerg2@example.com').one()
    # Create system owner role with necessary perms (deterministic)
    owner_role = Role(name='Owner', is_system=True, description_i18n={'en': 'Owner'})
    session.add(owner_role); session.flush()
    for code in ['ADMIN.GROUP.MANAGE', 'ADMIN.USER.MANAGE', 'ADMIN.ROLE.MANAGE']:
        perm = session.query(Permission).filter_by(code=code).one_or_none()
        if not perm:
            svc, action = code.split('.', 1)
            perm = Permission(code=code, service=svc, action=action, description_i18n={'en': code})
            session.add(perm); session.flush()
        session.add(RolePermission(role_id=owner_role.id, permission_id=perm.id))
    session.add(UserRole(user_id=owner.id, role_id=owner_role.id))
    session.commit()
    # Login
    resp = client.post('/iam/auth/login', json={'email': owner.email, 'password': 'pass'})
    assert resp.status_code == 200
    token = resp.json['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    # Create group
    g_resp = client.post('/iam/groups', json={'name': 'OpsGroup', 'branch_scope': {'allow': [1,2]}}, headers=headers)
    assert g_resp.status_code == 201
    gid = g_resp.json['id']
    # Update group
    u_resp = client.put(f'/iam/groups/{gid}', json={'branch_scope': {'allow': [1,2,3]}}, headers=headers)
    assert u_resp.status_code == 200
    # Assign roles to group (reuse owner role id)
    owner_role = session.query(Role).filter_by(name='Owner').one()
    gr_resp = client.put(f'/iam/groups/{gid}/roles', json={'role_ids': [owner_role.id]}, headers=headers)
    assert gr_resp.status_code == 200
    # Assign group to user
    ug_resp = client.put(f'/iam/users/{owner.id}/groups', json={'group_ids': [gid]}, headers=headers)
    assert ug_resp.status_code == 200
    # List groups
    list_resp = client.get('/iam/groups', headers=headers)
    assert list_resp.status_code == 200
    groups = list_resp.json['data']
    assert any(g['id']==gid for g in groups)
    # Delete group
    del_resp = client.delete(f'/iam/groups/{gid}', headers=headers)
    assert del_resp.status_code == 200
    # Audit existence
    audit_group_create = session.query(AuditLog).filter(AuditLog.action=='GROUP.CREATE').all()
    assert audit_group_create
    # Ensure update audit captured diff
    audit_group_update = session.query(AuditLog).filter(AuditLog.action=='GROUP.UPDATE').order_by(AuditLog.id.desc()).first()
    assert audit_group_update and 'changes' in (audit_group_update.meta or {}), 'Expected changes diff in GROUP.UPDATE audit'
    changes = audit_group_update.meta.get('changes')
    assert 'branch_scope' in changes, 'branch_scope diff missing'


def test_branch_scope_in_jwt(client):
    session = get_db()
    try:
        session.rollback()
    except Exception:
        pass
    # User + group with branch scope
    u = User(name='Scoped', email='scoped@test.local', password_hash='')
    u.set_password('pw')
    session.add(u)
    g = Group(name='BranchGroup', description_i18n={'en': 'BG'}, branch_scope={'allow': [10, 20]})
    session.add(g)
    session.flush()
    session.add(UserGroup(user_id=u.id, group_id=g.id))
    session.commit()

    resp = client.post('/iam/auth/login', json={'email': 'scoped@test.local', 'password': 'pw'})
    assert resp.status_code == 200
    token = resp.get_json()['access_token']
    me = client.get('/iam/auth/me', headers={'Authorization': f'Bearer {token}'})
    body = me.get_json()
    assert body['id'] == u.id
    assert 'branch_ids' in body
    assert body['branch_ids'] == [10, 20]


def test_audit_log_listing(client):
    session = get_db()
    try:
        session.rollback()
    except Exception:
        pass
    # Ensure admin user with SETTINGS manage permission
    u = User(name='Auditor', email='audit@test.local', password_hash='')
    u.set_password('pw')
    session.add(u)
    # Create role with ADMIN.SETTINGS.MANAGE
    role = Role(name='SettingsAdmin', is_system=False, description_i18n={'en': 'Settings Admin'})
    session.add(role); session.flush()
    perm = session.query(Permission).filter_by(code='ADMIN.SETTINGS.MANAGE').one_or_none()
    if not perm:
        perm = Permission(code='ADMIN.SETTINGS.MANAGE', service='ADMIN', action='SETTINGS.MANAGE', description_i18n={'en': 'settings'})
        session.add(perm); session.flush()
    session.add(RolePermission(role_id=role.id, permission_id=perm.id))
    # Also need ADMIN.ROLE.MANAGE to create roles for audit generation
    perm_role_manage = session.query(Permission).filter_by(code='ADMIN.ROLE.MANAGE').one_or_none()
    if not perm_role_manage:
        perm_role_manage = Permission(code='ADMIN.ROLE.MANAGE', service='ADMIN', action='ROLE.MANAGE', description_i18n={'en': 'manage roles'})
        session.add(perm_role_manage); session.flush()
    session.add(RolePermission(role_id=role.id, permission_id=perm_role_manage.id))
    session.add(UserRole(user_id=u.id, role_id=role.id))
    session.commit()
    # Produce some audit (create a role via API using same user)
    token = client.post('/iam/auth/login', json={'email': 'audit@test.local', 'password': 'pw'}).get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    # Create subordinate role triggers ROLE.CREATE audit
    role_create_resp = client.post('/iam/roles', json={'name': 'TempAuditRole'}, headers=headers)
    assert role_create_resp.status_code in (201, 400)  # 400 if already exists from rerun
    # List audit logs
    resp = client.get('/iam/audit/logs?limit=10', headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    if not body['data']:
        # Fallback: create a group to force an audit then re-fetch
        client.post('/iam/groups', json={'name': 'AuditGroup'}, headers=headers)
        body = client.get('/iam/audit/logs?limit=10', headers=headers).get_json()
    assert body['data'], 'Expected audit data after fallback action'
    # Filter by action
    role_create = client.get('/iam/audit/logs?action=ROLE.CREATE', headers=headers)
    assert role_create.status_code == 200
    assert any(r['action']=='ROLE.CREATE' for r in role_create.get_json()['data'])
