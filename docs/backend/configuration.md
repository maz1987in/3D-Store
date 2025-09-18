# Configuration & Feature Flags

Environment variables (current):

| Key | Purpose | Default |
|-----|---------|---------|
| JWT_SECRET_KEY | JWT signing secret | dev-secret |
| DATABASE_URL | SQLAlchemy database URL | sqlite:///dev.db |

Planned / Future Flags:

| Flag | Description | Effect |
|------|-------------|--------|
| AUTHZ_ENFORCE_BRANCH_SCOPE | Enforce branch filtering for branch-aware endpoints | Query filters apply based on JWT.branch_ids |
| SELLER_SEES_ONLY_THEIR_SALES | Restrict Sales views to the owning seller | Query + ownership guard |
| PRINTER_SEES_ASSIGNED_ONLY | Restrict Print jobs listing to assigned printer | Query + assignment guard |

## Managing Flags
Short-term: environment variables consumed at app startup.
Long-term: persisted settings model + admin UI + caching (invalidation via version stamp).

## Branch Enforcement Strategy
If `AUTHZ_ENFORCE_BRANCH_SCOPE=true`:
- All endpoints operating on branch-bound models MUST use `filter_query_by_branches()` or `assert_branch_access`.
- Non-compliant queries risk data leakage (CI lint rule may be added later).

## Secrets Management
- Local dev: `.env` file loaded by python-dotenv.
- Production: inject via orchestrator (Kubernetes secrets / environment).

## Observability Config (Future)
- LOG_LEVEL (INFO/DEBUG)
- REQUEST_LOG_JSON (boolean)
- TRACE_ENABLED (boolean)
