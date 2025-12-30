## ADDED Requirements

### Requirement: Storage Page as Vue Entry
The system SHALL implement the storage page (`/storage`) using Vue 3 + TypeScript.

#### Scenario: Display stored videos and images
- **WHEN** an authenticated user visits `/storage`
- **THEN** the page loads videos from `GET /api/v1/videos`
- **AND** the page loads images from `GET /api/v1/images`
- **AND** results are rendered with download and delete actions

#### Scenario: Redirect to login when unauthorized
- **WHEN** storage API calls return 401
- **THEN** the user is redirected to `/login?next=/storage`

### Requirement: Delete Stored Items
The storage page SHALL allow deleting stored videos and images.

#### Scenario: Delete a stored image
- **WHEN** a user deletes an image
- **THEN** the client calls `DELETE /api/v1/images/{id}` with required credentials/CSRF headers
- **AND** the item disappears from the rendered list

