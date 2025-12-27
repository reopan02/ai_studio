# Change: Add Admin Dashboard for User Management

## Why
Currently, the system only has a single admin endpoint (`PATCH /admin/users/{user_id}/quota`) for updating user storage quotas. Administrators have no way to:
- View and manage all users in the system
- Monitor user activity and storage usage
- Enable/disable user accounts
- View login history and session management
- Access system-wide statistics

This limits operational oversight and makes it difficult to manage users at scale.

## What Changes
- **NEW**: Admin dashboard UI at `/admin` with user management interface
- **NEW**: Backend API endpoints for listing, viewing, updating, and deleting users
- **NEW**: User activity and statistics views
- **ENHANCED**: Existing admin quota endpoint remains unchanged

**Breaking Changes**: None (purely additive)

## Impact
- **Affected specs**: `specs/admin-user-management/spec.md` (new capability)
- **Affected code**:
  - `app/api/v1/admin.py` - Add new endpoints
  - `app/static/admin.html` - New admin dashboard UI
  - `app/static/admin.js` - Dashboard JavaScript logic
  - `app/main.py` - Add route for `/admin` page
- **Affected users**: Only admin users will have access to these features
- **Database changes**: None (uses existing `users`, `user_sessions`, `user_login_logs` tables)
