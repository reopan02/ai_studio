## ADDED Requirements

### Requirement: Store user-owned records in Supabase Postgres via PostgREST
The system SHALL store user-owned repository records (videos, images, products, etc.) in Supabase Postgres and SHALL access them via PostgREST (supabase-js) from the frontend.

#### Scenario: Save a generated video record
- **WHEN** a signed-in user saves a generated video
- **THEN** the frontend inserts a row into the Supabase `user_videos` table via PostgREST

### Requirement: Enforce per-user access with RLS
The system SHALL enable RLS on user-owned tables and SHALL restrict access such that a user can only access rows where `user_id = auth.uid()`.

#### Scenario: Cross-user access is denied
- **WHEN** a user attempts to read another user’s record
- **THEN** Supabase returns an authorization error or an empty result set according to policy

### Requirement: Store repository request/response in plaintext
The system SHALL store repository request/response payloads in plaintext JSON columns in Supabase tables.

#### Scenario: Saved record includes plaintext metadata
- **WHEN** a user saves a record with request/response metadata
- **THEN** the stored row contains the JSON payloads in plaintext

### Requirement: In-app admin is removed in favor of Supabase Studio
The system SHALL remove or disable the in-app admin UI and SHALL use Supabase Studio for administrative tasks.

#### Scenario: User cannot access in-app admin
- **WHEN** a user attempts to access `/admin`
- **THEN** the app does not provide an in-app admin dashboard and instead relies on Supabase Studio

