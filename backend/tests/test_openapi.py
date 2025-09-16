def test_openapi_spec_available(client):
    resp = client.get('/openapi.json')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['openapi'].startswith('3.')
    assert '/iam/auth/login' in body['paths']


def test_docs_page(client):
    resp = client.get('/docs')
    assert resp.status_code == 200
    assert b'Redoc' in resp.data or b'redoc' in resp.data


def test_sort_parameter_components_and_usage(client):
    resp = client.get('/openapi.json')
    spec = resp.get_json()
    comps = spec['components']['parameters']
    expected = [
        'SortProductsParam','SortOrdersParam','SortPrintJobsParam','SortAccountingParam',
        'SortCatalogItemsParam','SortPurchaseOrdersParam','SortVendorsParam','SortRepairsParam'
    ]
    for name in expected:
        assert name in comps, f"Missing parameter component: {name}"
    path_map = {
        '/inventory/products': 'SortProductsParam',
        '/sales/orders': 'SortOrdersParam',
        '/print/jobs': 'SortPrintJobsParam',
        '/accounting/transactions': 'SortAccountingParam',
        '/catalog/items': 'SortCatalogItemsParam',
        '/po/purchase-orders': 'SortPurchaseOrdersParam',
        '/po/vendors': 'SortVendorsParam',
        '/repairs/tickets': 'SortRepairsParam'
    }
    for p, comp in path_map.items():
        params = spec['paths'][p]['get'].get('parameters', [])
        assert any(pr.get('$ref','').endswith(comp) for pr in params), f"{p} missing ref to {comp}"


def test_list_caching_headers_documented(client):
    resp = client.get('/openapi.json')
    spec = resp.get_json()
    # sample a few representative list endpoints for header presence
    for p in ['/sales/orders','/print/jobs','/inventory/products','/po/vendors']:
        get_op = spec['paths'][p]['get']
        hdrs = get_op['responses']['200'].get('headers', {})
        for h in ['ETag','Last-Modified','X-Last-Modified-ISO']:
            assert h in hdrs, f"{p} missing header doc {h}"


def test_openapi_spec_hash_stable(client):
    """Detect unintended spec drift. Update snapshot intentionally when making planned changes."""
    import hashlib, json, pathlib
    resp = client.get('/openapi.json')
    spec = resp.get_json()
    blob = json.dumps(spec, sort_keys=True, separators=(',',':')).encode()
    current = hashlib.sha256(blob).hexdigest()
    snapshot_path = pathlib.Path(__file__).parent / 'openapi_spec_hash.txt'
    expected = snapshot_path.read_text().strip()
    assert current == expected, f"OpenAPI spec hash changed. Old={expected} new={current}. If intentional update snapshot file." 
