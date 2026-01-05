# Change: Admin management of user target descriptions

## Why
Admins need to review and maintain users' saved target descriptions for support and compliance.

## What Changes
- Add admin API endpoints to list, update, and delete user target descriptions with user and target type context.
- Add an admin-only management modal in the ecommerce image generator for viewing, editing, and deleting descriptions.
- Provide pagination for admin listings.

## Impact
- Affected specs: target-template-config
- Affected code: app/api/v1/admin.py, app/models/schemas.py, frontend/src/pages/ecommerce-image/ecommerce-image-page.vue, frontend/src/styles/ecommerce-image.css
