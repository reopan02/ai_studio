## 1. Supabase stack + schema
- [x] 1.1 Decide how Supabase is started in dev (clone `supabase/supabase` + docker compose, or vendored compose).
- [x] 1.2 Add env contract: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` (frontend); `SUPABASE_JWT_SECRET` (backend token verification).
- [x] 1.3 Add initial SQL schema for app tables + RLS policies (no data migration).

## 2. Frontend: Supabase Auth
- [x] 2.1 Add `@supabase/supabase-js` and a shared client module.
- [x] 2.2 Replace `/login` page to use Supabase Auth (email/password).
- [x] 2.3 Add a shared “require session” guard used by all pages (redirect to `/login?next=...`).
- [x] 2.4 Remove/hide in-app admin navigation and page entry.

## 3. Backend: validate Supabase JWT
- [x] 3.1 Implement JWT verification using `SUPABASE_JWT_SECRET` and derive `user_id` from `sub`.
- [x] 3.2 Replace `get_current_user` dependency to use Supabase auth context (no DB lookup).
- [x] 3.3 Remove cookie-session-only gates (`WebAuthRedirectMiddleware`) and keep CSRF only if any cookie auth remains.

## 4. Frontend: move persistence to Supabase
- [x] 4.1 Update “save to repository” flows (video page + runninghub page) to insert rows into Supabase tables.
- [x] 4.2 Update storage page to list videos/images from Supabase tables (and remove calls to `/api/v1/videos` + `/api/v1/images`).
- [x] 4.3 Update product page to persist products/images to Supabase (recognition can remain server-side).

## 5. Remove legacy DB endpoints
- [x] 5.1 Deprecate/remove `/api/v1/auth/*`, `/api/v1/videos/*`, `/api/v1/images/*`, `/api/v1/products/*` CRUD that existed purely for persistence.
- [x] 5.2 Remove/disable `/api/v1/admin/*`, `/api/v1/logs`, `/api/v1/categories`, `/api/v1/storage/me` or re-implement them via Supabase as needed.

## 6. Validation + docs
- [ ] 6.1 Manual happy path: sign in, generate/save, list records, sign out.
- [x] 6.2 Add minimal automated tests for JWT verification helpers and RLS-safe request patterns where feasible.
- [x] 6.3 Update `README.md` with Supabase setup instructions and new auth model.
