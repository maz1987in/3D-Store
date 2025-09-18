# Permissions & Roles Matrix

## Permission Inventory
| Service | Actions |
|---------|---------|
| SALES | READ, CREATE, UPDATE, DELETE, APPROVE, EXPORT |
| PRINT | READ, CREATE, UPDATE, DELETE, START, COMPLETE |
| ACC | READ, UPDATE, APPROVE, PAY, EXPORT |
| INV | READ, ADJUST, RECEIVE_PO |
| CAT | READ, MANAGE |
| PO | READ, CREATE, RECEIVE, CLOSE |
| RPR | READ, MANAGE |
| RPT | READ |
| ADMIN | USER.MANAGE, ROLE.MANAGE, GROUP.MANAGE, SETTINGS.MANAGE |

Generated permission codes: `SERVICE.ACTION` for each combination above.

## Seed Roles (Baseline)
| Role | Permissions (Summary) |
|------|-----------------------|
| Seller | SALES.CREATE, SALES.READ, RPT.READ |
| Printer | PRINT.READ, PRINT.START, PRINT.COMPLETE, RPR.MANAGE, RPT.READ (typo test: PRINT.COMPPLETE) |
| Accounting | ACC.* (READ, UPDATE, APPROVE, PAY, EXPORT), RPT.READ |
| Manager | Programmatically composed superset of core operational (SALES/PRINT/ACC/INV/RPT) without full ADMIN.* |
| Owner | * (wildcard all permissions) |

## Manager Role Construction Logic
1. Collect all permission codes for services: SALES, PRINT, ACC, INV, RPT.
2. Exclude specialized or high-risk actions if introduced (e.g., PAY in some models—currently included, may revisit).
3. Deduplicate and assign.

## Adding a New Permission
1. Choose proper service or introduce new service key (uppercase, <= 8 chars recommended).
2. Add action(s) to `PERMISSIONS` in seed file.
3. Decide which seed roles receive it; revise tests if expectations change.
4. Run seed validation (CI ensures drift detection).
5. Reference in endpoints using `@require_permissions`.

## Wildcard Semantics
Currently only the Owner role has wildcard via seed `['*']`. Resolution expands to all defined permissions at claim computation time ensuring testability (no implicit bypass).

## Typos & Governance
CI should eventually include a script that: ensures every `SERVICE.ACTION` referenced in code exists in seed map; catches typos (`PRINT.COMPPLETE`). Tests can assert absence/presence to surface mismatches.
