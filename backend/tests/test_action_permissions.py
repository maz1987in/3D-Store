def test_all_action_endpoints_have_permissions(client):
    resp = client.get('/openapi.json')
    assert resp.status_code == 200
    spec = resp.get_json()
    paths = spec["paths"]
    missing = []
    action_endpoints = 0
    for path, ops in paths.items():
        for method, op in ops.items():
            # Only POST action endpoints should have been annotated explicitly in builder
            if method != "post":
                continue
            # Heuristic: action endpoints are POST on resource id subpath with trailing action token
            segments = path.strip("/").split("/")
            if len(segments) < 3:
                # likely /iam/auth/login or similar
                continue
            # pattern: /domain/collection/{id}/action
            if segments[-2].startswith("{") and not segments[-1].startswith("{"):
                action_endpoints += 1
                if "x-required-permissions" not in op or not op["x-required-permissions"]:
                    missing.append(path)
    assert not missing, f"Action endpoints missing x-required-permissions: {missing}"
    assert action_endpoints > 0, "No action endpoints detected; test may be misconfigured"


def test_read_endpoints_have_read_permissions(client):
    resp = client.get('/openapi.json')
    assert resp.status_code == 200
    spec = resp.get_json()
    paths = spec["paths"]
    read_missing = []
    for path, ops in paths.items():
        for method in ("get", "head"):
            if method not in ops:
                continue
            op = ops[method]
            # Skip auth endpoints intentionally open
            if path.startswith("/iam/auth/"):
                continue
            if "x-required-permissions" not in op:
                read_missing.append(f"{method.upper()} {path}")
    assert not read_missing, f"Read endpoints missing x-required-permissions: {read_missing}"
