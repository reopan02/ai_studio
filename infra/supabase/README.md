# Supabase (Self-Hosted) Setup

This project uses **Supabase** (Auth + PostgREST + Postgres) as the primary identity provider and database.

## 1) Start Supabase

We use the upstream `supabase/supabase` docker compose stack for local development.

```bash
git clone https://github.com/supabase/supabase .supabase
cd .supabase/docker
cp .env.example .env
docker compose up -d
```

After startup:
- Supabase Studio: `http://localhost:3000`
- Supabase API (Kong): `http://localhost:8000`

## 2) Create tables + RLS policies

Open Supabase Studio → **SQL Editor** and run:

- `infra/supabase/schema.sql`

## 3) Configure this app

Backend: set `SUPABASE_JWT_SECRET` to match Supabase `JWT_SECRET`.

Frontend (Vite): set:
- `VITE_SUPABASE_URL` (example: `http://<LAN-IP>:8000`, must be reachable from the browser)
- `VITE_SUPABASE_ANON_KEY` (the Supabase `ANON_KEY`)
