# Implementation Tasks

## 1. Backend API Endpoints
- [ ] 1.1 Add `GET /api/v1/admin/users` - List all users with pagination, search, and filters
- [ ] 1.2 Add `GET /api/v1/admin/users/{user_id}` - Get detailed user info including activity stats
- [ ] 1.3 Add `PATCH /api/v1/admin/users/{user_id}` - Update user fields (is_active, is_admin, email)
- [ ] 1.4 Add `DELETE /api/v1/admin/users/{user_id}` - Delete user and cascade data
- [ ] 1.5 Add `GET /api/v1/admin/stats` - Get system-wide statistics

## 2. Frontend Admin Dashboard
- [ ] 2.1 Create `app/static/admin.html` - Admin dashboard page structure
- [ ] 2.2 Create `app/static/admin.js` - Dashboard logic and API integration
- [ ] 2.3 Add user list table with search, filter, and pagination
- [ ] 2.4 Add user detail modal showing activity, storage, sessions
- [ ] 2.5 Add user edit functionality (enable/disable, update quota, change role)
- [ ] 2.6 Add user deletion with confirmation
- [ ] 2.7 Add system statistics dashboard cards

## 3. Route and Integration
- [ ] 3.1 Add `GET /admin` route in `app/main.py` to serve admin dashboard
- [ ] 3.2 Update navigation in existing pages to include admin link (for admin users only)
- [ ] 3.3 Add admin check middleware or dependency to protect admin routes

## 4. Testing and Validation
- [ ] 4.1 Test all admin API endpoints with admin user
- [ ] 4.2 Test authorization (non-admin users should get 403)
- [ ] 4.3 Test user deletion cascades correctly
- [ ] 4.4 Test frontend pagination and search functionality
- [ ] 4.5 Validate OpenSpec with `openspec validate add-admin-dashboard --strict`
