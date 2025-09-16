from __future__ import annotations
"""Reusable validation helpers for domain models.

Currently focuses on status lifecycle validation to reduce scattered string comparisons
and provide consistent 400 error semantics.
"""
from typing import Iterable
from flask import abort


def validate_status(new_status: str, allowed: Iterable[str], field_name: str = 'status') -> str:
    """Validate that new_status is inside allowed.

    Returns the status (to enable inline usage) or aborts with 400.
    """
    if new_status not in allowed:
        abort(400, description=f"{field_name} invalid")
    return new_status

__all__ = ['validate_status']
