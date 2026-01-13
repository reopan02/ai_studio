## Context
We are migrating to a self-hosted Supabase stack (Auth + PostgREST + Postgres) and moving user-owned persistence to Supabase. The frontend will be the primary client of Supabase (Auth + database), and the backend will be reduced to “server-side capabilities” (calling external model providers, product recognition, etc.) protected by Supabase JWT validation.

The current backend user/session model (custom JWT + `users`/`user_sessions`) and SQLAlchemy persistence tables will be replaced.

## Goals / Non-Goals
- Goals
  - Users authenticate via Supabase Auth from the frontend.
  - Frontend reads/writes repository data via PostgREST with RLS.
  - Backend accepts `Authorization: Bearer <supabase_access_token>` and validates it.
  - Remove the in-app admin UI and use Supabase Studio.
- Non-Goals
  - Migrate existing database data.
  - Provide an in-app admin panel equivalent to Supabase Studio.
  - Preserve encrypted-at-rest repository blobs (`STORAGE_MASTER_KEY`).

## Architecture
### Identity and request auth
- Frontend uses `@supabase/supabase-js` to sign in/sign out and hold session state.
- For backend-protected routes (`/api/v1/...` that call external providers), the frontend includes `Authorization: Bearer <access_token>`.
- Backend validates JWT signatures using the Supabase Auth JWT secret (self-hosted) and extracts `sub` as the user id.

### Data plane (Supabase Postgres + PostgREST)
- Define application tables in Supabase Postgres (e.g. `user_videos`, `user_images`, `products`, `product_images`).
- Enable RLS and create policies enforcing `user_id = auth.uid()`.
- Frontend uses supabase-js (PostgREST) for CRUD and list views.

### Web access
- Backend stops redirecting unauthenticated users away from HTML pages. Pages are always served, and the frontend redirects to `/login` if no Supabase session exists.

## Migration notes
Because we are not migrating existing data, we can:
- drop/disable the local DB requirements for running the app
- create new Supabase schema from scratch
- remove legacy `/api/v1/auth/*` and repository CRUD endpoints over time (or keep temporarily behind feature flags)

## Validation
- Manual: bring up Supabase stack, set frontend env, and confirm:
  - login/logout works
  - storage page lists only current user’s records (RLS)
  - backend provider endpoints reject missing/invalid Supabase JWTs

