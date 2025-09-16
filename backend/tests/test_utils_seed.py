"""Test seeding utilities to reduce duplication.

These helpers centralize creation of users, roles, permissions, groups with branch scopes
while preserving the project authorization invariants.
"""
from typing import Iterable, Dict, List, Optional
from app import get_db
from app.models.authz import User, Role, Permission, RolePermission, Group, GroupRole, UserGroup, UserRole, Base
from sqlalchemy import select


def ensure_permissions(codes: Iterable[str]):
    """Ensure each permission code exists; return dict code->Permission."""
    session = get_db()
    # Safety: ensure all authz tables exist (engine may be re-created mid-suite)
    try:
        engine = session.get_bind()
        Base.metadata.create_all(bind=engine, checkfirst=True)
    except Exception:
        pass
    out: Dict[str, Permission] = {}
    for code in codes:
        obj = session.query(Permission).filter_by(code=code).one_or_none()
        if not obj:
            if '.' not in code:
                raise ValueError(f"Permission code '{code}' missing SERVICE.ACTION pattern")
            service, action = code.split('.', 1)
            obj = Permission(code=code, service=service, action=action, description_i18n={'en': code})
            session.add(obj); session.flush()
        out[code] = obj
    session.commit()
    return out


def ensure_user(email: str, name: Optional[str] = None, password: str = 'pw') -> User:
    session = get_db()
    u = session.query(User).filter_by(email=email).one_or_none()
    if not u:
        u = User(name=name or email.split('@')[0], email=email, password_hash='')
        u.set_password(password)
        session.add(u); session.commit(); session.refresh(u)
    return u


def ensure_role(name: str, perm_codes: Iterable[str] = ()) -> Role:
    session = get_db()
    role = session.query(Role).filter_by(name=name).one_or_none()
    perms = ensure_permissions(perm_codes) if perm_codes else {}
    if not role:
        role = Role(name=name, is_system=False, description_i18n={'en': name})
        session.add(role); session.flush()
    # attach any missing permissions
    existing_perm_ids = {rp.permission_id for rp in session.query(RolePermission).filter_by(role_id=role.id)}
    for p in perms.values():
        if p.id not in existing_perm_ids:
            session.add(RolePermission(role_id=role.id, permission_id=p.id))
    session.commit()
    return role


def ensure_user_role_assignment(user: User, role: Role):
    session = get_db()
    if not session.query(UserRole).filter_by(user_id=user.id, role_id=role.id).one_or_none():
        session.add(UserRole(user_id=user.id, role_id=role.id)); session.commit()


def ensure_group(name: str, role: Role, branch_ids: List[int]) -> Group:
    session = get_db()
    g = session.query(Group).filter_by(name=name).one_or_none()
    if not g:
        g = Group(name=name, description_i18n={'en': name}, branch_scope={'allow': branch_ids})
        session.add(g); session.flush()
        session.add(GroupRole(group_id=g.id, role_id=role.id)); session.commit()
    return g


def ensure_user_group_membership(user: User, group: Group):
    session = get_db()
    if not session.query(UserGroup).filter_by(user_id=user.id, group_id=group.id).one_or_none():
        session.add(UserGroup(user_id=user.id, group_id=group.id)); session.commit()


def seed_user_with_role_and_group(email: str, role_name: str, perm_codes: Iterable[str], group_name: str, branch_ids: List[int]):
    """High level convenience: user + role(with perms) + group association + branch scope."""
    user = ensure_user(email)
    role = ensure_role(role_name, perm_codes)
    ensure_user_role_assignment(user, role)
    group = ensure_group(group_name, role, branch_ids)
    ensure_user_group_membership(user, group)
    return user, role, group


# ---------------- Domain helpers (Inventory / Sales) ---------------- #
def ensure_product(sku: str, name: str = None, branch_id: int = 1, quantity: int = 0, description_i18n=None):
    """Idempotently ensure a Product exists (by SKU). Returns the Product.

    Args:
        sku: Unique stock keeping unit (lookup key)
        name: Display name (defaults to sku if omitted)
        branch_id: Branch owning the product
        quantity: Initial quantity value
        description_i18n: Optional i18n dict
    """
    from app import get_db
    from app.models.product import Product  # lazy import to avoid test import cycles
    session = get_db()
    prod = session.query(Product).filter_by(sku=sku).one_or_none()
    if not prod:
        prod = Product(name=name or sku, sku=sku, branch_id=branch_id, quantity=quantity, description_i18n=description_i18n or {'en': name or sku})
        session.add(prod); session.commit(); session.refresh(prod)
    return prod


def create_order(customer_name: str, branch_id: int = 1, total_cents: int = 0, status: str = 'NEW'):
    """Create a Sales Order (non-idempotent). Returns the Order.

    Tests often want multiple orders with same customer; we don't enforce uniqueness.
    Args:
        customer_name: Name of customer
        branch_id: Branch under which order is placed
        total_cents: Monetary total (integer smallest unit)
        status: Initial status (default NEW)
    """
    from app import get_db
    from app.models.order import Order  # lazy import
    session = get_db()
    order = Order(customer_name=customer_name, branch_id=branch_id, total_cents=total_cents, status=status)
    session.add(order); session.commit(); session.refresh(order)
    return order


__all__ = [
    'ensure_permissions', 'ensure_user', 'ensure_role', 'ensure_user_role_assignment', 'ensure_group',
    'ensure_user_group_membership', 'seed_user_with_role_and_group', 'ensure_product', 'create_order'
]
