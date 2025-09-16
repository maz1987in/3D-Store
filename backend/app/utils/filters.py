from __future__ import annotations
from typing import Callable, Any, Dict
from flask import abort

def apply_filters(query, specs: Dict[str, Dict[str, Any]], params: Dict[str, Any]):
    """Generic filter builder.

    specs: { param_name: { 'op': callable(query, model_attr, value)->query, 'coerce': type/func, 'validate': callable(optional) } }
    """
    for name, meta in specs.items():
        if name not in params or params[name] is None:
            continue
        val = params[name]
        if 'coerce' in meta:
            try:
                val = meta['coerce'](val)
            except Exception:
                abort(400, description=f'{name} invalid')
        if 'validate' in meta and not meta['validate'](val):
            abort(400, description=f'{name} invalid')
        query = meta['op'](query, val)
    return query