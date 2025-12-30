## ADDED Requirements

### Requirement: Admin Page as Vue Entry
The system SHALL implement the admin dashboard page (`/admin`) using Vue 3 + TypeScript.

#### Scenario: Render admin dashboard
- **WHEN** an admin user visits `/admin`
- **THEN** the page loads and renders system statistics and user management UI

### Requirement: Admin API Integration
The admin dashboard SHALL integrate with existing admin endpoints under `/api/v1/admin/*`.

#### Scenario: Load system stats
- **WHEN** the admin dashboard loads
- **THEN** the client calls `GET /api/v1/admin/stats`
- **AND** the stats are displayed

#### Scenario: List users with filters
- **WHEN** an admin searches or filters users
- **THEN** the client calls `GET /api/v1/admin/users` with query params for pagination/search/filters
- **AND** results are displayed in a table/grid

### Requirement: Unauthorized and Forbidden Handling
The admin dashboard SHALL handle auth failures consistently.

#### Scenario: Redirect on 401
- **WHEN** an admin API call returns 401
- **THEN** the client redirects to `/login?next=/admin`

#### Scenario: Handle 403
- **WHEN** an admin API call returns 403
- **THEN** the user is redirected to `/?error=Admin%20access%20required` or shown an equivalent access error state

