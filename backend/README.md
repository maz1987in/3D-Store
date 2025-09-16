# 3D Store (Scaffold)

Initial scaffold focusing on multi-tenant RBAC foundation.

## Run (Dev)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python - <<'PY'
from app import create_app
app = create_app()
print('App created, run a WSGI server (e.g., flask run) after setting FLASK_APP.')
PY
```

## Next Build Steps
- Implement migrations (alembic init) & generate tables from models.
- Implement seed runner using `seeds/permissions_roles.py`.
- Flesh out IAM endpoints (roles, groups, users).
- Add JWT login and effective permission resolution logic.
- Introduce tests for permission resolution & 403 paths.

Refer to `.github/copilot-instructions.md` for invariants.

## List Endpoints: Multi-Field Sorting
Most list endpoints now accept a unified `sort` query parameter supporting multi-field ordering:

Pattern: `?sort=field1,-field2,field3`

Rules:
- Comma separated list of fields; prefix any field with `-` for descending.
- Unknown / disallowed fields are ignored (server falls back to default tie-breaker `id`).
- Stable: an implicit `id` ascending tie-breaker is always appended to guarantee deterministic pagination.

Allowed fields by resource:
- Inventory Products: `name, sku, updated_at, id`
- Sales Orders: `customer_name, status, total_cents, updated_at, id`
- Print Jobs: `status, updated_at, id`
- Accounting Transactions: `status, amount_cents, updated_at, id`
- Catalog Items: `price_cents, name, updated_at, id`
- Purchase Orders: `vendor_name, status, total_cents, updated_at, id`
- Vendors: `name, status, updated_at, id`
- Repair Tickets: `customer_name, status, updated_at, id`

Examples:
```
/sales/orders?sort=-updated_at,status
/po/purchase-orders?sort=vendor_name,-total_cents
/catalog/items?sort=price_cents,-updated_at
```

## Conditional Caching (ETag / Last-Modified)
List endpoints emit these headers to enable client-side caching & 304 validation:
- `ETag`: Strong validator derived from a stable hash of row payload slice + pagination window.
- `Last-Modified`: RFC1123 GMT timestamp of most recent row's `updated_at`.
- `X-Last-Modified-ISO`: ISO8601 UTC variant (client convenience; not standard but explicit).

Clients MAY send:
- `If-None-Match: <etag>` and/or
- `If-Modified-Since: <Last-Modified>`

Server replies `304 Not Modified` with no body (HEAD always produces an empty body) when validators match current state.

Single-resource conditional validators currently implemented for:
- Vendors (`/po/vendors/{id}` GET/HEAD)
- Inventory Products (`/inventory/products/{id}` GET/HEAD)

Other domains (orders, print jobs, repairs, purchase orders, accounting transactions) currently provide validators only on list endpoints; single-resource conditional support can be added using the same pattern (compute ETag + latest timestamp, unify GET+HEAD logic) when needed.

## OpenAPI Spec Notes
The lightweight programmatic builder (`app/openapi_clean.py` exported via `app/openapi.py`) generates a deterministic minimal spec:
- Auth endpoints: `/iam/auth/login`, `/iam/auth/me`
- For each core entity: list + single GET/HEAD with caching headers (`ETag`, `Last-Modified`, `X-Last-Modified-ISO`).
- Reusable parameter components: `LimitParam`, `OffsetParam`, and per-entity `Sort*Param` objects.

Determinism:
- Spec assembly orders dict keys and tags alphabetically.
- Tests snapshot the canonical JSON hash (`tests/openapi_spec_hash.txt`). Any intentional change requires updating this file.

Finite State Machine Metadata:
- `x-transitions` extension added for `PrintJob` and `AccountingTransaction` schemas (consumed by FSM tests).
 - Additional lifecycle-enabled entities now annotated: `Order`, `PurchaseOrder`, `RepairTicket`, `CatalogItem` for status toggle, plus others as added.

Action Endpoints & State Transitions:
The spec now programmatically adds action (state transition / non-CRUD) endpoints immediately alongside single-resource paths. Example patterns:
```
/print/jobs/{job_id}/start        POST  (PRINT.START)
/print/jobs/{job_id}/complete     POST  (PRINT.COMPLETE)
/sales/orders/{order_id}/approve  POST  (SALES.APPROVE)
/sales/orders/{order_id}/cancel   POST  (SALES.CANCEL)
/po/purchase-orders/{po_id}/receive POST (PO.RECEIVE)
/repairs/tickets/{ticket_id}/start POST  (RPR.MANAGE)
/accounting/transactions/{tx_id}/approve POST (ACC.APPROVE)
/catalog/items/{item_id}/archive  POST  (CAT.UPDATE)
```

Guidelines:
- Use POST for idempotent-ish workflow transitions to keep semantics simple (body rarely needed; can evolve later for payloads like notes, reasons).
- Each transition audited (`@audit_log`) with diff of status (and assignment fields when relevant) to form a tamper trail.
- `x-transitions` sequence lists every distinct status string (not edges). Edge validation lives in server FSM validators.

`x-required-permissions` Metadata:
Every operation is annotated (builder heuristic) so front-end can: (a) hide gated UI affordances early, (b) perform optimistic navigation permission checks before 401/403 round-trip.

Rules applied by builder:
- List + single GET/HEAD map to `<SERVICE>.READ`.
- Print actions map to `PRINT.START` / `PRINT.COMPLETE`.
- Order actions map individually: APPROVE / FULFILL / COMPLETE / CANCEL.
- PurchaseOrder actions: RECEIVE, CLOSE.
- Repairs all transitions use consolidated `RPR.MANAGE` (single controlling permission).
- Accounting actions: APPROVE / PAY / REJECT (REJECT shares `ACC.APPROVE`).
- Catalog archive / activate share `CAT.UPDATE` (mutation authority).
- Inventory product adjustments use `INV.ADJUST` (non-action currently; future action endpoints should follow same pattern).

Why not rely solely on server responses?
- Spec-level exposure allows build-time menu generation & prevents client divergence when feature flags appear.
- Puts permission mapping under testable deterministic spec hashing (diff surfaces accidental broadening).

Extending with New Actions:
1. Add FSM edge logic + permission constant (if new) in code.
2. Add action route + `@require_permissions` + `@audit_log` (diff keys, pre-fetch snapshot).
3. Insert action endpoint generation branch in builder (mirroring pattern) or generalize if many similar.
4. Add expected permission to heuristic in builder OR (future) migrate to a centralized registry list consumed by the builder.
5. Update tests + snapshot hash.

Future Hardening Ideas:
- Replace heuristic with declarative `ACTION_REGISTRY = [{path_suffix, perm, summary, schema}]` consumed by builder to eliminate duplication.
- Add `x-transition-rules` object: map of `from_status -> [allowed_statuses]` for richer client-side disable states (currently implicit server-side only).
- Emit `x-audit-event` per operation to allow UI to surface “this action will be audited” badge.
- Gate CI to ensure every `POST */*/{id}/*` action has `x-required-permissions` and returns a schema.

Client Consumption Pattern (Recommended):
1. Load OpenAPI once post-auth; index by operationId.
2. Derive actionable buttons per resource row by intersecting row.status with local transition map and user perms from JWT.
3. Use ETag/Last-Modified on action responses (optionally extend server endpoints to include validators post-mutation for cache refresh events).

Migration Path (Existing Endpoints):
- Already-created action endpoints required no spec patching beyond builder addition; runtime code unchanged.
- Downstream clients can start reading `x-required-permissions` immediately without waiting for version bump.

Pitfalls Avoided:
- Avoid embedding permission names in descriptions (use extension field instead for machine clarity).
- No partial duplication of FSM edge lists in spec—single list of statuses prevents drift.

Minimal Example Snippet (spec fragment):
```json
"/sales/orders/{order_id}/approve": {
	"post": {
		"summary": "Approve order",
		"x-required-permissions": ["SALES.APPROVE"],
		"responses": {"200": {"description": "OK"}}
	}
}
```

Extending the Spec (recommended approach):
1. Add new schema or parameter definitions inside the builder (central place ensures reuse).
2. Programmatically add new paths; assign `operationId` using the existing pattern (`auto_<method>_<sanitized_path>`).
3. Re-run tests; if hash mismatch is intentional, regenerate and update `openapi_spec_hash.txt`.

Planned Enhancements:
- Include mutation endpoints (create/update/activate/deactivate) with appropriate `@require_permissions` mapping.
- Add action/transition endpoints for state machines (approve / pay / reject for accounting, start / complete for print jobs) and embed `x-transition-rules` if needed.
- CI gate comparing previous hash on PRs to force reviewer acknowledgement.

Regenerating Hash Manually:
```bash
pytest tests/test_openapi.py::test_openapi_spec_hash_stable -q || \
	python - <<'PY'
import json,hashlib;from app import create_app;app=create_app();
from app.openapi import build_openapi_spec
spec=build_openapi_spec();blob=json.dumps(spec,sort_keys=True,separators=(',',':')).encode();
open('backend/tests/openapi_spec_hash.txt','w').write(hashlib.sha256(blob).hexdigest()+"\n")
print('Updated hash')
PY
```

Best Practices:
- Never hand-edit large static dicts (risk of drift & syntax errors). Always extend the builder.
- Keep i18n-capable fields (`description_i18n`) in seeds/models rather than plain strings.
- Introduce new permissions following `SERVICE.ACTION` taxonomy (see `.github/copilot-instructions.md`).

---
## Testing Patterns (Summary)
High-value tests cover:
- Multi-field sorting stability & ordering with tie-breakers
- Conditional caching 200 vs 304 branches (list and single-resource)
- Permission enforcement (403) vs allowed paths
- OpenAPI spec hash stability
- FSM transition metadata presence via `x-transitions`

When adding endpoints:
1. Provide both positive (permission present) and negative (403) tests.
2. Add HEAD validator tests mirroring GET list/single behavior.
3. Update pagination/sorting tests if new sortable fields introduced.

---
## Conditional Caching Extension Guide
To add single-resource caching to another entity (example: `Order`):
1. Fetch row & latest timestamp (`updated_at`).
2. Build ETag using a stable representation (existing helper `compute_etag`).
3. Call `handle_conditional(etag, latest_ts)`; if it returns a response, return immediately (304 or short-circuit HEAD).
4. On GET success, set `ETag`, and if timestamp present set `Last-Modified` + `X-Last-Modified-ISO` (UTC `Z`).
5. For HEAD, zero the body (`resp.set_data(b'')`).

Ensure tests assert header presence and 304 behavior when re-supplying validators.

---
## Roadmap Snippet
- Add audit trail enrichment for financial mutations (already scaffolded with `@audit_log`).
- Introduce branch scoping flags to spec documentation (reflect `assert_branch_access`).
- Provide a generated `permissions.json` artifact (CI already exports via seed script) and compare checksum in future.

