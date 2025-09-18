# 3D Store Documentation

This directory contains structured documentation for the 3D Store backend (Flask) and planned Angular frontend authorization layer.

## Index

- [Architecture Overview](architecture.md)
- [Authorization Model](authz-model.md)
- [Permissions & Roles Matrix](permissions-roles.md)
- [Seeding & Drift Governance](seeding.md)
- [API Reference (IAM & Auth)](api-reference.md)
- [Audit Logging & Observability](audit-logging.md)
- [Error Handling Contract](error-handling.md)
- [Configuration & Feature Flags](configuration.md)
- [Testing Strategy](testing.md)
- [Frontend AuthZ Integration](frontend-authz.md)
- [Glossary](glossary.md)
- [Changelog](changelog.md)
- [Roadmap](roadmap.md)

## Quick Start

1. Create virtualenv and install backend requirements:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Export `JWT_SECRET_KEY` (optional for dev) or let default apply.
3. Run the app (example minimal runner you add):
   ```bash
   flask --app backend.app:create_app run --reload
   ```
4. View OpenAPI spec at: `GET /openapi.json` and human docs at `/docs`.

## Key Tenets
- Principle of Least Privilege via granular permission codes `SERVICE.ACTION`.
- Union-based effective permissions (direct roles + group roles).
- Branch scoping (per-group) surfaces `branch_ids[]` in JWT for filtering.
- Standardized JSON error envelope.
- Audit logging for all IAM mutations (now including diff snapshots for certain updates).

See individual pages for deep detail.
