# Change: Refactor auth + storage to Supabase (self-hosted)

## Why
The current system uses a local database (SQLite/PostgreSQL via SQLAlchemy) plus a custom JWT + session table for authentication. This creates operational overhead (schema management, session persistence, admin UI) and prevents the frontend from using a unified data plane for user-owned records.

We want to adopt **self-hosted Supabase** (`supabase/supabase`) as the primary datastore and identity provider:
- Supabase Auth replaces custom `/api/v1/auth/*`
- Supabase PostgREST + RLS replace the app’s per-user repository tables (videos/images/products/etc)
- The frontend becomes the source of truth for user session state (Supabase session)

## What Changes
- **Authentication**
  - Frontend signs users in via Supabase Auth (no backend-issued cookie session).
  - Backend verifies Supabase JWTs on protected `/api/*` endpoints.
  - Remove backend “web auth redirect” gate for HTML pages; frontend handles redirect-to-login.
- **Persistence**
  - Frontend reads/writes user-owned records via Supabase PostgREST (supabase-js).
  - Records are stored **in plaintext** (no `STORAGE_MASTER_KEY` encryption); access control relies on RLS.
  - No migration: existing local DB data is not migrated.
- **Admin**
  - Remove/disable the in-app `/admin` page and `/api/v1/admin/*` endpoints; use Supabase Studio for admin operations.

## Impact
- Breaking changes for:
  - Login flow (`/login` moves from backend cookie login to Supabase Auth).
  - Any client relying on `/api/v1/auth/*`, `/api/v1/videos/*`, `/api/v1/images/*`, `/api/v1/products/*`, `/api/v1/storage/me`, `/api/v1/categories`, `/api/v1/logs`, `/api/v1/admin/*`.
- Affected code areas:
  - Backend auth middleware (`app/api/deps.py`, `app/middleware/web_auth_redirect.py`, `app/middleware/csrf.py`)
  - DB layer and models (`app/db/*`, `app/models/database.py`)
  - Frontend auth + storage pages (`frontend/src/pages/*`, `frontend/src/shared/*`)
  - Deployment/dev setup (Supabase stack + env vars)

