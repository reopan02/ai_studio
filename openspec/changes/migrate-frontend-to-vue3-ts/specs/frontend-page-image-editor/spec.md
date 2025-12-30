## ADDED Requirements

### Requirement: Image Editor Page as Vue Entry
The system SHALL implement the image editor page (`/image`) using Vue 3 + TypeScript.

#### Scenario: Load the image editor UI
- **WHEN** an authenticated user visits `/image`
- **THEN** the page renders the image editor UI and loads required assets successfully

### Requirement: Preserve Upstream Image Generation Configuration
The image editor SHALL preserve the ability to generate/edit images via a user-configured upstream API using an API key and base URL stored in localStorage.

#### Scenario: Persist API settings
- **WHEN** a user sets an API key and base URL in the UI
- **THEN** the settings are persisted in localStorage
- **AND** reloading the page restores the saved settings

### Requirement: Persist and Manage Image History
The image editor SHALL continue to persist generated images to the backend repository and provide history CRUD operations.

#### Scenario: Save a completed image
- **WHEN** an image generation/edit completes successfully
- **THEN** the client persists the record via backend endpoints under `/api/v1/images`

#### Scenario: Delete a saved image
- **WHEN** a user deletes a saved image from history
- **THEN** the client calls `DELETE /api/v1/images/{id}` with required credentials/CSRF headers
- **AND** the deleted item is removed from the UI

