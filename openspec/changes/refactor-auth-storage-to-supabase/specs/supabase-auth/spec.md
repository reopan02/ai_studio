## ADDED Requirements

### Requirement: Frontend uses Supabase Auth for login
The system SHALL authenticate users via Supabase Auth from the frontend, and SHALL NOT require backend-issued session cookies for normal operation.

#### Scenario: User signs in from the login page
- **WHEN** a user enters valid Supabase credentials on `/login`
- **THEN** the frontend obtains a Supabase session and stores it client-side
- **AND** subsequent backend API calls include `Authorization: Bearer <access_token>`

### Requirement: Backend validates Supabase JWT bearer tokens
The backend SHALL validate Supabase JWT bearer tokens for protected `/api/*` endpoints and SHALL reject requests with missing or invalid tokens.

#### Scenario: Protected API call with invalid token
- **WHEN** a client calls a protected endpoint with an invalid `Authorization: Bearer ...` token
- **THEN** the backend returns `401`

### Requirement: HTML pages are not gated by backend cookie redirects
The backend SHALL serve HTML pages without requiring cookie authentication, and the frontend SHALL redirect unauthenticated users to `/login`.

#### Scenario: User opens a page without a session
- **WHEN** a user opens `/storage` without a Supabase session
- **THEN** the page loads
- **AND** the frontend redirects the user to `/login?next=/storage`

