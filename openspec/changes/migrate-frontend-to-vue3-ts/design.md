# Design: Vue 3 + TypeScript Multi-Page Frontend

## Goals
- Migrate all existing frontend pages to **Vue 3 + TypeScript** with minimal functional regressions.
- Keep current route structure (Plan B): each backend route serves a distinct HTML page.
- Reuse as much existing styling and UI behavior as practical to maintain parity.

## Non-goals
- SPA conversion with `vue-router` as the primary navigation mechanism
- Backend API/schema changes
- Major UX redesign or new feature work beyond what is required for the migration

## Current State (Baseline)

### Pages and Static Assets
- `app/static/` contains:
  - `app.html` (portal), `login.html`, `video.html`, `storage.html`, `admin.html`
  - `script.js` (video), `storage.js`, `admin.js`, `style.css`
- `images_editing/` contains the image editor:
  - `index.html`, `app.js`, `styles.css`

### Serving Model
- FastAPI serves each page via `FileResponse` in `app/main.py`:
  - `/`, `/login`, `/video`, `/storage`, `/admin`, `/image`
- Static files are mounted with cache-control via `CacheControlStaticFiles`:
  - `/static` → `app/static`
  - `/images_editing` → `images_editing`

### Runtime Integration Patterns (Must Preserve)
- Cookie-based auth + redirects via `WebAuthRedirectMiddleware`
- CSRF token header (`X-CSRF-Token`) on mutating API calls
- UI calls both:
  - internal APIs (`/api/v1/*`) for persistence/history/admin
  - upstream model APIs via user-configured `baseUrl` + `apiKey` (stored in localStorage)

## Proposed Architecture

### Vite Multi-Page (MPA)
- Add a `frontend/` project built with:
  - `vue@3`, `typescript`, `vite`, `@vitejs/plugin-vue`
- Use Vite’s multi-page build so each route has its own HTML entry and bundle.

### Page Mapping
Each backend route continues to serve a dedicated HTML entry:
- `/` → portal entry
- `/login` → login entry
- `/video` → video studio entry
- `/storage` → storage repository entry
- `/admin` → admin dashboard entry
- `/image` → image editor entry

### Shared Frontend Modules
Create shared TypeScript modules to avoid duplicating critical behavior:
- Auth/me utilities (`GET /api/v1/auth/me`) and admin gating
- CSRF utilities (read cookie, build headers)
- Fetch helpers (JSON/text error parsing, redirect-on-401 behavior)
- LocalStorage key normalization and config persistence
- UI primitives (buttons/layout wrappers/toast/modals) as incremental refactors

## Build & Serving Strategy (Plan B)

### Preferred Minimal Path
- Build artifacts are produced by Vite and served as static files by FastAPI.
- Back-end continues to serve HTML via route handlers (not by exposing `*.html` directly).

### Artifact Placement (Decision Point)
Two viable strategies; both satisfy Plan B:
1) **Single static mount**: output all pages and assets to `app/static/` and serve everything from `/static`.
   - Simplifies bundling and asset base paths.
   - Allows eventual removal of `images_editing/` mount.
2) **Two static mounts (preserve current split)**: keep image editor artifacts under `images_editing/` and other pages under `app/static/`.
   - Preserves current directory split and asset gating behavior.
   - Requires two build targets (or more complex build configuration).

This change proposal assumes **(1)** for simplicity unless (2) is explicitly required.

## Migration Strategy

1) **Tooling first**
   - Introduce `frontend/` with Vite MPA and TypeScript.
   - Produce stub pages that render “Hello” per route, served by the backend.

2) **Page-by-page parity**
   - Migrate smaller pages first: portal → login → storage.
   - Migrate complex pages next: admin → video → image editor.
   - Keep existing API contracts and localStorage keys to reduce user-visible changes.

3) **Cleanup**
   - Remove or archive legacy vanilla JS/CSS only after parity checks pass.
   - Ensure cache-control and asset hashing remain correct (Vite hashed assets).

## Risks & Mitigations
- **Parity regressions**: mitigate with page-by-page migration and explicit validation scenarios.
- **Asset base path issues**: standardize built assets to load from `/static/assets/*`.
- **Auth/CSRF edge cases**: centralize helpers and preserve redirect semantics.
- **Large page complexity** (video + image editor): migrate incrementally and keep UI flows intact before refactoring.

