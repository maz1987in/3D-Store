from test_utils_seed import seed_user_with_role_and_group, ensure_permissions


def test_head_products_validators(client):
    # Seed user+role+group with inventory permissions
    seed_user_with_role_and_group(
        email='head_inv@example.com',
        role_name='HeadInvRole',
        perm_codes=['INV.READ', 'INV.ADJUST'],
        group_name='HeadInvGroup',
        branch_ids=[2]
    )
    token = client.post('/iam/auth/login', json={'email': 'head_inv@example.com', 'password': 'pw'}).get_json()['access_token']
    headers={'Authorization': f'Bearer {token}'}
    # Seed product
    client.post('/inventory/products', json={'name': 'HeadWidget', 'sku': 'HEADSKU', 'branch_id':2, 'quantity':1}, headers=headers)
    r = client.head('/inventory/products?limit=5', headers=headers)
    assert r.status_code == 200
    etag = r.headers.get('ETag'); lm = r.headers.get('Last-Modified'); iso = r.headers.get('X-Last-Modified-ISO')
    assert etag and lm and iso
    r2 = client.get('/inventory/products?limit=5', headers={**headers, 'If-None-Match': etag})
    assert r2.status_code == 304
    r3 = client.head('/inventory/products?limit=5', headers={**headers, 'If-None-Match': etag})
    assert r3.status_code == 304


def test_head_audit_logs_validators(client):
    # Seed user with audit-relevant permissions
    seed_user_with_role_and_group(
        email='headaudit@example.com',
        role_name='HeadAuditRole',
        perm_codes=['ADMIN.SETTINGS.MANAGE', 'ADMIN.ROLE.MANAGE'],
        group_name='HeadAuditGroup',
        branch_ids=[1]
    )
    token = client.post('/iam/auth/login', json={'email': 'headaudit@example.com', 'password': 'pw'}).get_json()['access_token']
    headers={'Authorization': f'Bearer {token}'}
    # Create an audit log by creating a role
    client.post('/iam/roles', json={'name': 'HeadAuditTempRole'}, headers=headers)
    r = client.head('/iam/audit/logs?limit=5', headers=headers)
    assert r.status_code == 200
    etag = r.headers.get('ETag'); lm = r.headers.get('Last-Modified'); iso = r.headers.get('X-Last-Modified-ISO')
    assert etag and lm and iso
    r2 = client.get('/iam/audit/logs?limit=5', headers={**headers, 'If-None-Match': etag})
    assert r2.status_code == 304
    r3 = client.head('/iam/audit/logs?limit=5', headers={**headers, 'If-None-Match': etag})
    assert r3.status_code == 304