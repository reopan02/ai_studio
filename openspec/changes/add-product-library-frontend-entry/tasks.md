## 1. Frontend Entry Point Wiring

- [x] 1.1 Create `frontend/products.html` (MPA entry) and mount `frontend/src/pages/products/main.ts`
- [x] 1.2 Update `frontend/vite.config.ts` to include `products` in `rollupOptions.input`
- [x] 1.3 Fix `frontend/src/pages/products/main.ts` to mount `products-page.vue` (remove incorrect Video imports)

## 2. Products Page UI (Minimal MVP)

- [x] 2.1 Implement `frontend/src/pages/products/products-page.vue` with:
  - product image upload (multipart)
  - list products (offset/limit + `name` search)
  - edit product attributes (manual correction via PUT)
  - delete product
  - pagination controls based on `total`
- [x] 2.2 Use cookie-based `fetch(..., { credentials: 'include' })` and include CSRF header for unsafe methods via `frontend/src/shared/csrf.ts`
- [x] 2.3 Render images using `original_image_url` directly (expected `/uploads/products/...`)

## 3. Backend Route Integration

- [x] 3.1 Update `GET /products` to serve the built `app/static/products.html`
- [x] 3.2 Decide whether to keep `app/static/product-library.html` as a fallback route during rollout (document decision)

## 4. Validation

- [x] 4.1 Run `npm run build` in `frontend/` and verify `app/static/products.html` is produced
- [x] 4.2 Verify `GET /products` loads and calls the backend APIs successfully
- [x] 4.3 Smoke test upload → edit → list → delete flow with cookie auth (including CSRF for POST/PUT/DELETE)
