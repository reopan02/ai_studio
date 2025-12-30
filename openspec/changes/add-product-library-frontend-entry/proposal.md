# Change: Add Product Library Frontend Entry Point

## Why

The project’s frontend is built as a Vite multi-page app (MPA) with Vue 3 + TypeScript, outputting to `app/static/`. The Product Library UI currently does not have a corresponding Vite entry point, and the existing `frontend/src/pages/products/` scaffolding is incomplete (e.g. empty `products.html` / `products-page.vue`, and a copy/paste `main.ts` that mounts the Video page).

This prevents a consistent build pipeline for the Product Library UI and makes it easy for regressions or missing pages to slip into production builds.

## What Changes

- **Frontend entry point**: Add a proper Vite MPA entry for Products (HTML + TS entry) so the Product Library page is part of the normal frontend build.
- **Fix frontend wiring errors**: Ensure the Products page mounts the correct Vue component and uses shared helpers for auth/CSRF/error handling.
- **Backend page route**: Serve the built Products page at `GET /products` (and keep compatibility with the existing Product Library endpoints under `/api/v1/products`).

## Impact

- **Depends on**: `openspec/changes/add-product-library` (Product CRUD + recognition endpoints).
- **Affected code**:
  - Frontend: `frontend/products.html`, `frontend/vite.config.ts`, `frontend/src/pages/products/*`
  - Backend: `app/main.py` route for `GET /products` (to serve the built page)
- **User-visible**: Product Library becomes available as a first-class built page (same build system as `/video`, `/storage`, etc.).

## Open Questions

1. Should `GET /products` switch to the Vite-built `app/static/products.html` immediately, or keep the current `app/static/product-library.html` as the default for one release?
2. Should the portal page (`GET /`) add a “产品库” card linking to `/products`?
