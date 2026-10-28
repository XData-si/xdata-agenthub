---
name: python-web-review
description: Review Python web applications built with Django or FastAPI for security, data access and deployment correctness — settings, authentication and permissions, ORM queries, async pitfalls, input validation and production server configuration. Use when reviewing or hardening a Django or FastAPI service.
license: MIT
---

# Python Web Review (Django and FastAPI)

## Goal
A Django or FastAPI service with safe production settings, enforced permissions, efficient queries and correct async behaviour.

## Inputs
- Framework and Python versions, settings per environment, authentication method, ORM (Django ORM, SQLAlchemy), ASGI/WSGI server, deployment target.

## Review checklist
1. **Production settings (Django)**: `DEBUG = False`; `SECRET_KEY` from the environment; `ALLOWED_HOSTS` explicit; `SECURE_*` settings and `CSRF_TRUSTED_ORIGINS` set; run `python manage.py check --deploy`.
2. **Authentication and permissions**: Django REST Framework's built-in default is `AllowAny` — set `DEFAULT_PERMISSION_CLASSES` (for example `IsAuthenticated`) so endpoints deny by default and verify every view that overrides it; FastAPI dependencies (`Depends`) enforce authentication on routers; object-level checks against the current user.
3. **Validation**: Pydantic models with constrained types (FastAPI), serializers or forms (Django); extra fields forbidden where mass assignment matters.
4. **ORM and queries**: avoid N+1 (`select_related`, `prefetch_related`, SQLAlchemy `selectinload`); paginate; no raw SQL with string formatting (`.raw()`/`text()` with parameters only); migrations reviewed (see `database-migrations`).
5. **Async correctness (FastAPI)**: no blocking I/O (`requests`, sync DB drivers, `time.sleep`) inside `async def` routes — use async clients or plain `def` routes, which run in a thread pool; session or connection lifetimes scoped per request.
6. **Files and templates**: uploaded files validated for size and type, stored outside the web root; templates autoescape (do not use `|safe` or `Markup` on user content).
7. **Serving**: Gunicorn with Uvicorn workers or Uvicorn behind a reverse proxy; worker count sized to CPU and memory; timeouts set; static files served by the proxy or a CDN; health endpoint without sensitive data.
8. **Dependencies**: `pip-audit` or similar in CI; pinned lockfile (`uv.lock`, `poetry.lock`, hashed requirements).

## Example fixture
```python
@app.get("/invoices/{invoice_id}")
async def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    time.sleep(0.2)  # rate smoothing
    return db.execute(text(f"SELECT * FROM invoices WHERE id = {invoice_id}")).first()
```
Expected findings: blocking sleep in async route, SQL built with an f-string, no authentication or ownership check, raw row returned without a response model.

## Acceptance checks
- `manage.py check --deploy` (Django) clean, or each warning justified.
- Tests prove a user cannot access another user's object; validation errors return 422/400.
- Negative case: a slow downstream dependency does not block unrelated requests (async test or load test).

## Output
Findings, settings changes, patches and tests.

## Safety
Use synthetic data in tests. Never enable `DEBUG` in production to investigate an error; use logs and error tracking instead. Services that process personal data must also follow GDPR: collect only needed fields, define retention, and support access and erasure requests (see `gdpr-dsar-handling`).
