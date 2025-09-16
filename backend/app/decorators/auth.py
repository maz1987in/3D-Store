from functools import wraps
from flask import abort
from flask_jwt_extended import verify_jwt_in_request
from app.services.policy import has_permissions


def require_permissions(*codes: str):
    def outer(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            if not has_permissions(*codes):
                abort(403, description='Missing permission')
            return fn(*args, **kwargs)
        return wrapper
    return outer
