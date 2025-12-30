# Implementation Tasks

## 1. Tooling & Project Setup
- [x] 1.1 Add `frontend/` with Vite + Vue 3 + TypeScript
- [x] 1.2 Configure Vite multi-page build entries for: portal, login, video, storage, admin, image
- [x] 1.3 Add `npm` scripts: `dev`, `build`, `typecheck` (and optional `lint`)
- [x] 1.4 Decide artifact policy: commit built assets to `app/static/` (npm)

## 2. Backend Static Serving Integration
- [x] 2.1 Decide output locations for built HTML/assets (see `design.md`)
- [x] 2.2 Update `app/main.py` to serve built HTML entries for `/`, `/login`, `/video`, `/storage`, `/admin`, `/image`
- [x] 2.3 Ensure static mounts (`/static` and optional `/images_editing`) serve the correct build output directories
- [x] 2.4 Verify cache-control behavior remains correct via `CacheControlStaticFiles`

## 3. Shared Frontend Infrastructure
- [x] 3.1 Implement shared TS utilities: localStorage config, CSRF header helper, fetch error parsing
- [x] 3.2 Implement shared auth helpers (admin gating via `GET /api/v1/auth/me`)
- [x] 3.3 Add shared UI primitives (minimal): reuse existing CSS primitives; keep legacy toast/modal behaviors
- [x] 3.4 Reuse existing CSS variables/styles where possible to minimize visual drift

## 4. Page Migration (Parity First)
- [x] 4.1 Portal (`/`): cards + error banner + admin-only card behavior
- [x] 4.2 Login (`/login`): safe `next` redirect + error handling + cookie login flow
- [x] 4.3 Storage (`/storage`): load videos/images + download + delete + auth redirect
- [x] 4.4 Admin (`/admin`): stats + user list/search/filter + view/edit/delete + 401/403 handling
- [x] 4.5 Video (`/video`): preserve unified layout + task polling + history CRUD + upstream baseUrl/apiKey flow
- [x] 4.6 Image (`/image`): preserve editor workflow (uploads/mask/prompt/generate) + repository integration + history CRUD

## 5. Cleanup & Hardening
- [x] 5.1 Remove/retire legacy vanilla JS/HTML once Vue equivalents are complete
- [x] 5.2 Ensure all pages handle 401 redirects consistently (to `/login?next=...`)
- [x] 5.3 Ensure CSRF headers are applied to mutating backend requests
- [x] 5.4 Validate bundling output does not leak incorrect absolute paths

## 6. Validation
- [x] 6.1 `npm run typecheck`
- [x] 6.2 `npm run build` and confirm artifacts load via FastAPI
- [x] 6.3 Smoke verification (HTTP-level) with cookie auth + CSRF:
  - [x] pages render and load assets (`/login`, `/`, `/video`, `/storage`, `/image`)
  - [x] non-admin `/admin` redirect behavior (303 to portal error)
  - [x] repository CRUD: create/list/delete via `/api/v1/videos` and `/api/v1/images`
