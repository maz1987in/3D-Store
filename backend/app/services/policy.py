from __future__ import annotations
from typing import Iterable, Set
from flask_jwt_extended import get_jwt
from sqlalchemy import select
from app.models.authz import User, UserRole, RolePermission, GroupRole, UserGroup, Permission, Role, Group
from app.constants.permissions import ROLE_PRESETS
from app import get_db

# Feature flags names (must align with config / future settings persistence)
FLAG_BRANCH_SCOPE = 'AUTHZ_ENFORCE_BRANCH_SCOPE'
FLAG_SELLER_SCOPE = 'SELLER_SEES_ONLY_THEIR_SALES'
FLAG_PRINTER_SCOPE = 'PRINTER_SEES_ASSIGNED_ONLY'


def current_permissions() -> Set[str]:
    claims = get_jwt()
    return set(claims.get('perms', []))


def has_permissions(*codes: str) -> bool:
    perms = current_permissions()
    return all(c in perms for c in codes)


def compute_effective_permissions(user_id: int):
    session = get_db()
    # Direct roles
    direct_role_ids = [r.role_id for r in session.execute(select(UserRole).where(UserRole.user_id==user_id)).scalars()]
    # Group roles
    group_ids = [ug.group_id for ug in session.execute(select(UserGroup).where(UserGroup.user_id==user_id)).scalars()]
    group_role_ids = []
    if group_ids:
        group_role_ids = [gr.role_id for gr in session.execute(select(GroupRole).where(GroupRole.group_id.in_(group_ids))).scalars()]
    role_ids = set(direct_role_ids + group_role_ids)
    perm_codes = set()
    if role_ids:
        role_perms = session.execute(select(RolePermission).where(RolePermission.role_id.in_(role_ids))).scalars().all()
        perm_ids = [rp.permission_id for rp in role_perms]
        if perm_ids:
            for p in session.execute(select(Permission).where(Permission.id.in_(perm_ids))).scalars():
                perm_codes.add(p.code)
    # Owner wildcard support (if role named Owner present)
    owner_role = session.execute(select(Role).where(Role.name=='Owner')).scalar_one_or_none()
    if owner_role and owner_role.id in role_ids:
        # Expand to all permissions dynamically (wildcard semantics)
        for p in session.execute(select(Permission)).scalars():
            perm_codes.add(p.code)
    return {
        'roles': list(role_ids),
        'perms': sorted(perm_codes),
        'groups': group_ids,
    }


def compute_branch_ids(user_id: int):
    """Aggregate allowed branch ids from group.branch_scope JSON: {"allow": [ids...]}. Unique & sorted."""
    session = get_db()
    branch_ids = set()
    group_ids = [ug.group_id for ug in session.execute(select(UserGroup).where(UserGroup.user_id==user_id)).scalars()]
    if group_ids:
        for grp in session.execute(select(Group).where(Group.id.in_(group_ids))).scalars():
            scope = grp.branch_scope or {}
            allow = scope.get('allow') if isinstance(scope, dict) else None
            if isinstance(allow, list):
                for b in allow:
                    if isinstance(b, int):
                        branch_ids.add(b)
    return sorted(branch_ids)


def enforce_branch_scope_enabled(app_config) -> bool:
    return bool(app_config.get('AUTHZ_ENFORCE_BRANCH_SCOPE', False))


def filter_query_by_branches(query, model_branch_column, branch_ids):
    """Return query filtered by branch ids if list not empty."""
    if branch_ids:
        return query.where(model_branch_column.in_(branch_ids))
    return query


def count_owner_users(session=None) -> int:
    """Return number of distinct users who possess the Owner role via direct or group assignment."""
    close_after = False
    if session is None:
        session = get_db()
        close_after = True
    owner_role = session.execute(select(Role).where(Role.name=='Owner')).scalar_one_or_none()
    if not owner_role:
        return 0
    # Direct user_roles
    direct_user_ids = [ur.user_id for ur in session.execute(select(UserRole).where(UserRole.role_id==owner_role.id)).scalars()]
    # Group-based
    group_ids_with_owner = [gr.group_id for gr in session.execute(select(GroupRole).where(GroupRole.role_id==owner_role.id)).scalars()]
    group_user_ids = []
    if group_ids_with_owner:
        group_user_ids = [ug.user_id for ug in session.execute(select(UserGroup).where(UserGroup.group_id.in_(group_ids_with_owner))).scalars()]
    total_users = set(direct_user_ids + group_user_ids)
    if close_after:
        session.close()
    return len(total_users)


def assert_not_removing_last_owner(target_user_id: int, new_direct_role_ids: set[int]):
    """Ensure that after applying new_direct_role_ids for target_user_id we still have at least one Owner overall."""
    session = get_db()
    owner_role = session.execute(select(Role).where(Role.name=='Owner')).scalar_one_or_none()
    if not owner_role:
        return
    owner_id = owner_role.id
    # If target user will still have owner role, safe.
    if owner_id in new_direct_role_ids:
        return
    # Count existing owners excluding this user if currently owner.
    current_owner_count = count_owner_users(session)
    # Determine if target user currently had owner role
    had_owner = session.execute(select(UserRole).where(UserRole.user_id==target_user_id, UserRole.role_id==owner_id)).scalar_one_or_none() is not None
    if had_owner and current_owner_count <= 1:
        from flask import abort
        abort(400, description='Cannot remove last Owner role')


def assert_branch_access(branch_id: int):
    claims = get_jwt()
    if not claims.get('branch_ids'):
        return  # No scoping
    if branch_id not in claims['branch_ids']:
        from flask import abort
        abort(403, description='Branch access denied')


def assert_owns_record(owner_user_id: int):
    claims = get_jwt()
    if claims.get('sub') != owner_user_id:
        from flask import abort
        abort(403, description='Record ownership required')
