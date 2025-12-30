## ADDED Requirements

### Requirement: Login Page as Vue Entry
The system SHALL implement the login page (`/login`) using Vue 3 + TypeScript.

#### Scenario: Successful login and redirect
- **WHEN** a user submits valid credentials on `/login`
- **THEN** the client calls `POST /api/v1/auth/login?set_cookie=1` with `credentials: include`
- **AND** the user is redirected to the safe `next` path (or `/` if missing/invalid)

#### Scenario: Invalid credentials show error
- **WHEN** a user submits invalid credentials
- **THEN** the page shows a user-visible error message
- **AND** the user remains on `/login`

### Requirement: Safe `next` Redirect
The login page SHALL prevent open redirects via the `next` query parameter.

#### Scenario: Reject external redirect
- **WHEN** `next` is not a safe same-origin path (e.g. contains `://` or does not start with `/`)
- **THEN** the client redirects to `/` after login

