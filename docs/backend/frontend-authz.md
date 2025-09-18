# Frontend AuthZ Integration (Planned Angular)

## JWT Acquisition
- User logs in via `/iam/auth/login` (POST) → receives `access_token`.
- Store token (memory + refresh strategy later). Include in `Authorization: Bearer` header.

## Permission Guard (Angular Sketch)
```ts
@Injectable({providedIn: 'root'})
export class PermissionGuard implements CanActivate {
  constructor(private auth: AuthService, private router: Router) {}
  canActivate(route: ActivatedRouteSnapshot): boolean {
    const required: string[] = route.data['perms'] || [];
    const perms = this.auth.currentUser?.perms || [];
    const ok = required.every(r => perms.includes(r));
    if (!ok) { this.router.navigate(['/unauthorized']); }
    return ok;
  }
}
```
Route example:
```ts
{ path: 'accounting', component: AccountingPage, canActivate: [AuthGuard, PermissionGuard], data: { perms: ['ACC.READ'] } }
```

## Menu Rendering
Drive visibility solely from `perms[]` claim (never infer). Example directive:
```html
<button *appHasPerm="'ACC.EXPORT'">Export</button>
```

## Branch Selector
If `branch_ids.length > 1`, show a dropdown. Selected branch → add `X-Branch-Id` header on relevant API calls. Backend still intersects with JWT.claims for safety.

## i18n
Permissions / Roles returned with `description_i18n` enabling label mapping. Use Angular i18n or ngx-translate to display localized labels.

## Error Handling
Central interceptor maps backend error envelope → user notifications.
```ts
if (err.error?.error?.detail) showToast(err.error.error.detail);
```

## Token Refresh (Future)
- Introduce `/iam/auth/refresh` endpoint (JWT refresh token pattern) or short-lived tokens + silent re-login.

## Security Considerations
- Never trust client-provided branch id; server already enforces.
- Avoid storing token in localStorage if XSS risk high; consider HttpOnly cookie strategy (CSRF mitigations required).

## Asset Caching
Invalidate cached permission-dependent UI fragments upon login or role change events (trigger re-fetch of /auth/me post mutation flows in IAM UI).
