from __future__ import annotations
from typing import Any, Dict, Optional
from flask_jwt_extended import get_jwt_identity, get_jwt
from app import get_db
from app.models.audit import AuditLog


def add_audit(action: str, entity: Optional[str] = None, entity_id: Optional[str] = None, meta: Optional[Dict[str, Any]] = None):
    """Persist an audit log entry within the current DB session.

    Parameters:
      action: short action code e.g. ROLE.CREATE, ROLE.PERM.REPLACE, USER.ROLES.SET
      entity: optional entity name (Role, User, etc.)
      entity_id: optional primary key string
      meta: additional JSON-safe dictionary (will be shallow copied)
    """
    session = get_db()
    claims = {}
    try:
        claims = get_jwt() or {}
    except Exception:
        pass  # no JWT context (e.g., during tests without auth) – keep empty
    actor = None
    try:
        ident = get_jwt_identity()
        actor = int(ident) if ident is not None else None
    except Exception:
        actor = None
    log = AuditLog(
        actor_user_id=actor or 0,
        action=action,
        entity=entity,
        entity_id=str(entity_id) if entity_id is not None else None,
        perms_snapshot={'perms': claims.get('perms', [])},
        meta=meta or {},
    )
    session.add(log)
    # No commit here; caller's transaction boundary controls durability.
    return log
