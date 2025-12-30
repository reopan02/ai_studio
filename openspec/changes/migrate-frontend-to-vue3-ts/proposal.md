# Change: Migrate Frontend to Vue 3 + TypeScript (Vite Multi-Page)

## Why

The current frontend is implemented as static HTML + vanilla JavaScript split across `app/static/` and `images_editing/`. As features expanded (video studio, image editor, storage repository, admin dashboard), the UI logic has become large, harder to refactor safely, and difficult to share across pages.

Migrating to **Vue 3 + TypeScript** provides:
- Stronger maintainability through components and shared utilities
- Type-safety for UI state, API payloads, and cross-page contracts
- Clearer separation of concerns (views, state, services)
- More scalable structure for continued UI evolution

## What Changes

- Replace all user-facing pages with **Vue 3 + TypeScript** implementations:
  - `/` portal, `/login`, `/video`, `/storage`, `/admin`, `/image`
- Introduce a **Vite multi-page (MPA)** build so each route remains a dedicated HTML entry (Plan B).
- Consolidate common UI and utilities (auth/me check, CSRF header, fetch helpers, storage keys, toasts/modals) into shared TypeScript modules.
- Preserve existing backend APIs and routes; the migration focuses on frontend implementation details and static asset build/serving.

## Impact

### Affected Code / Assets
- Frontend assets currently in:
  - `app/static/*` (portal/video/storage/admin/login)
  - `images_editing/*` (image editor)
- Backend static serving entrypoints in `app/main.py` (FileResponse routes and static mounts) may be adjusted to serve built artifacts.

### Breaking Changes
- Developer workflow becomes Node-based for building frontend assets (**BREAKING** for contributors who only used Python tooling).
- Minor visual/behavior differences are possible during migration; the goal is feature parity with current pages.

## Non-goals
- Changing backend API contracts, authentication model, or database schema
- Introducing SSR or converting to a single SPA with client-side routing
- Redesigning UX; this change prioritizes parity and maintainability

## Open Questions
- Artifact policy: build artifacts are **committed** to `app/static/` (keeps the server runnable without requiring Node at runtime).
- Package manager: **npm**.
