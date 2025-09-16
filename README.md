# 3D Store Monorepo

Structure:
- `backend/` Flask + SQLAlchemy + JWT (multi-tenant RBAC foundation)
- `frontend/` (Angular app placeholder)

See `backend/README.md` for current implementation details.

## Planned Frontend
Angular app providing:
- Auth flow consuming JWT
- PermissionGuard & directive for action gating
- Branch selector component adding `X-Branch-Id` header

## Planned Backend Enhancements
- Alembic migrations & seed runner
- Full IAM CRUD endpoints
- Audit logging & reporting

See `TODO.md` for the evolving, detailed enhancement backlog (FSM extensions, reporting pivots, permissions hardening, sorting & metrics expansions).

Refer to `.github/copilot-instructions.md` for architectural invariants.

### Backend Features Snapshot
- Multi-field sorting via unified `sort` parameter across inventory, sales, print, accounting, catalog, purchasing, vendors, repairs.
- Deterministic list validators: `ETag`, `Last-Modified`, `X-Last-Modified-ISO` (supports 304 / HEAD optimization).
- Single-resource conditional caching currently for Vendors & Inventory Products (more can be extended easily).

See `backend/README.md` ("List Endpoints: Multi-Field Sorting" & "Conditional Caching") for full details and allowed fields.

### OpenAPI & Determinism
The spec is generated programmatically (no static YAML) for safety and reproducibility. A hash snapshot (`tests/openapi_spec_hash.txt`) guards against unintended drift. Extend via `backend/app/openapi_clean.py` and update the hash intentionally when planned changes occur.

## Continuous Integration
Workflow: `.github/workflows/ci.yml`

Pipeline stages (per Python 3.9 & 3.11 matrix):
1. Checkout & environment setup
2. Install dependencies (cached)
3. Linting (Ruff) – style & basic errors
4. Type checking (Mypy) – loose config (ignore_missing_imports)
5. Seed validation & drift detection (`seed_authz.py --validate --fail-if-changed --dry-run`)
6. Test execution with coverage (XML uploaded as artifact)
7. Seed export JSON artifact for auditing role/permission state
8. Vulnerability scan (pip-audit)

Artifacts:
- `coverage-<python-version>`: Coverage XML
- `seed-export-<python-version>`: Snapshot of permissions & roles

Failures will block merge if:
- Lint/type issues are detected
- Seed drift (permission/role mismatch) occurs
- Tests fail or coverage job errors
- Vulnerabilities discovered by `pip-audit`

Next CI enhancements (future):
- Enforce minimum coverage threshold
- OpenAPI spec generation & diff gating
- SBOM & dependency review
- Caching compiled wheels
