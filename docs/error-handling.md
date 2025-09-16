# Error Handling Contract

All errors (framework + custom aborts + unhandled exceptions) are transformed into a consistent JSON envelope:

```json
{
  "error": {
    "status": 400,
    "title": "Bad Request",
    "detail": "Reason message"
  }
}
```

## HTTPException Mapping
- Flask/Werkzeug exceptions preserve status & title.
- `abort(404)` → `{ "error": { "status":404, "title":"Not Found", "detail":"404 Not Found: ..." } }` (detail may be default or custom description).
- `abort(403, description='Missing permission')` → status 403 with provided detail.

## Unhandled Exceptions
Return status 500 with:
```json
{ "error": { "status": 500, "title": "Internal Server Error", "detail": "Unexpected error" } }
```
(No stack trace leaked.)

## Client Guidance
- Rely on `error.status` for conditional UI logic.
- Display `error.detail` for user-friendly messages (i18n translation mapping possible on frontend if detail keys standardized later).

## Future Enhancements
- Error correlation id (e.g., `trace_id`) injection for support diagnostics.
- Granular error codes separate from HTTP status (e.g., `code: LAST_OWNER_REMOVAL_DENIED`).
- Localization of error titles/details.
