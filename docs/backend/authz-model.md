# Authorization Model

## Core Concepts
- Permission: Atomic ability named `SERVICE.ACTION` (e.g. `INV.ADJUST`).
- Role: Named collection of permissions. System roles (`is_system=True`) seed baseline (Owner, Manager, etc.).
- Group: Aggregates roles and optional `branch_scope` policy defining allowed branches.
- User: May receive direct Role(s) (exception override) and belong to multiple Groups.

Effective permissions = union(User.direct_roles ∪ (Groups → GroupRoles)). Owner role acts as wildcard (currently expands to all permission codes at token creation).

## JWT Claims Structure
```
{
  "sub": <user_id>,
  "roles": [role_id, ...],
  "perms": ["ADMIN.ROLE.MANAGE", ...],
  "groups": [group_id, ...],
  "branch_ids": [1,2,3],
  "locale": "en"
}
```
`branch_ids` aggregated from each group.branch_scope.allow.

## Permission Naming Taxonomy
Pattern: `SERVICE.ACTION`
- Services: SALES, PRINT, ACC, INV, CAT, PO, RPR, RPT, ADMIN
- ACTION may contain dot for administrative composite (e.g. `ROLE.MANAGE`).

Guidelines:
- Never create vague actions (avoid `*.ALL`).
- For new state transitions prefer precise verbs (e.g. `PRINT.START`).
- If a single role needs an extra capability, add a new permission; don't broaden an existing one silently.

## Branch Scoping
When `branch_scope` is attached to groups: `{ "allow": [10, 20] }` → each branch id added to JWT.
Enforcement approach:
- For branch-bound queries: call `filter_query_by_branches(query, Model.branch_id, jwt.branch_ids)`.
- For direct entity access: `assert_branch_access(entity.branch_id)`.
- Controlled by future config flag `AUTHZ_ENFORCE_BRANCH_SCOPE` (currently rely on presence of branch_ids array).

## Owner Safeguard
`assert_not_removing_last_owner(user_id, new_role_ids)` aborts (400) if change would eliminate final Owner.

## Feature Flags (Planned)
- AUTHZ_ENFORCE_BRANCH_SCOPE
- SELLER_SEES_ONLY_THEIR_SALES
- PRINTER_SEES_ASSIGNED_ONLY

## Policy Anti-Patterns
- Do NOT inline permission string comparisons inside business logic: use decorators or helpers.
- Avoid duplicating permission codes in tests—centralize expected sets.
- Never mutate system roles to satisfy a single user; attach a direct role instead.

## Future Enhancements
- Attribute-based constraints at row level (e.g. limit sales view to user if SELLER flag on).
- Delegated admin (scoped Owner variant per branch).
- Permission templates import/export.
