from __future__ import annotations
"""Audit logging decorator to reduce repetitive add_audit() calls in route handlers.

Usage examples:

@audit_log('ROLE.CREATE', entity='Role', entity_id_key='id', meta_keys=['name'])
def create_role():
    ... return {'id': role.id, 'name': role.name}, 201

@audit_log('ROLE.PERM.REPLACE', entity='Role', entity_id_key='id',
           meta_builder=lambda data, rv, args, kwargs: {'count': len(data.get('permissions', []))})
def replace_role_permissions(role_id): ...

Parameters:
  action: required audit action code (e.g. ROLE.CREATE)
  entity: optional entity label (Role, User, Group)
  entity_id_key: key in the returned JSON object whose value becomes entity_id.
  entity_id_arg: name of the function argument / path parameter to use for entity_id (fallback if entity_id_key absent).
  meta_keys: list of keys to project from returned JSON into meta dict (shallow copy).
  meta_builder: callable returning a meta dict; receives (data, original_return_value, args, kwargs). If provided it overrides meta_keys.

Return handling:
  Flask view functions commonly return one of:
    dict
    (dict, status)
    (dict, status, headers)
  The decorator extracts the first element as the JSON payload for key/meta extraction while preserving the original return value.
"""

from functools import wraps
from typing import Any, Callable, Iterable, Optional, Dict

from app.services.audit import add_audit
from app import get_db


def _extract_payload(rv: Any):
    """Return (data, original_rv) where data is the JSON-able dict for inspection."""
    if isinstance(rv, tuple) and rv:
        data = rv[0]
        return data, rv
    return rv, rv


def audit_log(
    action: str,
    *,
    entity: Optional[str] = None,
    entity_id_key: Optional[str] = None,
    entity_id_arg: Optional[str] = None,
    meta_keys: Optional[Iterable[str]] = None,
    meta_builder: Optional[Callable[[dict, Any, tuple, dict], dict]] = None,
    commit: bool = True,
    # Diff support
    diff_keys: Optional[Iterable[str]] = None,
    pre_fetch: Optional[Callable[[tuple, dict], Dict[str, Any]]] = None,
):
    def outer(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            before_snapshot = None
            if diff_keys and pre_fetch:
                try:
                    before_snapshot = pre_fetch(args, kwargs)
                except Exception:
                    before_snapshot = None
            rv = fn(*args, **kwargs)
            try:
                data, original_rv = _extract_payload(rv)
                if not isinstance(data, dict):  # nothing to inspect
                    add_audit(action, entity, None, None)
                    return rv
                entity_id = None
                if entity_id_key and entity_id_key in data:
                    entity_id = data.get(entity_id_key)
                elif entity_id_arg and entity_id_arg in kwargs:
                    entity_id = kwargs.get(entity_id_arg)
                # Build meta
                meta = None
                if meta_builder:
                    try:
                        meta = meta_builder(data, rv, args, kwargs)
                    except Exception:  # defensive – audit should not break endpoint
                        meta = None
                elif meta_keys:
                    meta = {k: data.get(k) for k in meta_keys if k in data}
                # Append diff if requested
                if diff_keys and before_snapshot and isinstance(before_snapshot, dict):
                    changes = {}
                    for k in diff_keys:
                        if k in before_snapshot and k in data:
                            if before_snapshot.get(k) != data.get(k):
                                changes[k] = {
                                    'before': before_snapshot.get(k),
                                    'after': data.get(k)
                                }
                    if changes:
                        if meta is None:
                            meta = {}
                        meta['changes'] = changes
                add_audit(action, entity, entity_id, meta)
                if commit:
                    try:
                        get_db().commit()
                    except Exception:
                        # Do not raise – audit must not interfere with main response
                        pass
                return rv
            except Exception:
                # Fail closed: do not block main response if audit decorator internal logic fails
                return rv
        return wrapper
    return outer
