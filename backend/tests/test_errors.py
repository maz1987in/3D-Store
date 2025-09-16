def test_unknown_path_returns_error_json(client):
    resp = client.get('/non-existent-path')
    # Flask default 404 should be wrapped by error handler
    assert resp.status_code == 404
    body = resp.get_json()
    assert 'error' in body
    assert body['error']['status'] == 404
    assert 'detail' in body['error']


def test_internal_error_shape(client, monkeypatch):
    # Create a user with ADMIN.ROLE.MANAGE and monkeypatch the route to raise
    from app import get_db
    from app.models.authz import User, Role, Permission, RolePermission, UserRole
    from app.routes import iam
    session = get_db()
    u = User(name='ErrUser', email='err@example.com', password_hash='')
    u.set_password('pw'); session.add(u)
    role = Role(name='ErrRole', is_system=False, description_i18n={'en': 'err'})
    session.add(role); session.flush()
    perm = session.query(Permission).filter_by(code='ADMIN.ROLE.MANAGE').one_or_none()
    if not perm:
        perm = Permission(code='ADMIN.ROLE.MANAGE', service='ADMIN', action='ROLE.MANAGE', description_i18n={'en': 'roles'})
        session.add(perm); session.flush()
    session.add(RolePermission(role_id=role.id, permission_id=perm.id))
    session.add(UserRole(user_id=u.id, role_id=role.id))
    session.commit()
    token = client.post('/iam/auth/login', json={'email': 'err@example.com', 'password': 'pw'}).get_json()['access_token']
    # Monkeypatch AFTER login so auth works; only break roles listing
    import app.routes.iam as iam_mod
    class BoomSession:
        def execute(self, *a, **k):
            raise RuntimeError('explode')
    def boom_get_db():
        return BoomSession()
    monkeypatch.setattr(iam_mod, 'get_db', boom_get_db)
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.get('/iam/roles', headers=headers)
    assert resp.status_code == 500
    body = resp.get_json()
    assert body['error']['status'] == 500
    assert body['error']['title'] == 'Internal Server Error'
    # No need to restore for test isolation (process ends). Optional restore omitted.
    assert resp.status_code == 500
    body = resp.get_json()
    assert body['error']['status'] == 500
    assert body['error']['title'] == 'Internal Server Error'
