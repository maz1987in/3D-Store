# Testing Strategy

## Goals
- Guarantee authorization correctness (positive & negative permission paths).
- Prevent regression in owner safeguard & branch scoping.
- Maintain deterministic audit coverage.

## Current Test Coverage (Summary)
- Login & JWT claim issuance.
- Role CRUD + permission replacement (success + error paths).
- Group CRUD + role/group assignments.
- User role/group assignment endpoints.
- Branch scope aggregation into JWT (`branch_ids`).
- Audit log listing + filtering.
- Permission denials (403) for unauthorized access.
- Standardized error response shape (404, forced 500).

## Patterns
- Each test ensures clean SQLAlchemy session via `session.rollback()` safety at start.
- Direct inserts used sparingly to set minimal preconditions quickly.
- Assertions tolerant to reruns (e.g., `status_code in (201,400)` for idempotent create attempts).

## Adding New Tests
1. Create entities / seed permissions required for scenario.
2. Authenticate and capture token.
3. Exercise endpoint(s) with and without required permissions.
4. Assert on:
   - Status codes (200 vs 403 / 400 / 404 as relevant)
   - Response JSON structure
   - Audit entries (when mutation)
5. If branch-related, add group with branch_scope and assert query result filtering once domain entities exist.

## Negative Testing Focus
- Missing permission → 403.
- Unknown resource IDs → 404.
- Validation errors (e.g. empty name) → 400 with explanatory detail.
- Last owner removal attempt → 400.

## Roadmap Tests
- OpenAPI contract drift (generate + diff snapshot).
- Coverage threshold enforcement (fail CI if < target %).
- Field-level audit diff assertions for additional entities.
- Performance smoke: N roles/groups retrieval under large dataset (benchmark mode).
