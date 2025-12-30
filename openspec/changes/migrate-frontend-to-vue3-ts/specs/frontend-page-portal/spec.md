## ADDED Requirements

### Requirement: Portal Page as Vue Entry
The system SHALL implement the portal page (`/`) using Vue 3 + TypeScript.

#### Scenario: Display navigation cards
- **WHEN** an authenticated user visits `/`
- **THEN** the page displays navigation entries to `/video`, `/storage`, and `/image`

#### Scenario: Display admin-only entry
- **WHEN** the current user is an admin
- **THEN** an admin entry to `/admin` is visible
- **AND** non-admin users do not see the admin entry

### Requirement: Error Banner Handling
The portal page SHALL surface server-provided error messages via query params.

#### Scenario: Render `error` query param
- **WHEN** the user visits `/?error=<message>`
- **THEN** the page displays `<message>` in an error banner

