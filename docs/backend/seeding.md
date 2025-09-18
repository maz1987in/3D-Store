# Seeding & Drift Governance

## Purpose
Ensure a single authoritative definition for permissions and role composition to avoid configuration drift across environments.

## Seed Source
`backend/seeds/permissions_roles.py` defines:
- `PERMISSIONS` dict: service → list of actions
- `ROLES` dict: role → list of permission codes (supports `*` wildcard)

## Seed Script (Implemented)
Features (current / planned):
- Idempotent insertion of new permissions & roles.
- Manager role dynamic composition.
- Checksum / hash export for CI drift detection.
- JSON export artifact (attached in CI for change review).
- Validation (`--validate`) mode to assert DB matches definition.
- Fail-if-changed option to break CI when drift occurs.

## Workflow
1. Modify seed source.
2. Run seed script locally (or let CI run on push).
3. Commit both code & any expected spec changes.
4. CI compares computed checksum to repository baseline; mismatch → failure.

## Adding a Role
1. Update `ROLES` (empty list if computed programmatically).
2. If requires dynamic expansion (e.g., Manager), implement logic in script to fill at runtime.
3. Ensure tests reflect new effective permissions where relevant.

## Removal / Renames
- Renaming a permission: treat as removal + addition (migration may be needed to cascade changes to existing role assignments).
- Removing a permission: ensure no roles reference it (script should detect dangling references and fail).

## Future Enhancements
- Seed diff report (human-readable) in CI comment.
- Automatic OpenAPI examples update referencing permission codes.
- SBOM / provenance attestation.
