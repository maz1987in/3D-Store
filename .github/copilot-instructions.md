## 3D Store – AI Implementation Playbook

Concise, task-focused rules so an agent can extend the (Flask + Angular) multi-tenant store safely and consistently.

### 1. Core Domain Axes
Services (namespaces) drive permission codes: SALES, PRINT, ACCOUNTING (ACC), INVENTORY (INV), CATALOG (CAT), PURCHASES (PO), REPAIRS (RPR), REPORTS (RPT), ADMIN. Permission code pattern: SERVICE.ACTION (e.g. PRINT.START, ACC.PAY, INV.ADJUST).

### 2. Authorization Model (Must Respect Every Change)
Entity chain: User → (UserRole ∪ (UserGroup → GroupRole)) → RolePermission → Permission.code.
Effective perms = union at login; embedded in JWT: sub, roles[], perms[], groups[], branch_ids[] (optional), locale.
Direct UserRole is an override (adhoc exception) – never mutate system roles just to satisfy one user.

### 3. Roles (Seed Baseline)
Seller (SALES.CREATE, SALES.READ, RPT.READ); Printer (PRINT.READ, PRINT.START, PRINT.COMPLETE, RPR.MANAGE); Accounting (ACC.READ, ACC.UPDATE, ACC.APPROVE, ACC.PAY, ACC.EXPORT); Manager (broad + APPROVE); Owner (ADMIN.* + all).

### 4. Scoping & Policy
Branch scope: enforce when AUTHZ_ENFORCE_BRANCH_SCOPE=true → always filter queries by branch_ids[].
User visibility feature flags: SELLER_SEES_ONLY_THEIR_SALES, PRINTER_SEES_ASSIGNED_ONLY.
Row guards live in services/policy.py: assert_branch_access(), assert_owns_record(). Do NOT inline ad‑hoc checks in route handlers.

### 5. Backend Patterns
Decorator: @require_permissions(*codes) near the outer edge (Flask view) → inside handler call policy helpers then service logic.
I18n fields: description_i18n / label_i18n JSON { "en": ..., "ar": ... }; never hardcode English in responses.
Audit all security‑sensitive mutations (payments, stock adjust, role/group changes) including actor_user_id + snapshot(perms[]).

### 6. Frontend (Angular) AuthZ Usage
Guard chain example: { path: 'accounting', canActivate: [AuthGuard, PermissionGuard], data: { perms: ['ACC.READ'] } }.
Menus/actions show/hide strictly from perms[] (client never infers). Branch selector sets active branch header (X-Branch-Id) for scoped endpoints.

### 7. Adding a New Feature (Checklist)
1) Define permission(s) (follow SERVICE.ACTION) → add to seeds. 2) Map to appropriate role(s). 3) Expose via @require_permissions. 4) Insert policy row/branch checks. 5) Add audit log if financial / security impacting. 6) Provide i18n labels (en/ar). 7) Add positive + negative test (perm present / absent).

### 8. Testing Focus (High Value)
Permission resolution unions; denial paths (403) for missing code; branch scoping filters; prevention of last Owner role removal; state transition perms (e.g. PRINT.START vs PRINT.COMPLETE).

### 9. Pitfalls to Avoid
Do NOT trust client-claimed branch id—always intersect with JWT claim. Avoid permission string typos (prefer central enum/constant module). Never silently broaden a role—create a new permission instead. Keep Owner count > 0 before deleting/removing roles.

### 10. Minimal File Map (Expected As Project Evolves)
models/ (User, Role, Permission, Group, join tables); services/policy.py; decorators/auth.py; seeds/ (permissions_roles.py); migrations/ (Alembic); frontend: src/app/auth/permission-guard.ts, shared/permission.directive.* for button-level gating.

### 11. When Unsure
Ask: (a) Which SERVICE? (b) What ACTION taxonomy fits? (c) What scoping (branch/user) applies? If all three are clear, proceed; otherwise pause for clarification.

Keep this file tight—extend only when a new invariant becomes actively enforced in code.