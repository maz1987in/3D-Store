# API Reference (IAM & Auth)

Base path prefix: `/iam`

> NOTE: This is a concise human summary. The canonical machine-readable contract lives at `/openapi.json`.

## Authentication
### POST /iam/auth/login
Request:
```json
{ "email": "user@example.com", "password": "secret" }
```
Responses:
- 200: `{ "access_token": "<JWT>" }`
- 400: missing credentials
- 401: invalid credentials

### GET /iam/auth/me
Headers: `Authorization: Bearer <JWT>`
Response:
```json
{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com",
  "roles": [2,5],
  "perms": ["ADMIN.ROLE.MANAGE", "SALES.CREATE"],
  "groups": [3],
  "locale": "en",
  "branch_ids": [10,20]
}
```

## Permissions
### GET /iam/permissions
Requires: `ADMIN.ROLE.MANAGE`
Response: `{ "data": [ { "id":1, "code":"ADMIN.ROLE.MANAGE", ... } ] }`

## Roles
### GET /iam/roles
Requires: `ADMIN.ROLE.MANAGE`
Response: List role objects with embedded permission codes.

### POST /iam/roles
Requires: `ADMIN.ROLE.MANAGE`
Body: `{ "name": "Support" }`
Responses: 201 with created role, 400 duplicates.
Audited: `ROLE.CREATE`

### PUT /iam/roles/{id}/permissions
Requires: `ADMIN.ROLE.MANAGE`
Body: `{ "permissions": ["ACC.READ", "ACC.PAY"] }`
Audited: `ROLE.PERM.REPLACE`

## User Role Assignment
### PUT /iam/users/{user_id}/roles
Requires: `ADMIN.USER.MANAGE`
Body: `{ "role_ids": [1,2] }`
Audited: `USER.ROLES.SET` + last Owner safeguard.

## Groups
### GET /iam/groups
Requires: `ADMIN.GROUP.MANAGE`

### POST /iam/groups
Requires: `ADMIN.GROUP.MANAGE`
Body: `{ "name": "Ops", "branch_scope": {"allow": [1,2]} }`
Audited: `GROUP.CREATE`

### PUT /iam/groups/{id}
Requires: `ADMIN.GROUP.MANAGE`
Body: partial update of name, description_i18n, branch_scope.
Audited: `GROUP.UPDATE` (diff of name / branch_scope captured in meta.changes)

### DELETE /iam/groups/{id}
Requires: `ADMIN.GROUP.MANAGE`
Audited: `GROUP.DELETE`

### PUT /iam/groups/{id}/roles
Requires: `ADMIN.GROUP.MANAGE`
Body: `{ "role_ids": [3,4] }`
Audited: `GROUP.ROLES.SET`

## User Group Assignment
### PUT /iam/users/{user_id}/groups
Requires: `ADMIN.USER.MANAGE`
Body: `{ "group_ids": [5,7] }`
Audited: `USER.GROUPS.SET`

## Audit Logs
### GET /iam/audit/logs
Requires: `ADMIN.SETTINGS.MANAGE`
Query Params: `actor_user_id`, `action`, `entity`, `entity_id`, `limit`, `offset`
Response includes pagination + newest-first ordering.

## Error Schema
All error responses (4xx/5xx) follow:
```json
{ "error": { "status": 400, "title": "Bad Request", "detail": "Explanation" } }
```

## Examples
### Create Role then Assign to User (pseudo)
1. POST /iam/roles {"name":"Support"}
2. PUT  /iam/users/42/roles {"role_ids":[<support_role_id>]}
3. GET  /iam/auth/me (user 42) → perms now include Support's permission set.

### Filter Audit by Action
`GET /iam/audit/logs?action=GROUP.UPDATE`

## Versioning Strategy (Planned)
- Breaking changes to response fields will increment semantic version surfaced via future `/meta` endpoint.
- OpenAPI diff gating in CI (planned) will flag changes for review.
