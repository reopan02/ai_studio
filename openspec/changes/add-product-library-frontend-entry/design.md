# Design: Product Library Frontend Entry Point (Vite MPA)

## Context

The repository uses a Vite multi-page frontend (`frontend/`) that builds into `app/static/` and is served via FastAPI routes (e.g. `/video`, `/storage`, `/image`). A Products page exists in the frontend tree (`frontend/src/pages/products/`) but is not wired into the build and is incomplete.

Separately, backend Product Library APIs exist at `/api/v1/products` (CRUD + image upload) and product images are exposed under `/uploads/products/...`.

## Goals / Non-Goals

**Goals**
- Make the Products/Product Library UI a first-class Vite build entry (consistent with other pages).
- Fix current “products page” wiring errors (wrong imports / empty entry files).
- Use existing shared helpers for cookie-based auth + CSRF (consistent with other frontend pages).

**Non-Goals**
- Redesign Product Library backend APIs (handled by `add-product-library`).
- Introduce a new SPA router; keep MPA pattern.
- Add advanced UI features (bulk upload, complex filters) unless already required by existing specs.

## Decisions

### Decision 1: Entry Point Pattern

**Choice**: Add `products` to the Vite MPA inputs:
- `frontend/products.html` → `frontend/src/pages/products/main.ts`
- Build output: `app/static/products.html` and hashed assets under `app/static/assets/`

**Rationale**:
- Matches existing pages (`video.html`, `storage.html`, etc.).
- Keeps deployment simple (static files served by FastAPI).

### Decision 2: Auth + CSRF Strategy

**Choice**: Use cookie-based auth (same-origin fetch) with CSRF header injection for unsafe methods.

**Implementation sketch**:
- `fetch(..., { credentials: 'include' })`
- Merge `csrfHeaders()` from `frontend/src/shared/csrf.ts` for `POST/PUT/DELETE` when using cookies.

**Rationale**:
- Matches current middleware behavior: cookie auth requires `X-CSRF-Token` for non-safe `/api/*` requests.

### Decision 3: Image URL Rendering

**Choice**: Render product images using the `original_image_url` returned by the backend (expected to be an absolute path like `/uploads/products/...`).

**Rationale**:
- Avoids incorrect `/static` prefixing.
- Lets the backend control image URL shape.

### Decision 4: `/products` Route Rollout

**Choice**: Switch `GET /products` to serve the Vite-built `app/static/products.html` immediately and do not keep `app/static/product-library.html` as a fallback route.

**Rationale**:
- The frontend build owns `app/static/` output; the legacy standalone page would be deleted by `vite build` and is not a reliable rollback mechanism.
- Rollback should be handled by reverting the deployment version, not by keeping two parallel page implementations.

## Rollout Plan

1. Land the Vite products entry point and UI.
2. Update `GET /products` to serve the built `products.html`.
3. Stop serving the legacy standalone `app/static/product-library.html` page.
