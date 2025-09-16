from __future__ import annotations
from typing import Callable, Dict, Any, Tuple, Iterable, Optional
from flask import request, abort, make_response
from sqlalchemy.orm import Query
from app.config.pagination import normalize_pagination
import hashlib
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime, format_datetime

TIMESTAMP_TOLERANCE = timedelta(seconds=1)

def canonicalize_timestamp(dt: datetime) -> datetime:
    """Return UTC tz-aware timestamp truncated to whole seconds (microseconds removed)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.replace(microsecond=0)

def apply_pagination(q: Query) -> Tuple[Query, int, int, int]:
    try:
        limit, offset = normalize_pagination(request.args.get('limit'), request.args.get('offset'))
    except ValueError as e:
        abort(400, description=str(e))
    total = q.count()
    return q.offset(offset).limit(limit), total, limit, offset

def compute_etag(ids: Iterable[int], total: int, limit: int, offset: int, latest_ts: Optional[str] = '') -> str:
    seed = f"{list(ids)}|{total}|{limit}|{offset}|{latest_ts or ''}"
    return hashlib.sha256(seed.encode()).hexdigest()[:32]

def build_list_payload(rows: list, total: int, limit: int, offset: int):
    return {
        'data': rows,
        'pagination': {
            'total': total,
            'limit': limit,
            'offset': offset,
            'returned': len(rows)
        }
    }

def _http_date(dt: datetime) -> str:
    """Return RFC1123 HTTP-date string in GMT."""
    try:
        return format_datetime(dt, usegmt=True)  # Python 3.11+ ensures RFC1123
    except Exception:
        return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

def make_cached_list_response(rows: list, total: int, limit: int, offset: int, latest_ts: Optional[datetime] = None):
    ids = [r.get('id') for r in rows]
    latest_ts_c = canonicalize_timestamp(latest_ts) if isinstance(latest_ts, datetime) else None
    latest_iso = latest_ts_c.isoformat().replace('+00:00','Z') if latest_ts_c else (latest_ts or '')
    # Keep ETag seed stable using ISO canonical form
    etag = compute_etag(ids, total, limit, offset, latest_iso)
    resp = make_response(build_list_payload(rows, total, limit, offset))
    resp.headers['ETag'] = etag
    if latest_ts_c:
        resp.headers['Last-Modified'] = _http_date(latest_ts_c)
        # Provide original canonical ISO in secondary header for clients that prefer it
        resp.headers['X-Last-Modified-ISO'] = latest_iso
    return resp, etag

def _parse_if_modified_since(header_val: str) -> Optional[datetime]:
    if not header_val:
        return None
    # Try ISO 8601 first
    try:
        dt = datetime.fromisoformat(header_val.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        pass
    # Try HTTP-date (RFC 1123)
    try:
        dt = parsedate_to_datetime(header_val)
        if dt and dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None

def handle_conditional(etag_value: str, latest_ts: Optional[datetime]):
    """Evaluate conditional request headers.

    Precedence: If-None-Match over If-Modified-Since (per RFC 9110 semantics).
    Returns a 304 response object if conditions satisfied, else None.
    """
    inm = request.headers.get('If-None-Match')
    if inm and inm.strip('"') == etag_value:
        resp = make_response('', 304)
        resp.headers['ETag'] = etag_value
        if latest_ts:
            latest_c = canonicalize_timestamp(latest_ts)
            resp.headers['Last-Modified'] = _http_date(latest_c)
            resp.headers['X-Last-Modified-ISO'] = latest_c.isoformat().replace('+00:00','Z')
        return resp
    # Only evaluate If-Modified-Since if If-None-Match was not a match / absent
    ims_raw = request.headers.get('If-Modified-Since')
    if ims_raw and latest_ts:
        ims_dt = _parse_if_modified_since(ims_raw)
        if ims_dt:
            latest_c = canonicalize_timestamp(latest_ts)
            ims_c = canonicalize_timestamp(ims_dt)
            if latest_c <= ims_c + TIMESTAMP_TOLERANCE:
                resp = make_response('', 304)
                resp.headers['ETag'] = etag_value
                resp.headers['Last-Modified'] = _http_date(latest_c)
                resp.headers['X-Last-Modified-ISO'] = latest_c.isoformat().replace('+00:00','Z')
                return resp
    return None