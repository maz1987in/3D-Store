## 3D Store – AI Implementation Playbook

Fast, concrete guardrails for extending the Flask + Angular multi‑tenant store safely.

### Architecture & Routing
- Backend: Flask app (`backend/app/__init__.py`) registers service blueprints under prefixes: `/inventory`, `/sales`, `/print`, `/accounting`, `/catalog`, `/po`, `/repairs`, `/reports`, `/iam`.
- OpenAPI: generated programmatically (`backend/app/openapi_builder.py` via `app/openapi.py`), served at `/openapi.json`, Redoc at `/docs`.
- Determinism: spec order and hash are gated by tests (`backend/tests/test_openapi.py::test_openapi_spec_hash_stable`). Update snapshot with `python -m scripts.generate_spec --update-hash`.

### AuthZ Model (must respect)
- Permission taxonomy: SERVICE.ACTION (SALES, PRINT, ACC, INV, CAT, PO, RPR, RPT, ADMIN). Source of truth: `backend/app/constants/permissions.py` (SERVICE_ACTIONS, ROLE_PRESETS).
- Effective perms = union of direct roles + group roles at login; JWT embeds `sub, roles[], perms[], groups[], branch_ids[]`.
- Decorator at the edge: `@require_permissions(*codes)` (`backend/app/decorators/auth.py`). Use policy helpers (`backend/app/services/policy.py`) like `assert_branch_access`, `assert_owns_record` inside handlers.

### Branch Scoping & Flags
- When `AUTHZ_ENFORCE_BRANCH_SCOPE=true`, always filter queries by `branch_ids[]` from JWT (see `filter_query_by_branches`).
- Feature flags: `SELLER_SEES_ONLY_THEIR_SALES`, `PRINTER_SEES_ASSIGNED_ONLY` – enforce via policy helpers, never inline ad‑hoc checks.

### OpenAPI Invariants (tests enforce these)
- Entities and actions are declared centrally in the builder (`ENTITIES`, `ACTION_REGISTRY`). Add new actions there; the builder injects `x-required-permissions` for each POST action.
- All list/single GET and HEAD ops must expose read perms (`<SERVICE>.READ`). Tests: `test_action_permissions.py` and `test_openapi.py`.
- List and single-resource endpoints document caching headers: `ETag`, `Last-Modified`, `X-Last-Modified-ISO`; HEAD returns headers only.

### Seeding & Roles
- Idempotent seed script: `backend/scripts/seed_authz.py`
	- Normal: make seed (or `python backend/scripts/seed_authz.py`)
	- `--validate` (fail on invalid codes), `--dry-run`, `--show-roles`, `--export-json`, `--fail-if-changed <sha>`.
- Owner role expands to all permissions; Manager is broad but excludes `ADMIN.*`. Never mutate system roles to satisfy one user—use direct user role assignment.

### Dev Workflow (Makefile shortcuts)
- `make venv` → create venv and install backend deps.
- `make run-api` → FLASK dev server on 5000.
- `make migrate` → Alembic upgrade head (when migrations exist).
- `make seed` → seed permissions/roles; `make test` → run backend tests.
- Spec CLI: `python -m scripts.generate_spec [--out backend/openapi.json|--check|--update-hash]`.

### Patterns to follow (with examples)
- Route guard: `@require_permissions('ACC.APPROVE')` then `policy.assert_branch_access(branch_id)` before mutating.
- Audit & i18n: mutations in financial/security domains should be audited; prefer `*_i18n` fields over hardcoded English.
- Client gating: Angular uses JWT perms[] for menus/actions; branch selector must set `X-Branch-Id` header (server will intersect with JWT claims).

### Pitfalls to avoid
- Don’t trust client-claimed branch id—always intersect with JWT `branch_ids[]`.
- Avoid permission string typos—import from constants; never broaden a role silently; prevent removing the last Owner (policy check exists and is tested).

### Key references
- AuthZ constants: `backend/app/constants/permissions.py`
- Policy helpers: `backend/app/services/policy.py`
- Auth decorator: `backend/app/decorators/auth.py`
- OpenAPI builder: `backend/app/openapi_builder.py` (+ `scripts/generate_spec.py`); constants in `backend/app/openapi_parts/constants.py`
- Tests (contract gates): `backend/tests/test_action_permissions.py`, `backend/tests/test_openapi.py`

When unsure, anchor on: (a) which SERVICE, (b) what ACTION name, (c) what scoping applies. If all three are clear, proceed; otherwise clarify. Keep this file tight—extend only when a new invariant is enforced by code/tests.