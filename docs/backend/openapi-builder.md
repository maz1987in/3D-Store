# OpenAPI Builder (Deterministic, Programmatic)

This backend generates the OpenAPI spec in code for safety and testable determinism.

Key files
- `backend/app/openapi_builder.py` — canonical builder (re-exported via `app/openapi.py`).
- `backend/app/openapi_parts/constants.py` — entities and actions registry:
  - `ENTITIES`: `(SchemaName, domain, collection, id_param)` tuples
  - `ACTION_REGISTRY`: per-entity list of `{action, summary, permission}`
- `backend/app/openapi_parts/helpers.py` — tiny helpers for schema and headers.
- `backend/app/openapi_parts/domains/` — per-service path builders delegating to `_common.build_service_paths`.

Routes
- Spec: `/openapi.json`
- Docs: `/docs` (Redoc viewer)

Determinism & tests
- Spec JSON is assembled with stable ordering. A SHA256 snapshot in `backend/tests/openapi_spec_hash.txt` gates changes.
- Tests ensuring invariants:
  - `test_openapi.py::test_openapi_spec_hash_stable` — no drift without intent
  - `test_action_permissions.py` — `x-required-permissions` present
  - `test_action_permissions_seed_alignment.py` — action perms appear in at least one seeded role

Developer workflow
- Show current hash:
  - `PYTHONPATH=backend python -m backend.scripts.generate_spec`
- Check vs snapshot:
  - `PYTHONPATH=backend python -m backend.scripts.generate_spec --check`
- Write full JSON:
  - `PYTHONPATH=backend python -m backend.scripts.generate_spec --out backend/openapi.json`
- Update snapshot intentionally:
  - `PYTHONPATH=backend python -m backend.scripts.generate_spec --update-hash`

Extending the spec
1. Add/modify entity tuple in `ENTITIES` or action in `ACTION_REGISTRY`.
2. If needed, customize per-service builder in `openapi_parts/domains/<service>.py`.
3. Keep required permissions aligned with `backend/app/constants/permissions.py` and seeds.
4. Re-run spec check; update snapshot if intentional.

Notes
- List and single-resource GET/HEAD endpoints must include caching headers (`ETag`, `Last-Modified`, `X-Last-Modified-ISO`).
- Read endpoints auto-inject `<SERVICE>.READ`; action POSTs carry explicit required permission from the registry.
