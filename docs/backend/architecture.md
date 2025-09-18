# Architecture Overview

The 3D Store backend is a Flask application exposing a multi-tenant, policy‑driven Identity & Access Management (IAM) layer with extensible domain services. The frontend (planned Angular) consumes JWT tokens embedding authorization claims.

## Layers
- API (Blueprints): Currently `iam` blueprint for Auth + IAM operations.
- Decorators: `@require_permissions` and `@audit_log` for authorization gates & mutation auditing.
- Services: `policy` (permission aggregation, branch scoping, owner safeguards), `audit` (low-level audit writer).
- Persistence: SQLAlchemy ORM, single metadata (`authz` + `audit`) using SQLite (dev) / pluggable via `DATABASE_URL`.
- Docs: Programmatic OpenAPI builder with deterministic hash + Redoc viewer.
- Caching: List endpoints expose ETag + Last-Modified validators (see `caching-and-conditional-requests.md`).

## Entity Relationships
```
User -(UserRole)-> Role -(RolePermission)-> Permission
User -(UserGroup)-> Group -(GroupRole)-> Role
Group.branch_scope => contributes to JWT.claims.branch_ids
```
Effective permissions = union of roles (direct + via groups) -> RolePermission -> Permission.

## Authorization Flow
1. User authenticates via `/iam/auth/login`.
2. Service computes effective perms + branch_ids and issues JWT.
3. Each protected endpoint uses `@require_permissions` to validate required codes.
4. Branch-sensitive endpoints (future domain) apply policy helpers (`assert_branch_access`).

## Auditing Flow
- Mutating endpoints decorate with `@audit_log(action, ...)`.
- Decorator captures response, optional before snapshot (for diffs), and persists an `AuditLog` record (including perms snapshot from JWT).
- Read endpoints generally not audited unless sensitive.

## Error Handling
A global exception handler normalizes all errors into:
```json
{
  "error": { "status": 400, "title": "Bad Request", "detail": "..." }
}
```
Unhandled errors → status 500 with generic detail.

## Extensibility
Add new domain modules by:
1. Defining model(s) (include `branch_id` where appropriate).
2. Adding permissions following `SERVICE.ACTION` taxonomy.
3. Seeding new permissions + attaching them to roles (do NOT over-broaden existing roles without review).
4. Implementing endpoints gated by `@require_permissions`.
5. Adding policy enforcement + audits.
6. Updating the OpenAPI builder (centralized, programmatic):
  - Add entity/action metadata in `backend/app/openapi_parts/constants.py` (ENTITIES, ACTION_REGISTRY).
  - Domain paths are built via per-service modules in `backend/app/openapi_parts/domains/` using the common `_common.build_service_paths`.
  - The canonical builder is `backend/app/openapi_builder.py` (publicly re-exported by `app/openapi.py`).
  - Verify determinism: `python -m backend.scripts.generate_spec --check` (set `PYTHONPATH=backend`).
  - Update snapshot hash intentionally when planned changes occur: `--update-hash`.

See `authz-model.md` for deep IAM details.
