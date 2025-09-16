from test_utils_seed import seed_user_with_role_and_group, ensure_permissions


def test_head_roles_permissions_groups(client):
    # Seed composite user/role/group with needed perms
    seed_user_with_role_and_group(
        email='headmeta@example.com',
        role_name='HeadMetaRole',
        perm_codes=['ADMIN.ROLE.MANAGE','ADMIN.GROUP.MANAGE','ADMIN.PERMISSION.READ'],
        group_name='HeadMetaGroup',
        branch_ids=[1]
    )
    token = client.post('/iam/auth/login', json={'email': 'headmeta@example.com', 'password': 'pw'}).get_json()['access_token']
    headers={'Authorization': f'Bearer {token}'}

    # HEAD roles
    r_roles = client.head('/iam/roles?limit=5', headers=headers)
    assert r_roles.status_code == 200
    etag_roles = r_roles.headers.get('ETag'); assert etag_roles
    # conditional HEAD
    r_roles_cond = client.head('/iam/roles?limit=5', headers={**headers, 'If-None-Match': etag_roles})
    assert r_roles_cond.status_code == 304

    # HEAD groups
    r_groups = client.head('/iam/groups?limit=5', headers=headers)
    assert r_groups.status_code == 200
    etag_groups = r_groups.headers.get('ETag'); assert etag_groups
    r_groups_cond = client.head('/iam/groups?limit=5', headers={**headers, 'If-None-Match': etag_groups})
    assert r_groups_cond.status_code == 304

    # HEAD permissions
    r_perms = client.head('/iam/permissions?limit=5', headers=headers)
    assert r_perms.status_code == 200
    etag_perms = r_perms.headers.get('ETag'); assert etag_perms
    r_perms_cond = client.head('/iam/permissions?limit=5', headers={**headers, 'If-None-Match': etag_perms})
    assert r_perms_cond.status_code == 304


def test_head_orders_validators(client):
    seed_user_with_role_and_group(
        email='headorders@example.com',
        role_name='HeadOrdersRole',
        perm_codes=['SALES.READ','SALES.CREATE'],
        group_name='HeadOrdersGroup',
        branch_ids=[5]
    )
    token = client.post('/iam/auth/login', json={'email': 'headorders@example.com', 'password': 'pw'}).get_json()['access_token']
    headers={'Authorization': f'Bearer {token}'}
    # create order (branch 5 within scope)
    client.post('/sales/orders', json={'customer_name': 'HHead', 'branch_id':5, 'total_cents':1000}, headers=headers)

    r = client.head('/sales/orders?limit=5', headers=headers)
    assert r.status_code == 200
    etag = r.headers.get('ETag'); assert etag
    # conditional GET
    r2 = client.get('/sales/orders?limit=5', headers={**headers, 'If-None-Match': etag})
    assert r2.status_code == 304
    # conditional HEAD
    r3 = client.head('/sales/orders?limit=5', headers={**headers, 'If-None-Match': etag})
    assert r3.status_code == 304
