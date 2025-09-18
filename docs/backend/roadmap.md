# Roadmap

## Near Term
- Domain example entity (e.g., Product with branch_id) to demonstrate branch filtering.
- OpenAPI examples + response schemas for audit logs & errors.
- CI: OpenAPI diff gating + coverage threshold (e.g., >=85%).
- Lint rule / script verifying all permission codes referenced in code exist in seed map.

## Mid Term
- Frontend Angular scaffold with permission guard + dynamic menu.
- Refresh token endpoint & rotation strategy.
- Additional audit decorators for financial and inventory modules.
- Policy-based ownership enforcement for Sales & Print modules (flag driven).

## Long Term
- Fine-grained ABAC conditions (e.g., restricting actions to user locale or branch).
- Delegated administration (branch-level sub-owners).
- Archived audit log storage & pruning job.
- SBOM generation & dependency risk dashboards.
- Multi-factor authentication integration.
- Rate limiting & anomaly detection.

## Exploratory
- ReBAC graph store for complex relationship permissions (investigate if role/group model insufficient).
- Attribute hashing / pseudonymization for GDPR compliance on personal data fields.
