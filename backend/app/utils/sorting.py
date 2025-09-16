from __future__ import annotations
from flask import abort

def apply_multi_sort(query, sort_expr: str | None, allowed: dict, tie_breaker):
    """Apply multi-field sort to a SQLAlchemy query.
    sort_expr: comma-separated tokens, each optionally prefixed with '-'.
    allowed: mapping of field key -> column object.
    tie_breaker: column to append for deterministic ordering.
    """
    if not sort_expr:
        return query.order_by(tie_breaker.asc())
    clauses = []
    for raw in sort_expr.split(','):
        token = raw.strip()
        if not token:
            continue
        desc = token.startswith('-')
        key = token[1:] if desc else token
        col = allowed.get(key)
        if not col:
            abort(400, description=f'Invalid sort field {key}')
        clauses.append(col.desc() if desc else col.asc())
    clauses.append(tie_breaker.asc())
    return query.order_by(*clauses)
