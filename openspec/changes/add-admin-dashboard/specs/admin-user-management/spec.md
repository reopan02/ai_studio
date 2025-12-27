## ADDED Requirements

### Requirement: List Users with Pagination and Search
The system SHALL provide an endpoint for administrators to list all users with pagination, search, and filtering capabilities.

#### Scenario: Admin lists users with default pagination
- **GIVEN** an admin user is authenticated
- **WHEN** they request `GET /api/v1/admin/users`
- **THEN** the system returns up to 50 users ordered by creation date (newest first)
- **AND** includes user summary fields: id, username, email, is_active, is_admin, storage_quota_bytes, storage_used_bytes, created_at, last_login_at

#### Scenario: Admin searches users by username or email
- **GIVEN** an admin user is authenticated
- **WHEN** they request `GET /api/v1/admin/users?search=john`
- **THEN** the system returns users where username or email contains "john" (case-insensitive)

#### Scenario: Admin filters by active status
- **GIVEN** an admin user is authenticated
- **WHEN** they request `GET /api/v1/admin/users?is_active=false`
- **THEN** the system returns only inactive users

#### Scenario: Non-admin user attempts to list users
- **GIVEN** a non-admin user is authenticated
- **WHEN** they request `GET /api/v1/admin/users`
- **THEN** the system returns HTTP 403 Forbidden

### Requirement: View Detailed User Information
The system SHALL provide an endpoint for administrators to view detailed information about a specific user, including activity statistics.

#### Scenario: Admin views user details
- **GIVEN** an admin user is authenticated
- **WHEN** they request `GET /api/v1/admin/users/{user_id}`
- **THEN** the system returns complete user information including:
  - All user profile fields
  - Total video count and total image count
  - Active session count
  - Recent login attempts (last 10)
  - Storage usage breakdown

#### Scenario: Admin views non-existent user
- **GIVEN** an admin user is authenticated
- **WHEN** they request `GET /api/v1/admin/users/{invalid_id}`
- **THEN** the system returns HTTP 404 Not Found

### Requirement: Update User Account
The system SHALL provide an endpoint for administrators to update user account fields including active status, admin role, email, and storage quota.

#### Scenario: Admin enables/disables user account
- **GIVEN** an admin user is authenticated
- **WHEN** they send `PATCH /api/v1/admin/users/{user_id}` with `{"is_active": false}`
- **THEN** the system updates the user's active status to false
- **AND** returns the updated user information

#### Scenario: Admin promotes user to admin role
- **GIVEN** an admin user is authenticated
- **WHEN** they send `PATCH /api/v1/admin/users/{user_id}` with `{"is_admin": true}`
- **THEN** the system updates the user's admin status to true

#### Scenario: Admin updates user email
- **GIVEN** an admin user is authenticated
- **WHEN** they send `PATCH /api/v1/admin/users/{user_id}` with `{"email": "newemail@example.com"}`
- **THEN** the system validates email format
- **AND** checks for email uniqueness
- **AND** updates the user's email if valid and unique
- **AND** returns HTTP 422 if email is invalid or already exists

### Requirement: Delete User Account
The system SHALL provide an endpoint for administrators to permanently delete user accounts with cascading deletion of associated data.

#### Scenario: Admin deletes user account
- **GIVEN** an admin user is authenticated
- **WHEN** they send `DELETE /api/v1/admin/users/{user_id}`
- **THEN** the system deletes the user account
- **AND** cascades deletion to user_sessions, user_videos, user_images (via ON DELETE CASCADE)
- **AND** returns HTTP 204 No Content

#### Scenario: Admin cannot delete their own account
- **GIVEN** an admin user is authenticated
- **WHEN** they send `DELETE /api/v1/admin/users/{own_user_id}`
- **THEN** the system returns HTTP 400 Bad Request with message "Cannot delete your own account"

### Requirement: View System Statistics
The system SHALL provide an endpoint for administrators to view system-wide statistics.

#### Scenario: Admin views system statistics
- **GIVEN** an admin user is authenticated
- **WHEN** they request `GET /api/v1/admin/stats`
- **THEN** the system returns statistics including:
  - Total user count
  - Active user count
  - Total storage used across all users
  - Total storage quota across all users
  - Total video count
  - Total image count
  - Total session count (active)

### Requirement: Admin Dashboard UI
The system SHALL provide a web-based admin dashboard accessible at `/admin` for managing users.

#### Scenario: Admin accesses dashboard page
- **GIVEN** an admin user is logged in
- **WHEN** they navigate to `/admin`
- **THEN** the system serves the admin dashboard HTML page
- **AND** displays system statistics cards at the top
- **AND** displays a searchable, filterable user table with pagination

#### Scenario: Non-admin user attempts to access dashboard
- **GIVEN** a non-admin user is logged in
- **WHEN** they navigate to `/admin`
- **THEN** the system redirects to `/` with error message "Admin access required"

#### Scenario: Admin searches and filters users in UI
- **GIVEN** an admin is viewing the dashboard
- **WHEN** they enter a search term or select a filter
- **THEN** the user table updates dynamically via API call
- **AND** shows matching results with pagination controls

#### Scenario: Admin edits user from dashboard
- **GIVEN** an admin is viewing the user table
- **WHEN** they click "Edit" on a user row
- **THEN** a modal opens showing editable user fields
- **WHEN** they submit changes
- **THEN** the system calls `PATCH /api/v1/admin/users/{user_id}`
- **AND** updates the table row on success

#### Scenario: Admin deletes user from dashboard
- **GIVEN** an admin is viewing the user table
- **WHEN** they click "Delete" on a user row
- **THEN** a confirmation dialog appears
- **WHEN** they confirm deletion
- **THEN** the system calls `DELETE /api/v1/admin/users/{user_id}`
- **AND** removes the row from the table on success
