# Caching & Conditional Requests

The API exposes lightweight cache validators on list endpoints to reduce bandwidth and improve perceived latency for dashboards / admin consoles.

## Headers
- `ETag`: Short hash of result identity + select metadata (ids, pagination window, most recent timestamp) for the page returned.
- `Last-Modified`: RFC1123 HTTP-date (e.g. `Wed, 15 Sep 2025 14:22:05 GMT`) for the most recently updated (or created) record in the page.
	- Internally canonicalized to whole-second UTC before formatting.
	- An additional `X-Last-Modified-ISO` header exposes the same instant in ISO8601 (`YYYY-MM-DDTHH:MM:SSZ`) for clients that prefer ISO parsing.

Consumers MAY send:
- `If-None-Match: <etag>` to perform a conditional GET (takes precedence if both present).
- `If-Modified-Since: <timestamp>` (ISO8601 or RFC1123) — server-side evaluated; if newest record timestamp <= provided value returns 304.
	- 1 second tolerance applied to absorb cross-DB / serialization microsecond drift.

If the hash matches current server calculation the API returns `304 Not Modified` with empty body (and the same `ETag`).

## Current Coverage
| Endpoint | ETag | Last-Modified | Notes |
|----------|------|---------------|-------|
| GET /inventory/products | Yes | Yes | Seed includes aggregate of ids + newest updated_at |
| GET /sales/orders | Yes | Yes | updated_at column drives Last-Modified |
| GET /iam/roles | Yes | Yes | updated_at added to roles |
| GET /iam/groups | Yes | Yes | updated_at added to groups |
| GET /iam/permissions | Yes | Yes | updated_at added to permissions |
| GET /iam/audit/logs | Yes | Yes | created_at of newest log used |

## ETag Construction Strategy
Common formula (conceptually):
```
ids = [id1,id2,...]
etag_seed = f"{ids}|{total}|{limit}|{offset}|<latest_ts?>"
sha256(etag_seed).hexdigest()[:32]
```
Where `<latest_ts?>` is the `updated_at` / `created_at` of the first (newest) row when available.

Rationale:
- Stable across identical pagination windows.
- Changes when new items appear, items disappear, or an item in the window mutates (timestamp changes).
- Hash truncated to 32 chars for header brevity (still collision-resistant for practical use here).
	- Timestamp seed uses canonical ISO second precision value (not RFC1123) ensuring stable ETag independent of output header formatting.

### Centralized Implementation (Backend)
All list endpoints now delegate to shared helpers in `app/utils/listing.py`:

- `compute_etag(ids, total, limit, offset, latest_ts)` – pure function building the deterministic seed + sha256 hash (32 char truncation).
- `make_cached_list_response(rows_json, total, limit, offset, latest_ts)` – constructs the response body (data + pagination), sets `ETag`, and, when available, `Last-Modified` (ISO8601) header; returns `(response, etag)`.

Route pattern (simplified):
```python
rows = query.limit(limit).offset(offset).all()
rows_json = [serialize(r) for r in rows]
latest_ts = rows[0].updated_at if rows else None  # or created_at for audit logs
resp, etag = make_cached_list_response(rows_json, total, limit, offset, latest_ts)
cond = handle_conditional(etag)
if cond:
	return cond
return resp
```

Benefits:
- Eliminates duplicated hash + header code across services.
- Guarantees consistent seed composition if future adjustments (e.g., include branch scope) are needed.
- Eases future support for alternate validators (e.g., weak ETags, version tokens).

## Client Usage Pattern
Pseudo:
```http
GET /inventory/products?limit=25 HTTP/1.1
Authorization: Bearer <token>

200 OK
ETag: abcd1234...
Last-Modified: 2025-09-15T10:05:44Z

# Subsequent poll
GET /inventory/products?limit=25 HTTP/1.1
Authorization: Bearer <token>
If-None-Match: abcd1234...

304 Not Modified
ETag: abcd1234...
```
If 200 is returned, update cache store with new body + ETag + Last-Modified.

## Pitfalls & Considerations
- Do not treat ETag as permanent: any data mutation can change it.
- Pagination window matters: caching `/inventory/products?limit=10&offset=0` ETag does NOT apply to `offset=10`.
- For rapid, high-churn data consider shorter polling cadence + background refresh.
- Avoid storing stale Authorization tokens alongside cached payloads.

## Future Enhancements
- Stronger per-item versioning (e.g., row_version) for differential sync.
	(Implemented) HEAD endpoints provide only caching validators without payload for faster polling.

