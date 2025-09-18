# Changelog (IAM & Auth)

All notable IAM, audit, and authorization model changes.

## [Unreleased]
- OpenAPI examples (planned)
- Domain model with branch-enforced queries (planned)
- Coverage threshold gating in CI (planned)
- Spec diff CI job (planned)

## 2025-09-14
### Added
- `@audit_log` decorator with meta key extraction.
- Diff support (`diff_keys`, `pre_fetch`) for audit entries (used in GROUP.UPDATE).
- Comprehensive docs set (architecture, authz model, permissions matrix, API reference, audit logging, error handling, configuration, testing, frontend integration, glossary, roadmap).

### Changed
- Refactored IAM routes to use `@audit_log` instead of inline `add_audit` calls.

### Fixed
- Ensured audit commits inside decorator to surface entries for immediate tests.

## 2025-09-13
### Added
- Standardized error handler & Error schema integration into OpenAPI spec.
- Audit log listing endpoint with filtering & pagination.
- Group CRUD + role & user group assignment endpoints.

### Changed
- Seed script enhancements: checksum/export, dynamic Manager role composition.

### Fixed
- Last Owner safeguard logic validated via tests.

## 2025-09-12
### Added
- Initial RBAC models (User, Role, Permission, Group, joins) and audit log model.
- Login endpoint with JWT embedding roles/perms/groups/branch_ids.
- Permission enforcement decorator `@require_permissions`.
- CI pipeline (pytest matrix, ruff, mypy, pip-audit, coverage artifact).

