#!/usr/bin/env python
"""Idempotent seed script for permissions & roles.

Usage:
    python backend/scripts/seed_authz.py               # seed normally
    python backend/scripts/seed_authz.py --show-roles  # print role -> permission counts (after ensuring seed)
    python backend/scripts/seed_authz.py --dry-run     # run logic then rollback (no DB changes)
    python backend/scripts/seed_authz.py --dry-run --show-roles
"""
from __future__ import annotations
import os, sys, argparse, textwrap, json, hashlib
from sqlalchemy import select
from werkzeug.security import generate_password_hash

# Allow running from repo root
sys.path.append(os.path.abspath('backend'))

from app import create_app, get_db  # type: ignore
from sqlalchemy import text
from app.models.authz import Permission, Role, RolePermission, User
from app.constants.permissions import SERVICE_ACTIONS, ROLE_PRESETS, build_all_permission_codes


def ensure_permissions(session):
    existing = {p.code for p in session.execute(select(Permission)).scalars().all()}
    created = 0
    for svc, actions in SERVICE_ACTIONS.items():
        for act in actions:
            code = f"{svc}.{act}"
            if code not in existing:
                session.add(Permission(code=code, service=svc, action=act, description_i18n={"en": code.replace('.', ' - ')}))
                created += 1
    return created


def ensure_roles(session):
    existing_roles = {r.name: r for r in session.execute(select(Role)).scalars().all()}
    created = 0
    for role_name, codes in ROLE_PRESETS.items():
        if role_name not in existing_roles:
            role = Role(name=role_name, is_system=True, description_i18n={"en": role_name})
            session.add(role)
            existing_roles[role_name] = role
            created += 1
    session.flush()

    # Expand wildcard for Owner
    all_codes = set(build_all_permission_codes())
    # Pre-calculate dynamic Manager expansion if empty list configured
    if 'Manager' in existing_roles and not ROLE_PRESETS.get('Manager'):
        # Manager gets all non-admin permissions (exclude ADMIN.*) + all APPROVE actions (already included if non-admin)
        manager_codes = {c for c in all_codes if not c.startswith('ADMIN.')}
        # Assign for processing below
        dynamic_manager_codes = manager_codes
    else:
        dynamic_manager_codes = set()
    for role_name, role in existing_roles.items():
        raw_codes = ROLE_PRESETS[role_name]
        if role_name == 'Manager' and dynamic_manager_codes:
            raw_codes = list(dynamic_manager_codes)
        if '*' in raw_codes:
            desired_codes = all_codes
        else:
            desired_codes = {c for c in raw_codes if '.' in c}
        current_codes = {rp.permission.code for rp in role.permissions}
        to_add = desired_codes - current_codes
        if to_add:
            perms_map = {p.code: p for p in session.execute(select(Permission).where(Permission.code.in_(list(to_add)))).scalars()}
            for code in to_add:
                if code not in perms_map:
                    print(f"[WARN] Missing permission referenced by role {role_name}: {code}")
                    continue
                session.add(RolePermission(role=role, permission=perms_map[code]))
    return created


def ensure_initial_admin(session):
    owner_role = session.execute(select(Role).where(Role.name=='Owner')).scalar_one_or_none()
    if not owner_role:
        print('[WARN] Owner role missing; skipping admin user creation')
        return
    admin_email = os.getenv('SEED_ADMIN_EMAIL', 'admin@example.com')
    existing_admin = session.execute(select(User).where(User.email==admin_email)).scalar_one_or_none()
    if not existing_admin:
        user = User(name='Owner', email=admin_email, password_hash=generate_password_hash(os.getenv('SEED_ADMIN_PASSWORD','ChangeMe123!')))
        session.add(user)
        session.flush()
        from sqlalchemy import text as _text
        session.execute(_text("INSERT INTO user_roles (user_id, role_id) VALUES (:u, :r)"), {"u": user.id, "r": owner_role.id})
        print(f"[INFO] Created initial admin user {admin_email} with temporary password.")


def summarize_roles(session):
    rows = []
    for role in session.execute(select(Role)).scalars().all():
        perms = [rp.permission.code for rp in role.permissions]
        rows.append((role.name, len(perms), sorted(perms)[:8]))
    return rows


def print_role_summary(session):
    rows = summarize_roles(session)
    if not rows:
        print("[INFO] No roles present.")
        return
    name_w = max(len(r[0]) for r in rows)
    print(f"{'Role'.ljust(name_w)} | Count | Sample (up to 8)")
    print('-' * (name_w + 40))
    for name, cnt, sample in rows:
        print(f"{name.ljust(name_w)} | {str(cnt).rjust(5)} | {', '.join(sample)}")


def parse_args():
    p = argparse.ArgumentParser(
        description="Seed RBAC permissions & roles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""Examples:\n  seed normally: seed_authz.py\n  dry run: seed_authz.py --dry-run\n  show roles: seed_authz.py --show-roles\n""")
    )
    p.add_argument('--show-roles', action='store_true', help='Print role permission counts after seeding')
    p.add_argument('--dry-run', action='store_true', help='Rollback after operations (no commit)')
    p.add_argument('--export-json', nargs='?', const='-', metavar='FILE', help='Export role->permissions JSON (to FILE or stdout if omitted)')
    p.add_argument('--validate', action='store_true', help='Validate existing permission codes & role references; exits non-zero on problems')
    p.add_argument('--fail-if-changed', metavar='CHECKSUM', help='Exit 4 if computed roles checksum differs from provided value')
    return p.parse_args()


def build_role_permission_map(session):
    mapping = {}
    for role in session.execute(select(Role)).scalars().all():
        perms = sorted({rp.permission.code for rp in role.permissions})
        mapping[role.name] = perms
    return mapping


def main():
    args = parse_args()
    app = create_app()
    with app.app_context():
        session = get_db()
        try:
            # Ensure tables exist (lightweight fallback if migrations not run yet)
            session.execute(text('SELECT 1 FROM permissions LIMIT 1'))
        except Exception:
            # Auto-create schema for bootstrap; in real env prefer alembic upgrade
            from app.models.authz import Base  # local import to avoid circular
            engine = session.get_bind()
            Base.metadata.create_all(engine)
        finally:
            session.commit()

    with app.app_context():
        session = get_db()
        try:
            created_p = ensure_permissions(session)
            created_r = ensure_roles(session)
            ensure_initial_admin(session)
            role_perm_map = build_role_permission_map(session)
            if args.validate:
                # Perform validation before commit/rollback decision so dry-run still validates.
                problems = []
                # Validate permission code structure
                valid_services = set(SERVICE_ACTIONS.keys())
                for code in session.execute(select(Permission.code)).scalars().all():
                    if '.' not in code:
                        problems.append(f"Invalid format (missing '.'): {code}")
                        continue
                    svc, action = code.split('.', 1)
                    if svc not in valid_services:
                        problems.append(f"Unknown service '{svc}' in code: {code}")
                        continue
                    allowed_actions = set(SERVICE_ACTIONS[svc])
                    if action not in allowed_actions:
                        # Suggest closest
                        import difflib
                        suggestion = difflib.get_close_matches(action, allowed_actions, n=1)
                        hint = f" (did you mean {suggestion[0]})" if suggestion else ''
                        problems.append(f"Unknown action '{action}' for service '{svc}' in code: {code}{hint}")
                # Validate role_permission references correspond to existing codes (already enforced but double-check)
                all_codes = {c for c in session.execute(select(Permission.code)).scalars().all()}
                for role_name, codes in role_perm_map.items():
                    for c in codes:
                        if c not in all_codes:
                            problems.append(f"Role '{role_name}' references missing permission code: {c}")
                if problems:
                    print('\n[VALIDATION] FAIL:')
                    for p in problems:
                        print(' -', p)
                    # Exit non-zero (rollback if not committed yet)
                    if not args.dry_run:
                        session.rollback()
                    import sys as _sys
                    _sys.exit(2)
                else:
                    print('[VALIDATION] OK: All permission codes & role references valid.')
            if args.dry_run:
                session.rollback()
                print(f"[DRY-RUN] (rolled back) Permissions would create: {created_p}, Roles would create: {created_r}")
            else:
                session.commit()
                print(f"[DONE] Permissions created: {created_p}, Roles created: {created_r}")
            if args.show_roles:
                print('\nRole Permission Summary:')
                print_role_summary(session)
            if args.fail_if_changed and not args.export_json:
                # Need checksum even if not exporting JSON
                canonical = json.dumps(role_perm_map, sort_keys=True, separators=(',', ':'))
                checksum = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
                if checksum != args.fail_if_changed:
                    print(f"[CHECKSUM] MISMATCH: expected {args.fail_if_changed} got {checksum}")
                    if not args.dry_run:
                        session.rollback()
                    import sys as _sys
                    _sys.exit(4)
                else:
                    print(f"[CHECKSUM] OK: {checksum}")

            if args.export_json is not None:
                # Deterministic checksum for build caching / change detection
                canonical = json.dumps(role_perm_map, sort_keys=True, separators=(',', ':'))
                checksum = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
                payload = {
                    'roles': role_perm_map,
                    'meta': {
                        'permissions_total': sum(len(v) for v in role_perm_map.values()),
                        'distinct_permissions': len({p for plist in role_perm_map.values() for p in plist}),
                        'roles_checksum_sha256': checksum,
                        'role_names_sorted': sorted(role_perm_map.keys()),
                        'dry_run': args.dry_run,
                    }
                }
                if args.fail_if_changed and checksum != args.fail_if_changed:
                    print(f"[CHECKSUM] MISMATCH: expected {args.fail_if_changed} got {checksum}")
                    if not args.dry_run:
                        session.rollback()
                    import sys as _sys
                    _sys.exit(4)
                if args.export_json == '-' or args.export_json is None:
                    print(json.dumps(payload, indent=2, sort_keys=True))
                else:
                    with open(args.export_json, 'w', encoding='utf-8') as f:
                        json.dump(payload, f, indent=2, sort_keys=True)
                    print(f"[INFO] Exported JSON to {args.export_json}")
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

if __name__ == '__main__':
    main()
