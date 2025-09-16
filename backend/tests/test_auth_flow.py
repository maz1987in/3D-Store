from app.models.authz import User
from app import get_db
from sqlalchemy import select

def test_login_and_me(client):
    # Seed a user manually
    session = get_db()
    u = User(name='T', email='t@example.com', password_hash='')
    u.set_password('pw')
    session.add(u)
    session.commit()

    # Login
    resp = client.post('/iam/auth/login', json={'email': 't@example.com', 'password': 'pw'})
    assert resp.status_code == 200, resp.get_json()
    token = resp.get_json()['access_token']

    me = client.get('/iam/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert me.status_code == 200
    body = me.get_json()
    assert body['email'] == 't@example.com'
