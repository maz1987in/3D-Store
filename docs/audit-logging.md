# Audit Logging & Observability

## Goals
- Immutable trail of security-sensitive mutations.
- Facilitate incident response & compliance reviews.
- Support diff-based visibility for key updates (e.g., group branch scope changes).

## AuditLog Schema
| Field | Description |
|-------|-------------|
| id | PK |
| actor_user_id | Acting user (0 if unauthenticated context) |
| action | Code (e.g. ROLE.CREATE) |
| entity | Domain entity label (Role, Group, User) |
| entity_id | Identifier of affected entity |
| perms_snapshot | `{ "perms": ["ADMIN.ROLE.MANAGE", ...] }` at action time |
| meta | Arbitrary JSON (includes changes diff if captured) |
| created_at | Timestamp (DB default) |

## Emission Mechanism
Decorate mutating endpoints with `@audit_log`. The decorator:
1. Optionally pre-fetches a snapshot (`pre_fetch`) for diff keys.
2. Executes the handler.
3. Extracts meta (selected keys or custom builder).
4. Computes field diffs (`diff_keys`) if provided.
5. Persists entry and commits (isolated from main commit errors).

## Example Diff Meta
```json
{
  "name": "OpsGroup",
  "changes": {
    "branch_scope": { "before": {"allow":[1,2]}, "after": {"allow":[1,2,3]} }
  }
}
```

## Action Naming Conventions
`ENTITY.OPERATION` or hierarchical: `ROLE.PERM.REPLACE`, `USER.ROLES.SET`.
Keep verbs explicit: CREATE, UPDATE, DELETE, SET, REPLACE.

## When to Audit
Must audit:
- Role / Group / User membership mutations.
- Permission set changes (role perm replacement).
- Future: Payments, inventory adjustments, financial approvals, configuration changes.

Optional (case-by-case): Pure reads of sensitive data (if regulatory requirement emerges) → consider separate logging channel.

## Observability Roadmap
- Structured request logs (user_id, route, latency, status) → log aggregator.
- Correlation/trace id injection for multi-service contexts.
- Security anomaly heuristics (e.g., multiple 403s then elevated action) → future analytics job.

## Data Retention
(Not yet enforced.) Plan:
- Warm storage (DB) for 90 days; older entries archived.
- Consider partitioning if volume grows (timeline table sharding or log sink).
