DEFAULT_LIMIT = 50
MAX_LIMIT = 200

def normalize_pagination(limit_raw, offset_raw):
    try:
        limit = int(limit_raw) if limit_raw is not None else DEFAULT_LIMIT
        offset = int(offset_raw) if offset_raw is not None else 0
    except ValueError:
        raise ValueError('limit/offset must be int')
    limit = max(1, min(limit, MAX_LIMIT))
    offset = max(0, offset)
    return limit, offset
