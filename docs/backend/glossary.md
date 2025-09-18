# Glossary

| Term | Definition |
|------|------------|
| Permission | Atomic capability labeled `SERVICE.ACTION` (e.g., `ACC.PAY`). |
| Role | Named collection of permissions. System roles are seeded (Owner, Manager, etc.). |
| Group | Aggregator assigning roles to sets of users; may carry branch scope. |
| Branch Scope | JSON policy object on Group limiting accessible branches (e.g., `{"allow":[1,2]}`). |
| Effective Permissions | Union of direct role permissions and group role permissions (plus wildcard expansion). |
| Wildcard | Owner role designates `['*']` meaning all permissions. Resolved explicitly at claim time. |
| Audit Log | Immutable record of sensitive action containing actor, action code, entity, meta, timestamp. |
| Diff Audit | Audit entry enriched with before/after field differences. |
| JWT Claims | Embedded authorization context: roles[], perms[], groups[], branch_ids[], locale. |
| Feature Flag | Configuration toggle altering policy enforcement behavior. |
| Seed Drift | Divergence between database permissions/roles and code-defined seed specification. |
| Policy Layer | Central helper functions for permission checks and scoping (branch / ownership). |
| Last Owner Safeguard | Protection preventing removal of the final Owner role from the system. |
