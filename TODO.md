# Project TODO / Enhancement Backlog

Structured backlog of planned or proposed enhancements. Items are grouped by domain / concern. Use this file to drive incremental PRs. Keep each bullet
concise; when started, move to an Issue or strike through when completed.

## Legend
- [ ] Planned / not started
- [~] In progress (partial)
- [x] Done (recently completed — may be removed after a release note cycle)

## Cross‑Cutting / Platform
- [ ] Central /meta/transitions endpoint aggregating FSM graphs for all lifecycle entities (print jobs, purchase orders, repairs, accounting, orders, catalog when added).
- [ ] Add FSM + x-transitions vendor extension for `CatalogItem` (ACTIVE ↔ ARCHIVED) for consistency.
- [ ] Soft delete strategy (generic deleted_at column + filter) vs pure status archival for entities needing historical recovery.
- [x] Multi-field sort syntax (e.g. `sort=price_cents,-updated_at`) with deterministic tie-breakers (implemented for catalog items, orders, vendors).
- [ ] Unified query parameter documentation component for sort & filtering (reduce duplication across OpenAPI paths).
- [ ] Add per-entity HEAD endpoints (e.g. /sales/orders/{id} HEAD) for conditional retrieval of single resources.

## Catalog
- [ ] Split permissions: CAT.CREATE, CAT.UPDATE, CAT.ARCHIVE (currently single broad permission set) and migrate role seeds accordingly.
- [ ] Support multi-sort & stable secondary sorts (already partially implemented for name/updated_at fallback).
- [ ] Provide example queries / README snippet for combined price + sort usage.
- [ ] Optional: add price range validation error codes (distinct) vs generic 400 message.
- [ ] Single-resource conditional caching (GET/HEAD /catalog/items/{item_id}).
- [ ] Archiving endpoints: /catalog/items/{id}/archive (CAT.ARCHIVE), /restore (CAT.RESTORE) plus x-transitions ACTIVE↔ARCHIVED.

## Inventory
- [ ] Stock valuation metrics (quantity * optional cost_cents once cost field exists).
- [ ] Batch adjust endpoint for multiple product deltas in one transaction with audit entries per product.
- [ ] Low-stock threshold alerts (per product configurable field) + reporting integration.

## Sales / Orders
- [ ] Add SALES.REOPEN (COMPLETED → FULFILLED or COMPLETED → APPROVED depending business rule) with audit & FSM extension, guarded by SALES.REOPEN permission.
- [ ] Date range filters (created_from, created_to) for list endpoints.
- [ ] Total_cents min/max range filters.
- [ ] Order line items model (future) and recompute total from lines (deprecate direct total mutation).
- [ ] HEAD endpoint for single order (conditional validators) once generic pattern added.
- [ ] Single-resource conditional caching (GET/HEAD /sales/orders/{order_id}).
- [ ] Explicit transition endpoints (/sales/orders/{id}/approve, /cancel) guarded by SALES.APPROVE, SALES.CANCEL (taxonomy to confirm).

## Print Jobs
- [ ] Optional CANCELLED status + transition rules (QUEUED|STARTED → CANCELLED) with permissions PRINT.CANCEL.
- [ ] Add assignment audit diff (assigned_user_id changes tracked explicitly in diff metadata) if assignment mutation endpoint introduced.
- [ ] Single-resource conditional caching (GET/HEAD /print/jobs/{job_id}).
- [ ] Action endpoints: /print/jobs/{id}/start (PRINT.START), /print/jobs/{id}/complete (PRINT.COMPLETE).
- [ ] Extend OpenAPI builder with x-transition-rules (source→target map) for PrintJob lifecycle.

## Purchase Orders
- [ ] Add APPROVED status (DRAFT → APPROVED → RECEIVED → CLOSED) if business requires approval gating.
- [ ] Vendor reference table + FK for normalization (currently vendor_name string field).
- [ ] Single-resource conditional caching (GET/HEAD /po/purchase-orders/{po_id}).
- [ ] Action endpoints: /po/purchase-orders/{id}/approve (PO.APPROVE), /receive (PO.RECEIVE), /close (PO.CLOSE) with FSM + audit.

## Repairs
- [ ] Introduce parts usage tracking with inventory linkage for cost accumulation.
- [ ] Add SLA breach indicator (target completion datetime vs now) in listing with optional filter `sla_breached=true`.
- [ ] Single-resource conditional caching (GET/HEAD /repairs/tickets/{ticket_id}).
- [ ] Transition endpoints: /repairs/tickets/{id}/start, /complete, /cancel with RPR.START, RPR.COMPLETE, RPR.CANCEL permissions.

## Accounting Transactions
- [ ] Summation metrics by status (NEW / APPROVED / PAID / REJECTED) exposed via /reports/metrics (totals_cents) — extension of current counts.
- [ ] Export endpoint (CSV) with conditional caching and streaming for large datasets.
- [ ] Add reversal / adjustment transaction type or linked corrections.
- [ ] Single-resource conditional caching (GET/HEAD /accounting/transactions/{tx_id}).
- [ ] Action endpoints: /accounting/transactions/{id}/approve (ACC.APPROVE), /pay (ACC.PAY), /reject (ACC.REJECT) with audit logging.
- [ ] Extend OpenAPI builder with richer x-transitions including guard metadata (requires specific permission) for AccountingTransaction.

## Reporting / Metrics
- [x] Add date window filters (start_date, end_date) affecting underlying grouped counts.
- [x] Provide aggregated pivot structure endpoint: `{ domain: { status: count, ... }, ... }` for single round-trip UI consumption.
- [x] Include financial aggregates (sum_total_cents, sum_amount_cents) per domain where applicable. (Orders, PurchaseOrder, AccountingTransaction supported via include_financial=true)
- [x] Include Vendor domain in metrics aggregation.
- [ ] Optional caching layer (in-memory or materialized table) with last refresh timestamp and invalidation triggers on writes.
- [ ] Role-based scoping: consider separating RPT.READ from domain-specific aggregated metrics permissions (e.g. RPT.FINANCE vs RPT.OPERATIONS) if needed.

## OpenAPI / Developer Experience
- [ ] OperationId naming audit for new lifecycle endpoints (ensure consistency with naming style across future additions).
- [ ] Add OpenAPI diff CI gate (fail PR if breaking changes or undocumented permission additions) — integrate spectral or a simple json diff allowlist.
- [ ] Publish spec artifact (e.g. GitHub Pages or artifact upload) for frontend consumption.
- [ ] Automate operationId consistency check & forbid ad-hoc naming.
- [ ] Generator support for action/transition endpoints (iterate definitions + auto permission tagging) to keep builder DRY.

## Security / RBAC
- [ ] Coverage tests ensuring each newly added permission appears in seeds (seed drift test for new services).
- [ ] Safeguard to ensure at least one Owner remains before role deletion or permission removal (already partly enforced at user-role modification level) — extend to role deletion path.
- [ ] Permission constant central enumeration module to reduce string literal typos further (currently pattern followed manually).

## Testing
- [ ] Add performance smoke tests for large pagination (simulate >5k rows) focusing on listing ETag & Last-Modified correctness.
- [ ] Introduce parameterized lifecycle transition test matrix generator for each FSM to verify unreachable transitions 400.
- [ ] Add negative tests for metrics (If-Modified-Since precedence over ETag, branch scoping edge cases with zero scoped branches).

## Observability / Ops
- [ ] Structured logging with correlation/request IDs and actor embedding on mutating endpoints.
- [ ] Basic health & readiness endpoints (DB connectivity, migrations applied check hash) for deployment orchestration.
- [ ] Increment counters / histograms (Prometheus) around transition actions for dashboards.

## Data Model Enhancements
- [ ] Introduce created_at uniformly (some models rely only on server_default updated_at) for reliable temporal metrics.
- [ ] Add optimistic concurrency version column (integer) to critical financial / inventory tables.

## CI / Tooling
- [ ] Enforce minimum coverage threshold (e.g. 85%) once test surface stabilizes.
- [ ] SBOM generation (cyclonedx) & dependency review gating.
- [ ] Pre-commit hooks config (ruff, mypy, seed validation) for faster feedback.

## Documentation
- [ ] Update backend/README.md to reflect implemented services (current list out of date with accounting, catalog, lifecycle FSMs, metrics).
- [ ] Provide architectural diagram (RBAC resolution & branch scoping flow).
- [ ] Add example curl scripts for conditional GET/HEAD usage patterns.

---
Generated initial backlog from recent enhancement discussions. Trim or promote to Issues as work begins.
